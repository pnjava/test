"""Ingestion (M1): kb/knowledge/markdown/*.md + contradiction-register.yaml
-> 150-400-word chunks -> all-MiniLM-L6-v2 embeddings -> persistent ChromaDB.

Rules honored:
  - chunk_id = <doc_id>#<nn>; register chunks = register-<decision_id>
  - metadata per chunk: doc_id, title, source, state, confidence, tags
  - aliases.yaml is NOT ingested (query-time only, R4)
  - idempotent: re-running replaces a doc's chunks, never duplicates
  - split on headings first, then paragraphs, then sentence boundaries —
    never mid-sentence; zero chunks over 400 words

CLI:
    python -m src.ingest                 # full ingest, per-doc counts + total
    python -m src.ingest --file <path>   # single new doc (M5 loop), no full re-index
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import chromadb
import yaml
from sentence_transformers import SentenceTransformer

from src import config


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stale_risk(source: str) -> bool:
    """True when the doc source mentions a year <= STALE_YEAR_MAX
    (e.g. the 2014 DRAFTS flow doc) — V3 staleness warnings key off this."""
    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", source)]
    return bool(years) and min(years) <= config.STALE_YEAR_MAX

_model = None


def embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
    return _model


def word_count(text: str) -> int:
    return len(text.split())


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body). Empty dict when absent."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return yaml.safe_load(parts[1]) or {}, parts[2]
    return {}, text


def split_sections(body: str) -> list[tuple[str, str]]:
    """Split at markdown headings; returns [(heading_path, text), ...]."""
    sections: list[tuple[str, str]] = []
    path: list[tuple[int, str]] = []
    buf: list[str] = []

    def flush() -> None:
        text = "\n".join(buf).strip()
        if text:
            sections.append((" > ".join(t for _, t in path), text))
        buf.clear()

    for line in body.splitlines():
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            flush()
            level, title = len(m.group(1)), m.group(2).strip()
            while path and path[-1][0] >= level:
                path.pop()
            path.append((level, title))
        else:
            buf.append(line)
    flush()
    return sections


def split_oversize(text: str, limit: int) -> list[str]:
    """Split into <=limit-word pieces at paragraph, then sentence boundaries."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if current:
            pieces.append("\n\n".join(current))
            current.clear()

    for p in paras:
        if word_count(p) > limit:
            flush()
            sentences = re.split(r"(?<=[.!?])\s+", p)
            acc: list[str] = []
            for s in sentences:
                if word_count(" ".join(acc + [s])) > limit and acc:
                    pieces.append(" ".join(acc))
                    acc = [s]
                else:
                    acc.append(s)
            if acc:
                pieces.append(" ".join(acc))
        elif word_count("\n\n".join(current + [p])) > limit:
            flush()
            current.append(p)
        else:
            current.append(p)
    flush()
    return pieces


def chunk_doc(path: Path) -> list[dict]:
    """One markdown doc -> chunk dicts {id, text, metadata}."""
    fm, body = parse_frontmatter(path.read_text(errors="replace"))
    doc_id = fm.get("id", path.stem)
    title_m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else doc_id

    packed: list[tuple[str, str]] = []
    for heading, text in split_sections(body):
        if word_count(text) > config.CHUNK_MAX_WORDS:
            for i, piece in enumerate(split_oversize(text, config.CHUNK_MAX_WORDS), 1):
                packed.append((f"{heading} (part {i})", piece))
        elif (packed
              and word_count(packed[-1][1]) < config.CHUNK_MIN_WORDS
              and word_count(packed[-1][1]) + word_count(text) <= config.CHUNK_MAX_WORDS):
            prev_h, prev_t = packed[-1]
            packed[-1] = (prev_h, f"{prev_t}\n\n[{heading}]\n{text}" if heading else f"{prev_t}\n\n{text}")
        else:
            packed.append((heading, text))

    chunks = []
    for i, (heading, text) in enumerate(packed, 1):
        header = f"[{doc_id}] {title}" + (f" — {heading}" if heading else "")
        chunk_text = f"{header}\n{text}"
        if word_count(chunk_text) > config.CHUNK_MAX_WORDS:
            chunk_text = " ".join(chunk_text.split()[: config.CHUNK_MAX_WORDS])
        chunks.append({
            "id": f"{doc_id}#{i:02d}",
            "text": chunk_text,
            "metadata": {
                "doc_id": doc_id,
                "title": title,
                "source": str(fm.get("source", path.name)),
                "state": str(fm.get("state", "unknown")),
                "confidence": str(fm.get("confidence", "unknown")),
                "tags": ",".join(str(t) for t in fm.get("tags", [])) if isinstance(fm.get("tags"), list) else str(fm.get("tags", "")),
                "stale_risk": _stale_risk(str(fm.get("source", ""))),
                "ingested_at": _now(),
            },
        })
    return chunks


