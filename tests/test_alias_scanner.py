#!/usr/bin/env python3
"""
T2.1 acceptance test:
  Feed two docs where "DG" and "Universe database" both appear →
  exactly ONE pending merge suggestion (DG <-> Universe database variant),
  and aliases.yaml is NOT modified (nothing auto-merged).

Run: python3 tests/test_alias_scanner.py
"""

import hashlib
import subprocess
import sys
import tempfile
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
REGISTRY = ROOT / "knowledge" / "aliases.yaml"
PENDING = ROOT / "knowledge" / "aliases_pending.yaml"
SCANNER = ROOT / "src" / "alias_scanner.py"

DOC1 = """\
Meeting notes A.

DG handles claim adjudication and enrollment processing for Meritain.
The nightly draft process runs on DG five days a week.
"""

DOC2 = """\
Meeting notes B.

Membership records live in the Universe database. One SME clarified:
DG is UniVerse database under the hood, accessed via the WebDE layer.
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    failures = []
    registry_hash_before = sha(REGISTRY)
    pending_before = PENDING.read_bytes() if PENDING.exists() else None

    with tempfile.TemporaryDirectory() as td:
        d1, d2 = Path(td) / "doc1.md", Path(td) / "doc2.md"
        d1.write_text(DOC1)
        d2.write_text(DOC2)

        result = subprocess.run(
            [sys.executable, str(SCANNER), str(d1), str(d2)],
            capture_output=True, text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append(f"Scanner exited {result.returncode}: {result.stderr}")

        report = yaml.safe_load(PENDING.read_text())
        merges = report.get("merge_suggestions", [])

        # Exactly one merge suggestion, linking DG to a Universe-database name
        dg_universe = [
            m for m in merges
            if m["canonical"] == "DG" and "universe" in m["candidate_alias"].lower()
        ]
        if len(dg_universe) == 1:
            print(f"✓ Exactly one DG<->Universe merge suggestion: "
                  f"'{dg_universe[0]['candidate_alias']}' (status={dg_universe[0]['status']})")
        else:
            failures.append(f"Expected exactly 1 DG<->Universe suggestion, got {len(dg_universe)}: {merges}")

        if dg_universe and dg_universe[0]["status"] != "pending":
            failures.append(f"Suggestion status must be 'pending', got {dg_universe[0]['status']}")

        # Registry untouched
        if sha(REGISTRY) == registry_hash_before:
            print("✓ aliases.yaml unmodified (nothing auto-merged)")
        else:
            failures.append("aliases.yaml WAS MODIFIED by the scanner — auto-merge is forbidden")

    # Restore pending file so the test doesn't clobber real scan results
    if pending_before is not None:
        PENDING.write_bytes(pending_before)
    else:
        PENDING.unlink(missing_ok=True)

    if failures:
        print("\nACCEPTANCE FAILED:")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("\nT2.1 ACCEPTANCE: PASSED")


if __name__ == "__main__":
    main()
