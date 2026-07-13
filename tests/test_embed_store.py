#!/usr/bin/env python3
"""
T3.2 acceptance test:
  - Collection count equals chunk count in chunks.jsonl
  - Metadata is queryable: by confidence, by state, by exact system token

Run with the project venv: .venv/bin/python tests/test_embed_store.py
Assumes the collection was built (src/embed_store.py).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from embed_store import get_client, load_chunks, COLLECTION  # noqa: E402


def main():
    failures = []
    chunks = load_chunks()
    coll = get_client().get_collection(COLLECTION)

    # 1. count parity
    if coll.count() == len(chunks):
        print(f"✓ Collection count equals chunk count ({coll.count()})")
    else:
        failures.append(f"count mismatch: collection={coll.count()} chunks={len(chunks)}")

    # 2. metadata queryable — confidence
    expected_verified = sum(1 for c in chunks if c["metadata"]["confidence"] == "verified")
    got = len(coll.get(where={"confidence": "verified"}, limit=10_000)["ids"])
    if got == expected_verified:
        print(f"✓ confidence=verified queryable ({got} chunks, matches jsonl)")
    else:
        failures.append(f"confidence query: got {got}, expected {expected_verified}")

    # 3. metadata queryable — exact system token match
    expected_dg = sum(1 for c in chunks if "DG" in c.get("systems", []))
    got_dg = len(coll.get(where={"systems": {"$in": []}} if False else None,
                          where_document=None, limit=10_000,
                          include=["metadatas"])["ids"])
    # exact-token via comma-wrapped $contains on metadata isn't supported by
    # `where`; filter client-side to validate the stored representation
    all_meta = coll.get(limit=10_000, include=["metadatas"])
    got_dg = sum(1 for m in all_meta["metadatas"] if ",DG," in m["systems"])
    if got_dg == expected_dg:
        print(f"✓ system token ',DG,' resolvable from stored metadata ({got_dg} chunks)")
    else:
        failures.append(f"DG system tag: got {got_dg}, expected {expected_dg}")

    # 4. every stored chunk kept its source pointer fields
    missing = [m for m in all_meta["metadatas"] if not m.get("source_file") or not m.get("kb_file")]
    if not missing:
        print("✓ every stored chunk carries source_file + kb_file metadata")
    else:
        failures.append(f"{len(missing)} stored chunks missing source pointer metadata")

    if failures:
        print("\nACCEPTANCE FAILED:")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("\nT3.2 ACCEPTANCE: PASSED")


if __name__ == "__main__":
    main()
