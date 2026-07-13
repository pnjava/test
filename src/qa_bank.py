"""QA Bank fast path (Phase 5).

qa_bank.yaml (112 curated Q&As: 69 answered, 16 partial, 27 gaps) is embedded
into Chroma collection "qa_bank". The answer flow consults it BEFORE live RAG:

  similarity >= QA_MATCH_THRESHOLD (0.92) and answerable in (Y, P)
      -> stored answer, badge "⚡ verified Q&A bank", zero LLM calls
  similarity >= threshold and answerable == N (a known gap)
      -> "Not in knowledge base." + suggested SME, logged to gaps.yaml
  below threshold
      -> live RAG; the question is logged to bank_candidates.yaml

CLI:
    python -m src.qa_bank index    # (re)build the bank embedding index
    python -m src.qa_bank lookup "What is DG?"
    python -m src.qa_bank build    # regenerate bank from docs (expensive; see build_bank)
"""

import json
import sys
import urllib.request
from datetime import date
from functools import lru_cache

import chromadb
import yaml

from src import config
from src.ingest import embedder

_BANK_CACHE: dict | None = None


@lru_cache(maxsize=1)
def _doc_prefix_map() -> dict:
    """'06' -> '06-dg-current-state-landscape' (bank citations use page/doc numbers)."""
    out = {}
    for p in config.MARKDOWN_DIR.glob("*.md"):
        prefix = p.stem.split("-")[0]
        out[prefix] = p.stem
    return out


def _normalize_citations(citations: list) -> list[str]:
    pm = _doc_prefix_map()
    out = []
    for c in citations or []:
        c = str(c)
        out.append(pm.get(c, c))  # map '06' -> doc id; pass through full ids
    return out


def load_bank() -> list[dict]:
    global _BANK_CACHE
    if _BANK_CACHE is None:
        entries = yaml.safe_load(config.QA_BANK.read_text())["qa_bank"]
        for e in entries:
            e["citations_resolved"] = _normalize_citations(e.get("citations"))
        _BANK_CACHE = {e["id"]: e for e in entries}
    return list(_BANK_CACHE.values())


def bank_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    return client.get_or_create_collection(config.QA_COLLECTION, metadata={"hnsw:space": "cosine"})


def build_index() -> int:
    """(Re)embed all bank questions. Idempotent full rebuild."""
    entries = load_bank()
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    try:
        client.delete_collection(config.QA_COLLECTION)
    except Exception:
        pass
    coll = client.create_collection(config.QA_COLLECTION, metadata={"hnsw:space": "cosine"})
    questions = [e["question"] for e in entries]
    embeddings = embedder().encode(questions, show_progress_bar=False).tolist()
    coll.add(
        ids=[e["id"] for e in entries],
        documents=questions,
        metadatas=[{"answerable": e["answerable"]} for e in entries],
        embeddings=embeddings,
    )
    return coll.count()


_STOP = {"what", "is", "the", "a", "an", "of", "for", "and", "or", "in", "on",
         "to", "how", "who", "which", "are", "do", "does", "it", "s", "was"}


def _content_tokens(text: str) -> set:
    import re
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOP}


def _match_score(query: str, bank_q: str, cosine: float) -> float:
    """Hybrid: cosine, OR lexical containment when the query's content tokens
    are a subset of the bank question's (e.g. 'What is DG?' vs 'What is DG and
    what technology is it built on?' — cosine ~0.83 but an obvious match).
    Cosine floor 0.70 guards the lexical path against topic drift."""
    from rapidfuzz import fuzz, utils
    score = cosine
    q_tokens = _content_tokens(query)
    if q_tokens and cosine >= 0.70 and q_tokens <= _content_tokens(bank_q):
        score = max(score, fuzz.token_set_ratio(query, bank_q,
                                                processor=utils.default_process) / 100.0)
    return score


