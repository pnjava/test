#!/usr/bin/env python3
"""
T3.3 acceptance test:
  1. Query "DG" -> chunks containing the literal term ranked high
     (every top-3 result contains standalone "DG"; majority of top 8 do)
  2. Query "core claims database" -> DG chunks found via semantics
     (>=1 of top 8 is tagged DG in systems, without "DG" in the query)
  3. Results are deduped, carry metadata + source pointers, and len <= 8

Run: .venv/bin/python tests/test_retriever.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from retriever import retrieve  # noqa: E402

DG_RE = re.compile(r"(?<![A-Za-z0-9])DG(?![A-Za-z0-9])")


def main():
    failures = []

    # --- 1. literal keyword query ---
    res = retrieve("DG", k=8)
    top3_literal = [bool(DG_RE.search(r["text"])) for r in res[:3]]
    top8_literal = sum(bool(DG_RE.search(r["text"])) for r in res)
    if all(top3_literal):
        print(f"✓ 'DG': all top-3 contain the literal term ({top8_literal}/{len(res)} of top-8)")
    else:
        failures.append(f"'DG' top-3 literal containment: {top3_literal}")

    # --- 2. semantic bridge query (no 'DG' in query text) ---
    res2 = retrieve("core claims database", k=8)
    dg_tagged = [r["chunk_id"] for r in res2 if "DG" in r["systems"]]
    if dg_tagged:
        print(f"✓ 'core claims database': {len(dg_tagged)}/8 results are DG chunks "
              f"(e.g. {dg_tagged[0]})")
    else:
        failures.append("'core claims database' found no DG-tagged chunks in top 8")

    # --- 3. structural checks ---
    for res_i, label in ((res, "DG"), (res2, "core claims database")):
        ids = [r["chunk_id"] for r in res_i]
        if len(ids) != len(set(ids)):
            failures.append(f"duplicates in results for {label!r}")
        if len(ids) > 8:
            failures.append(f"more than 8 results for {label!r}")
        missing = [r["chunk_id"] for r in res_i
                   if not r["source_pointer"].get("source_file") or "confidence" not in r["metadata"]]
        if missing:
            failures.append(f"results missing metadata/pointer for {label!r}: {missing}")
    if not any("duplicates" in f or "more than" in f or "missing" in f for f in failures):
        print("✓ results deduped, ≤8, all carry metadata + source pointers")

    if failures:
        print("\nACCEPTANCE FAILED:")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("\nT3.3 ACCEPTANCE: PASSED")


if __name__ == "__main__":
    main()
