"""Hybrid retrieval (M2): alias expansion -> vector + BM25 -> RRF -> top-8,
with register chunks force-included on decision-topic queries.

Pipeline (R4 encoded here):
  (a) expand query with kb/knowledge/aliases.yaml (query "Data General"
      retrieves DG chunks)
  (b) vector search (Chroma, all-MiniLM-L6-v2, top 12)
  (c) BM25 over all chunk texts (top 12)
  (d) reciprocal-rank-fusion merge -> TOP_K=8
  (e) if the query hits DECISION_KEYWORDS, matching register chunks are
      force-included (R3 support)

CLI:
    python -m src.retrieve "your question"     # ranked chunk ids + scores
"""

import re
import sys
from functools import lru_cache

import yaml
from rank_bm25 import BM25Okapi

from src import config
from src.ingest import get_collection, embedder


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


@lru_cache(maxsize=1)
def _corpus() -> tuple[list[str], list[str], list[dict], BM25Okapi]:
    """(ids, documents, metadatas, bm25) over the whole collection."""
    got = get_collection().get(include=["documents", "metadatas"])
    ids, docs, metas = got["ids"], got["documents"], got["metadatas"]
    bm25 = BM25Okapi([_tokenize(d) for d in docs])
    return ids, docs, metas, bm25


@lru_cache(maxsize=1)
def _aliases() -> list[dict]:
    return yaml.safe_load(config.ALIASES_FILE.read_text())["aliases"]


def expand_query(query: str) -> str:
    """Append canonical + sibling names for any alias present in the query (R4)."""
    ql = query.lower()
    extra: list[str] = []
    for entry in _aliases():
        names = [entry["canonical"]] + [str(a) for a in entry.get("aka", [])]
        if any(re.search(rf"(?<![a-z0-9]){re.escape(n.lower())}(?![a-z0-9])", ql) for n in names):
            extra.extend(n for n in names if n.lower() not in ql)
    return query + (" " + " ".join(dict.fromkeys(extra)) if extra else "")


def _vector_rank(expanded: str) -> list[str]:
    """Vector search over real chunks AND synthetic questions (Phase 4).
    Synthetic hits substitute their parent chunk; merged by best distance."""
    emb = embedder().encode([expanded]).tolist()
    res = get_collection().query(query_embeddings=emb, n_results=config.VECTOR_POOL)
    best: dict[str, float] = {}
    for cid, dist in zip(res["ids"][0], res["distances"][0]):
        best[cid] = min(best.get(cid, 2.0), dist)

    try:
        from src.augment import synth_collection
        synth = synth_collection()
        if synth.count():
            sres = synth.query(query_embeddings=emb, n_results=config.VECTOR_POOL,
                               include=["metadatas", "distances"])
            for meta, dist in zip(sres["metadatas"][0], sres["distances"][0]):
                parent = meta["parent_chunk_id"]
                best[parent] = min(best.get(parent, 2.0), dist)
    except Exception:
        pass  # synth collection absent/unreadable -> plain vector search

    ranked = sorted(best.items(), key=lambda x: x[1])
    return [cid for cid, _ in ranked[: config.VECTOR_POOL]]


def _bm25_rank(expanded: str) -> list[str]:
    ids, _docs, _metas, bm25 = _corpus()
    scores = bm25.get_scores(_tokenize(expanded))
    ranked = sorted(zip(ids, scores), key=lambda x: -x[1])
    return [cid for cid, s in ranked[: config.BM25_POOL] if s > 0]


def _register_hits(query: str) -> list[str]:
    """Register chunk ids whose text matches a decision keyword in the query."""
    ql = _tokenize(query)
    hit_kw = [kw for kw in config.DECISION_KEYWORDS if kw in ql]
    if not hit_kw:
        return []
    ids, docs, metas, _ = _corpus()
    out = []
    for cid, doc, meta in zip(ids, docs, metas):
        if meta.get("state") == "register" and any(kw in doc.lower() for kw in hit_kw):
            out.append(cid)
    return out


