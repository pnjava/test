"""Phase 3 acceptance:
  1. "Data General" -> DG chunks in top-3 (alias expansion, R5-alias)
  2. "core claims database" -> DG chunks via semantics
  3. decision-keyword query -> register chunk(s) included
  4. sibling expansion: >=2 chunks of a doc in results -> whole doc included
  5. base results <= TOP_K (siblings may extend past it), deduped

Run: .venv/bin/python -m pytest tests/test_retrieve.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src import config  # noqa: E402
from src.retrieve import retrieve, expand_query, _corpus  # noqa: E402

DG_DOCS = {"06-dg-current-state-landscape", "00-stitched-architecture-overview"}


def _doc(r) -> str:
    return r["metadata"]["doc_id"]


def test_alias_expansion_data_general():
    expanded = expand_query("Data General")
    assert "DG" in expanded.split(), f"expansion failed: {expanded!r}"


def test_data_general_returns_dg_chunks_top3():
    res = retrieve("Data General")
    top3_docs = {_doc(r) for r in res[:3]}
    assert top3_docs & DG_DOCS, f"no DG chunks in top-3: {[r['chunk_id'] for r in res[:3]]}"


def test_semantic_core_claims_database():
    res = retrieve("core claims database")
    hit = [r["chunk_id"] for r in res if _doc(r) in DG_DOCS or "DG" in r["text"]]
    assert hit, f"no DG chunks retrieved: {[r['chunk_id'] for r in res]}"


def test_decision_keyword_includes_register():
    res = retrieve("Which CDC approach should we use with Kafka?")
    register = [r["chunk_id"] for r in res if r["metadata"]["state"] == "register"]
    assert register, f"no register chunks included: {[r['chunk_id'] for r in res]}"
    assert "register-cdc-pattern" in register


def test_sibling_expansion_completes_docs():
    """Any doc with >=2 chunks in the results must appear with ALL its chunks."""
    res = retrieve("systems DG interacts with integration landscape")
    got_by_doc: dict[str, set] = {}
    for r in res:
        got_by_doc.setdefault(_doc(r), set()).add(r["chunk_id"])

    ids_all, _docs, metas_all, _ = _corpus()
    total_by_doc: dict[str, set] = {}
    for cid, meta in zip(ids_all, metas_all):
        total_by_doc.setdefault(meta["doc_id"], set()).add(cid)

    multi = {d: got for d, got in got_by_doc.items() if len(got) >= 2}
    assert multi, "test query produced no multi-chunk docs — pick a broader query"
    for doc_id, got in multi.items():
        assert got == total_by_doc[doc_id], \
            f"{doc_id}: incomplete after sibling expansion: {got} != {total_by_doc[doc_id]}"
    siblings = [r["chunk_id"] for r in res if r.get("sibling")]
    print(f"  multi-chunk docs completed: {sorted(multi)}; siblings added: {siblings}")


def test_topk_base_and_dedupe():
    res = retrieve("eligibility enrollment claims")
    ids = [r["chunk_id"] for r in res]
    assert len(ids) == len(set(ids)), "duplicates in results"
    base = [r for r in res if not r.get("sibling")]
    assert len(base) <= config.TOP_K, f"base results exceed TOP_K: {len(base)}"
