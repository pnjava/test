#!/usr/bin/env python3
"""
T1.1 acceptance test:
  - Seeded file with 5 fake PHI patterns → all 5 pattern types caught
  - Clean file (realistic architecture text) → passes with zero hits

Run: python3 tests/test_phi_scanner.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from phi_pii_scanner import load_patterns, scan_text  # noqa: E402

# 5 seeded fake PHI patterns (all synthetic values)
SEEDED_TEXT = """\
Meeting notes — enrollment file sample review (FAKE TEST DATA)

1. Sample member SSN found in row 12: 123-45-6789
2. Legacy extract had bare SSN column: 478291035
3. Member record: MBR-48291047 flagged for re-enrollment
4. DOB: 04/17/1982 listed next to member name in the CSV header sample
5. Member contact given as jane.doe1982@gmail.com for follow-up
"""

# Realistic clean text — includes corporate emails and version numbers that
# must NOT trigger false positives
CLEAN_TEXT = """\
Meritain RCS Solution Architecture review notes.

Day 1 uses DataVision/EDP as preference source of truth; Day 2 migrates to
IPP. Contact the IPP team at ipp-support@aetna.com for the Swagger spec.
Chris Byrd (chris.byrd@meritain.com) owns CSI Web enhancements.
Escalations go to Jane.Smith@AETNA.com or ops@CVSHealth.com (mixed-case
corporate domains must not be flagged).

API endpoint: GET /ipp/v1/members/{id}/preferences
Roadmap deck version 2.1, slide 11. Estimated effort 10-12 weeks.
Table MemberPreferences has 15 columns; audit retention is 2555 days.
"""

EXPECTED_PATTERNS = {"ssn_dashed", "ssn_bare", "member_id", "dob_with_name", "personal_email"}


def main():
    patterns = load_patterns()
    failures = []

    # --- Seeded file: all 5 pattern types must be caught ---
    hits = scan_text(SEEDED_TEXT, patterns)
    caught = {h["pattern"] for h in hits}
    missed = EXPECTED_PATTERNS - caught
    if missed:
        failures.append(f"Seeded test MISSED patterns: {sorted(missed)}")
    else:
        print(f"✓ Seeded file: all 5 pattern types caught ({sorted(caught)})")

    # --- Clean file: zero hits ---
    clean_hits = scan_text(CLEAN_TEXT, patterns)
    if clean_hits:
        failures.append(
            "Clean file FALSE POSITIVES: "
            + ", ".join(f"{h['pattern']}×{h['count']}" for h in clean_hits)
        )
    else:
        print("✓ Clean file: zero hits (corporate emails, versions, weeks not flagged)")

    # --- Log must mask raw values ---
    for h in hits:
        for sample in h["masked_samples"]:
            if "*" not in sample:
                failures.append(f"Unmasked sample in log output: {sample}")
    if not failures or all("Unmasked" not in f for f in failures):
        print("✓ All logged samples are masked (no raw PHI in quarantine log)")

    if failures:
        print("\nACCEPTANCE FAILED:")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("\nT1.1 ACCEPTANCE: PASSED")


if __name__ == "__main__":
    main()
