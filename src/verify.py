"""Post-answer verification (Phase 6).

V1 Citation integrity — enforced in src/answer.py (strip fabricated citations,
   one repair call, reject-to-refusal as last resort). Helpers live there;
   this module re-exports the contract pieces used by tests.
V2 Evidence-based confidence — HIGH / MEDIUM / LOW computed from retrieval
   evidence (never model self-report):
     HIGH   >= 2 distinct docs among the citations
     MEDIUM exactly 1 doc, > 1 chunk or non-stale
     LOW    single chunk, or ANY cited doc has stale_risk
V3 Staleness — any citation to a stale_risk doc appends a currency warning.
"""

from functools import lru_cache

import chromadb

from src import config

STALE_NOTE = "⏳ based on a 2014-era document — verify currency"


@lru_cache(maxsize=1)
def stale_doc_ids() -> frozenset:
    coll = chromadb.PersistentClient(path=str(config.CHROMA_DIR)).get_collection(config.COLLECTION_NAME)
    got = coll.get(include=["metadatas"])
    return frozenset(m["doc_id"] for m in got["metadatas"] if m.get("stale_risk"))


def _cited_docs(citations: list[str]) -> set[str]:
    return {c.split("#")[0] for c in citations}


def confidence(citations: list[str]) -> str:
    """V2: evidence-based confidence from the citation set."""
    if not citations:
        return "LOW"
    docs = _cited_docs(citations)
    if docs & stale_doc_ids():
        return "LOW"
    if len(docs) >= 2:
        return "HIGH"
    return "MEDIUM" if len(citations) > 1 else "LOW"


def staleness_note(citations: list[str]) -> str | None:
    """V3: currency warning when any cited doc is stale_risk."""
    return STALE_NOTE if _cited_docs(citations) & stale_doc_ids() else None
