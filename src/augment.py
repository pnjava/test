"""Synthetic query augmentation (Phase 4).

For every chunk in the main collection, generate 8 diverse questions
(locked GEN_QUESTIONS prompt) and store them in a SEPARATE Chroma
collection ("meritain_synth") as {type: synthetic_query, parent_chunk_id}.
Retrieval (src/retrieve.py) searches both collections and substitutes the
parent chunk whenever a synthetic question is the vector hit.

CLI:
    python -m src.augment                # generate for all chunks (idempotent per chunk)
    python -m src.augment --golden-rate  # retrieval-level golden hit-rate report
"""

import json
import sys
import urllib.request

import chromadb
import yaml

from src import config
from src.ingest import get_collection, embedder
from src.prompts import GEN_QUESTIONS

SYNTH_COLLECTION = "meritain_synth"


def synth_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    return client.get_or_create_collection(SYNTH_COLLECTION, metadata={"hnsw:space": "cosine"})


def _gen_questions(text: str) -> list[str]:
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [{"role": "user", "content": GEN_QUESTIONS.format(text=text)}],
        "stream": False,
        "options": {"temperature": 0.3},  # slight diversity for question variants
    }
    req = urllib.request.Request(
        f"{config.OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        out = json.loads(resp.read())["message"]["content"]
    lines = [ln.strip().lstrip("0123456789.-) ").strip() for ln in out.splitlines()]
    return [ln for ln in lines if ln and len(ln) > 8][:8]


def augment() -> None:
    main = get_collection()
    synth = synth_collection()
    got = main.get(include=["documents", "metadatas"])
    done_parents = set()
    existing = synth.get(include=["metadatas"])
    for m in existing["metadatas"]:
        done_parents.add(m["parent_chunk_id"])

    todo = [(cid, doc) for cid, doc in zip(got["ids"], got["documents"])
            if cid not in done_parents]
    print(f"{len(got['ids'])} chunks total; {len(done_parents)} already augmented; {len(todo)} to do")

    for n, (cid, doc) in enumerate(todo, 1):
        try:
            questions = _gen_questions(doc)
        except Exception as e:
            print(f"  ! {cid}: generation failed ({e}) — skipped")
            continue
        if not questions:
            print(f"  ! {cid}: no questions parsed — skipped")
            continue
        ids = [f"synth::{cid}::q{i}" for i in range(1, len(questions) + 1)]
        embeddings = embedder().encode(questions, show_progress_bar=False).tolist()
        synth.upsert(
            ids=ids,
            documents=questions,
            metadatas=[{"type": "synthetic_query", "parent_chunk_id": cid}] * len(questions),
            embeddings=embeddings,
        )
        print(f"  [{n}/{len(todo)}] {cid}: {len(questions)} questions")

    print(f"\n✓ synthetic collection count: {synth.count()}")


def golden_retrieval_rate() -> tuple[int, int, list[str]]:
    """Retrieval-level golden check: expected docs present in retrieve() results.
    (Answer-level golden runs in Phase 6; this isolates what augmentation moves.)"""
    from src.retrieve import retrieve
    from src.query_fix import fix_query

    qs = yaml.safe_load(config.GOLDEN_SET.read_text())["questions"]
    hits, total, failures = 0, 0, []
    for q in qs:
        expected = set(q.get("expected_retrieve_docs_any", []) or q.get("expected_cite_docs_any", []))
        if not expected:
            continue  # unknown-type questions have no retrieval expectation
        total += 1
        query = q["question"]
        if q["type"] == "robustness":
            query = fix_query(query)["corrected"]
        got_docs = {r["metadata"]["doc_id"] for r in retrieve(query)}
        if got_docs & expected:
            hits += 1
        else:
            failures.append(f"{q['id']}: expected {sorted(expected)}, got {sorted(got_docs)}")
    return hits, total, failures


def main() -> None:
    if "--golden-rate" in sys.argv:
        hits, total, failures = golden_retrieval_rate()
        print(f"golden retrieval hit-rate: {hits}/{total}")
        for f in failures:
            print(f"  MISS {f}")
        return
    augment()


if __name__ == "__main__":
    main()