def _watchlist_hits(query: str) -> list[str]:
    """R5: best BM25-scoring chunk per watchlist acronym present in the query."""
    q_tokens = set(_tokenize(query))
    wanted = [a for a in config.WATCHLIST_ACRONYMS if a.lower() in q_tokens]
    if not wanted:
        return []
    ids, docs, _metas, bm25 = _corpus()
    out = []
    for acro in wanted:
        token = acro.lower()
        scores = bm25.get_scores([token])
        best = max(
            ((cid, s) for cid, doc, s in zip(ids, docs, scores) if token in _tokenize(doc)),
            key=lambda x: x[1],
            default=None,
        )
        if best:
            out.append(best[0])
    return out


def retrieve(query: str, k: int = config.TOP_K) -> list[dict]:
    """Returns [{chunk_id, score, vector_rank, bm25_rank, forced, text, metadata}]."""
    expanded = expand_query(query)
    vec = _vector_rank(expanded)
    bm = _bm25_rank(expanded)

    fused: dict[str, float] = {}
    for rank, cid in enumerate(vec, 1):
        fused[cid] = fused.get(cid, 0.0) + 1.0 / (config.RRF_K + rank)
    for rank, cid in enumerate(bm, 1):
        fused[cid] = fused.get(cid, 0.0) + 1.0 / (config.RRF_K + rank)

    top = [cid for cid, _ in sorted(fused.items(), key=lambda x: -x[1])][:k]

    # (e) force-include register chunks (decision topics) and watchlist-acronym
    # chunks (R5), evicting the fused tail to keep top-k
    for forced_id in _register_hits(query) + _watchlist_hits(query):
        if forced_id not in top:
            if len(top) >= k:
                top.pop()
            top.append(forced_id)

    # (f) SIBLING EXPANSION: enumeration questions need whole documents —
    # if >=2 chunks of one doc made the cut, append that doc's remaining
    # chunks (appended beyond k; marked sibling in results)
    ids_all, docs_all, metas_all, _ = _corpus()
    doc_of = {cid: meta["doc_id"] for cid, meta in zip(ids_all, metas_all)}
    if any(cid not in doc_of for cid in top):
        # a chunk was ingested after this process built its corpus cache —
        # rebuild once (single-file SME ingests during a session)
        _corpus.cache_clear()
        ids_all, docs_all, metas_all, _ = _corpus()
        doc_of = {cid: meta["doc_id"] for cid, meta in zip(ids_all, metas_all)}
        top = [cid for cid in top if cid in doc_of]
    from collections import Counter
    doc_counts = Counter(doc_of[cid] for cid in top)
    siblings: list[str] = []
    for doc_id, n in doc_counts.items():
        if n >= 2:
            siblings.extend(cid for cid in ids_all
                            if doc_of[cid] == doc_id and cid not in top)
    top.extend(siblings)

    ids, docs, metas, _ = _corpus()
    by_id = {cid: (doc, meta) for cid, doc, meta in zip(ids, docs, metas)}
    vec_ranks = {cid: r for r, cid in enumerate(vec, 1)}
    bm_ranks = {cid: r for r, cid in enumerate(bm, 1)}

    results = []
    for cid in top:
        doc, meta = by_id[cid]
        results.append({
            "chunk_id": cid,
            "score": round(fused.get(cid, 0.0), 5),
            "vector_rank": vec_ranks.get(cid),
            "bm25_rank": bm_ranks.get(cid),
            "forced": cid not in fused and cid not in siblings,
            "sibling": cid in siblings,
            "text": doc,
            "metadata": meta,
        })
    return results


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    query = " ".join(sys.argv[1:])
    expanded = expand_query(query)
    if expanded != query:
        print(f"expanded: {expanded!r}\n")
    for r in retrieve(query):
        marks = (f"vec#{r['vector_rank'] or '-'} bm25#{r['bm25_rank'] or '-'}"
                 + (" FORCED" if r["forced"] else "")
                 + (" SIBLING" if r.get("sibling") else ""))
        print(f"{r['score']:.5f}  [{marks:>26}]  {r['chunk_id']}  (state={r['metadata']['state']})")


if __name__ == "__main__":
    main()
