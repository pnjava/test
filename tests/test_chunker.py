#!/usr/bin/env python3
"""
T3.1 acceptance test:
  - No chunk missing a source pointer
  - No chunk over 400 words
  - Every chunk carries frontmatter metadata (state + confidence at minimum)
  - Chunk IDs are unique

Run: python3 tests/test_chunker.py   (chunks all real KB files in-memory)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from chunker import chunk_file, load_confirmed_aliases, MARKDOWN_DIR, MAX_WORDS  # noqa: E402


def main():
    alias_lookup = load_confirmed_aliases()
    failures = []
    all_chunks = []
    for f in sorted(MARKDOWN_DIR.glob("*.md")):
        all_chunks.extend(chunk_file(f, alias_lookup))

    if not all_chunks:
        print("✗ No chunks produced — is knowledge/markdown/ empty?")
        sys.exit(1)

    oversize = [c["chunk_id"] for c in all_chunks if c["words"] > MAX_WORDS]
    if oversize:
        failures.append(f"{len(oversize)} chunks over {MAX_WORDS} words: {oversize[:5]}")

    no_ptr = [c["chunk_id"] for c in all_chunks
              if not c["source_pointer"].get("kb_file") or not c["source_pointer"].get("source_file")]
    if no_ptr:
        failures.append(f"{len(no_ptr)} chunks missing source pointer: {no_ptr[:5]}")

    no_meta = [c["chunk_id"] for c in all_chunks
               if not c["metadata"].get("state") or not c["metadata"].get("confidence")]
    if no_meta:
        failures.append(f"{len(no_meta)} chunks missing state/confidence metadata: {no_meta[:5]}")

    ids = [c["chunk_id"] for c in all_chunks]
    if len(ids) != len(set(ids)):
        failures.append("Duplicate chunk IDs found")

    print(f"Chunked {len(all_chunks)} chunks from {len(list(MARKDOWN_DIR.glob('*.md')))} files")
    if failures:
        print("ACCEPTANCE FAILED:")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    print(f"✓ All chunks ≤{MAX_WORDS} words")
    print("✓ All chunks carry source pointers")
    print("✓ All chunks carry state/confidence metadata")
    print("✓ Chunk IDs unique")
    print("\nT3.1 ACCEPTANCE: PASSED")


if __name__ == "__main__":
    main()
