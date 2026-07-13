#!/usr/bin/env python3
"""
Hybrid Retriever (T3.3)

Query -> semantic search (ChromaDB) + exact keyword matching (chunks.jsonl),
merged with reciprocal-rank fusion, deduped, top-K (default 8) with metadata.

Keyword side:
  - exact word-boundary matches for query terms (case-sensitive for short
    ALL-CAPS acronyms like "DG", case-insensitive otherwise)
  - query terms are expanded via CONFIRMED alias-registry entries, and hits on
    a chunk's resolved `systems` tag score extra

Usage:
    .venv/bin/python src/retriever.py "your query"
    .venv/bin/python src/retriever.py --k 5 "DG"

Library use (T4):
    from retriever import retrieve
    results = retrieve("core claims database", k=8)
"""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
CHUNKS = ROOT / "knowledge" / "chunks.jsonl"
ALIASES = ROOT / "knowledge" / "aliases.yaml"

RRF_K = 60          # reciprocal-rank fusion constant
SEMANTIC_POOL = 16  # candidates pulled from each side before fusion
KEYWORD_POOL = 16


def load_chunks():
    with open(CHUNKS) as f:
        return [json.loads(line) for line in f if line.strip()]


def load_alias_map():
    """name(lower) -> canonical, confirmed entries only (incl. canonical itself)."""
    reg = yaml.safe_load(open(ALIASES))
    amap = {}
    for s in reg.get("systems", []):
        if s["status"] != "confirmed":
            continue
        amap[s["canonical_name"].lower()] = s["canonical_name"]
        for a in s.get("aliases", []):
            amap[a.lower()] = s["canonical_name"]
    return amap


def query_terms(query, alias_map):
    """Extract match terms from the query: words/phrases plus any registry
    names present (resolved to canonical + all confirmed variants)."""
    terms = set(re.findall(r"[A-Za-z0-9][A-Za-z0-9/&.-]*", query))
    # multi-word registry names present in the query (e.g. "Sterling Gateway")
    canonicals = set()
    ql = query.lower()
    for name, canonical in alias_map.items():
        if re.search(rf"(?<![a-z0-9]){re.escape(name)}(?![a-z0-9])", ql):
            canonicals.add(canonical)
    # expand: every confirmed variant of every matched canonical becomes a term
    reg = yaml.safe_load(open(ALIASES))
    for s in reg.get("systems", []):
        if s["canonical_name"] in canonicals:
            terms.add(s["canonical_name"])
            terms.update(s.get("aliases", []))
    stop = {"the", "a", "an", "of", "for", "and", "or", "in", "on", "to", "is",
            "what", "which", "who", "how", "does", "do", "are", "was", "were"}
    return {t for t in terms if t.lower() not in stop and len(t) >= 2}, canonicals


def term_regex(term):
    """Short ALL-CAPS terms match case-sensitively (DG != dg);
    everything else case-insensitive."""
    esc = re.escape(term)
    if term.isupper() and len(term) <= 6:
        return re.compile(rf"(?<![A-Za-z0-9]){esc}(?![A-Za-z0-9])")
    return re.compile(rf"(?<![A-Za-z0-9]){esc}(?![A-Za-z0-9])", re.IGNORECASE)


def keyword_rank(chunks, terms, canonicals):
    """Rank chunks by exact-match score; returns [(chunk_id, score), ...] desc."""
    scored = []
    regexes = [(t, term_regex(t)) for t in terms]
    for c in chunks:
        score = 0.0
        matched_terms = 0
        for t, rx in regexes:
            hits = len(rx.findall(c["text"]))
            if hits:
                matched_terms += 1
                score += min(hits, 5)  # cap per-term so one spammy term can't dominate
        # bonus: chunk's resolved systems tag matches a canonical from the query
        sys_bonus = sum(3 for cn in canonicals if cn in c.get("systems", []))
        score += sys_bonus
        if matched_terms:
            score *= matched_terms  # reward covering more distinct terms
        if score > 0:
            scored.append((c["chunk_id"], score))
    scored.sort(key=lambda x: -x[1])
    return scored[:KEYWORD_POOL]


def semantic_rank(query, k=SEMANTIC_POOL):
    """Rank via Chroma; returns [(chunk_id, distance), ...] asc distance."""
    from embed_store import get_client, COLLECTION
    coll = get_client().get_collection(COLLECTION)
    res = coll.query(query_texts=[query], n_results=k)
    return list(zip(res["ids"][0], res["distances"][0]))


def retrieve(query, k=8):
    """Hybrid retrieval: RRF-fuse semantic + keyword rankings, dedupe, top-k."""
    chunks = load_chunks()
    by_id = {c["chunk_id"]: c for c in chunks}
    alias_map = load_alias_map()
    terms, canonicals = query_terms(query, alias_map)

    kw = keyword_rank(chunks, terms, canonicals)
    sem = semantic_rank(query)

    fused = {}
    for rank, (cid, _score) in enumerate(kw, 1):
        fused[cid] = fused.get(cid, 0.0) + 1.0 / (RRF_K + rank)
    for rank, (cid, _dist) in enumerate(sem, 1):
        fused[cid] = fused.get(cid, 0.0) + 1.0 / (RRF_K + rank)

    kw_ranks = {cid: r for r, (cid, _) in enumerate(kw, 1)}
    sem_ranks = {cid: r for r, (cid, _) in enumerate(sem, 1)}

    top = sorted(fused.items(), key=lambda x: -x[1])[:k]
    results = []
    for cid, score in top:
        c = by_id[cid]
        results.append(
            {
                "chunk_id": cid,
                "score": round(score, 5),
                "keyword_rank": kw_ranks.get(cid),
                "semantic_rank": sem_ranks.get(cid),
                "text": c["text"],
                "source_pointer": c["source_pointer"],
                "metadata": c["metadata"],
                "systems": c.get("systems", []),
            }
        )
    return results


def main():
    args = sys.argv[1:]
    k = 8
    if "--k" in args:
        i = args.index("--k")
        k = int(args[i + 1])
        del args[i : i + 2]
    if not args:
        print(__doc__)
        sys.exit(2)
    query = " ".join(args)

    results = retrieve(query, k=k)
    print(f"Query: {query!r} — top {len(results)}\n")
    for r in results:
        ranks = f"kw#{r['keyword_rank'] or '-'} sem#{r['semantic_rank'] or '-'}"
        first_line = r["text"].splitlines()[0][:90]
        print(f"{r['score']:.4f}  [{ranks:>12}]  {r['chunk_id']}")
        print(f"        {first_line}")
        print(f"        systems={','.join(r['systems']) or '-'}  confidence={r['metadata']['confidence']}\n")


if __name__ == "__main__":
    main()