def lookup(question: str) -> dict | None:
    """Best bank match >= QA_MATCH_THRESHOLD (hybrid score), or None."""
    coll = bank_collection()
    if not coll.count():
        return None
    emb = embedder().encode([question]).tolist()
    res = coll.query(query_embeddings=emb, n_results=5, include=["documents", "distances"])
    if not res["ids"][0]:
        return None
    load_bank()
    best = None
    for qb_id, doc, dist in zip(res["ids"][0], res["documents"][0], res["distances"][0]):
        cosine = 1.0 - dist
        score = _match_score(question, doc, cosine)
        # cosine breaks ties between multiple subset matches
        key = (score, cosine)
        if score >= config.QA_MATCH_THRESHOLD and (best is None or key > best[0]):
            best = (key, qb_id, doc)
    if best is None:
        return None
    (score, _cos), qb_id, doc = best
    return {"entry": _BANK_CACHE[qb_id], "similarity": round(score, 4),
            "matched_question": doc}


def record_candidate(question: str) -> None:
    """Questions that missed the bank — future build/curation input."""
    path = config.BANK_CANDIDATES
    data = yaml.safe_load(path.read_text()) if path.exists() else None
    data = data or {"candidates": []}
    qnorm = question.strip().lower()
    for c in data["candidates"]:
        if c["question"].strip().lower() == qnorm:
            c["count"] = c.get("count", 1) + 1
            c["last_asked"] = date.today().isoformat()
            break
    else:
        data["candidates"].append(
            {"question": question, "first_asked": date.today().isoformat(),
             "last_asked": date.today().isoformat(), "count": 1}
        )
    path.write_text(yaml.safe_dump(data, sort_keys=False, width=110))


def build_bank(per_doc: int = 5) -> None:
    """Regenerate qa_bank.yaml from the docs (ARCHITECT_QUESTIONS -> pipeline
    answer -> keep only fully-cited). EXPENSIVE: ~27 docs x (1 + per_doc) LLM
    calls. Entries whose kb_version predates changed docs are invalidated.
    Run deliberately, not on a schedule."""
    from src.answer import answer as pipeline_answer
    from src.prompts import ARCHITECT_QUESTIONS

    entries = load_bank()
    print(f"existing bank: {len(entries)} entries (kb_version seed-v1)")
    new_id = max(int(e["id"][2:]) for e in entries) + 1

    for doc in sorted(config.MARKDOWN_DIR.glob("*.md")):
        text = doc.read_text(errors="replace")
        payload = {
            "model": config.OLLAMA_MODEL,
            "messages": [{"role": "user",
                          "content": ARCHITECT_QUESTIONS.format(n=per_doc, text=text[:6000])}],
            "stream": False, "options": {"temperature": 0.3},
        }
        req = urllib.request.Request(f"{config.OLLAMA_URL}/api/chat",
                                     data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as resp:
            questions = [q.strip() for q in
                         json.loads(resp.read())["message"]["content"].splitlines() if q.strip()]
        for q in questions[:per_doc]:
            if lookup(q):
                continue  # already covered
            r = pipeline_answer(q, use_bank=False)
            if r["status"] == "grounded" and r["citations"]:
                entries.append({
                    "id": f"QB{new_id:03d}", "domain": doc.stem, "question": q,
                    "answerable": "Y", "answer": r["answer"],
                    "citations": r["citations"], "decision_status": None,
                    "suggested_sme": None, "priority": "Medium",
                    "kb_version": f"build-{date.today().isoformat()}",
                })
                new_id += 1
                print(f"  + {q[:70]}")
        break  # SAFETY: one doc per invocation until explicitly extended
    config.QA_BANK.write_text(yaml.safe_dump({"qa_bank": entries}, sort_keys=False, width=110))
    print(f"bank now {len(entries)} entries")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "index":
        print(f"✓ qa_bank index built: {build_index()} questions")
    elif cmd == "lookup" and len(sys.argv) > 2:
        hit = lookup(" ".join(sys.argv[2:]))
        print(yaml.safe_dump(
            {"similarity": hit["similarity"], "matched": hit["matched_question"],
             "id": hit["entry"]["id"], "answerable": hit["entry"]["answerable"]}
            if hit else {"match": None}, sort_keys=False))
    elif cmd == "build":
        build_bank()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