def register_chunks() -> list[dict]:
    """contradiction-register.yaml -> one chunk per decision, state='register'."""
    reg = yaml.safe_load(config.CONTRADICTION_REGISTER.read_text())
    chunks = []
    for d in reg["decisions"]:
        doc_id = f"{config.REGISTER_DOC_PREFIX}-{d['id'].lower()}"
        lines = [f"[DECISION REGISTER] {d['id']}: {d['topic']}", f"STATUS: {d['status']}"]
        for opt in d.get("options", []):
            lines.append(f"- option: {opt['name']} — status: {opt['status']}; evidence: {opt.get('evidence', '')}")
        for key in ("evidence", "notes", "reconciliation_hypothesis"):
            if d.get(key):
                lines.append(f"{key}: {d[key]}")
        chunks.append({
            "id": doc_id,
            "text": "\n".join(lines),
            "metadata": {
                "doc_id": doc_id,
                "title": f"Decision: {d['topic']}",
                "source": "contradiction-register.yaml",
                "state": "register",
                "confidence": "verified",
                "tags": "decision,register",
                "stale_risk": False,
                "ingested_at": _now(),
            },
        })
    return chunks


def watchlist_chunk() -> dict:
    """extraction-notes.md acronym-collision watchlist -> one retrievable chunk
    (R5: distinctness claims must be groundable, not just prompt rules)."""
    text = config.EXTRACTION_NOTES.read_text(errors="replace")
    m = re.search(r"^## Acronym collision watchlist.*?(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    section = m.group(0).strip() if m else text
    return {
        "id": "watchlist-acronyms",
        "text": "[ACRONYM WATCHLIST — these are DISTINCT systems, never merge]\n" + section,
        "metadata": {
            "doc_id": "watchlist-acronyms",
            "title": "Acronym collision watchlist",
            "source": "extraction-notes.md",
            "state": "register",
            "confidence": "verified",
            "tags": "watchlist,acronyms,register",
            "stale_risk": False,
            "ingested_at": _now(),
        },
    }


def get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    return client.get_or_create_collection(config.COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def upsert_doc(coll: chromadb.Collection, chunks: list[dict]) -> None:
    """Replace a doc's chunks: delete stale ids for the doc, then upsert."""
    if not chunks:
        return
    doc_id = chunks[0]["metadata"]["doc_id"]
    existing = coll.get(where={"doc_id": doc_id})
    stale = set(existing["ids"]) - {c["id"] for c in chunks}
    if stale:
        coll.delete(ids=sorted(stale))
    embeddings = embedder().encode([c["text"] for c in chunks], show_progress_bar=False).tolist()
    coll.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
        embeddings=embeddings,
    )


def verify(coll: chromadb.Collection) -> bool:
    """Acceptance: every chunk has source+state+confidence; none >400 words."""
    got = coll.get(include=["metadatas", "documents"])
    bad_meta = [i for i, m in zip(got["ids"], got["metadatas"])
                if not m.get("source") or not m.get("state") or not m.get("confidence")]
    oversize = [i for i, d in zip(got["ids"], got["documents"]) if word_count(d) > config.CHUNK_MAX_WORDS]
    if bad_meta:
        print(f"✗ {len(bad_meta)} chunks missing source/state/confidence: {bad_meta[:5]}")
    if oversize:
        print(f"✗ {len(oversize)} chunks over {config.CHUNK_MAX_WORDS} words: {oversize[:5]}")
    missing_new = [i for i, m in zip(got["ids"], got["metadatas"])
                   if "stale_risk" not in m or not m.get("ingested_at")]
    if missing_new:
        print(f"✗ {len(missing_new)} chunks missing stale_risk/ingested_at: {missing_new[:5]}")
    stale = [i for i, m in zip(got["ids"], got["metadatas"]) if m.get("stale_risk")]
    if not bad_meta and not oversize and not missing_new:
        print(f"✓ verify: all {len(got['ids'])} chunks carry source+state+confidence+stale_risk+ingested_at; "
              f"zero over {config.CHUNK_MAX_WORDS} words; stale_risk chunks: {stale or 'none'}")
    return not bad_meta and not oversize and not missing_new


def main() -> None:
    args = sys.argv[1:]
    coll = get_collection()

    if args[:1] == ["--file"]:
        path = Path(args[1])
        chunks = chunk_doc(path)
        upsert_doc(coll, chunks)
        print(f"✓ {path.name}: {len(chunks)} chunks upserted (collection now {coll.count()})")
        sys.exit(0 if verify(coll) else 1)

    total = 0
    for md in sorted(config.MARKDOWN_DIR.glob("*.md")):
        chunks = chunk_doc(md)
        upsert_doc(coll, chunks)
        total += len(chunks)
        print(f"  {md.stem}: {len(chunks)}")

    reg = register_chunks() + [watchlist_chunk()]
    upsert_doc_ids = {c["id"] for c in reg}
    existing = coll.get(where={"state": "register"})
    stale = set(existing["ids"]) - upsert_doc_ids
    if stale:
        coll.delete(ids=sorted(stale))
    embeddings = embedder().encode([c["text"] for c in reg], show_progress_bar=False).tolist()
    coll.upsert(ids=[c["id"] for c in reg], documents=[c["text"] for c in reg],
                metadatas=[c["metadata"] for c in reg], embeddings=embeddings)
    total += len(reg)
    print(f"  contradiction-register + watchlist: {len(reg)}")
    print(f"\nTotal chunks: {total}   (collection count: {coll.count()})")

    sys.exit(0 if verify(coll) else 1)


if __name__ == "__main__":
    main()
