#!/usr/bin/env python3
"""
T4.3 acceptance test:
  Asking 3 unanswerable questions produces 3 structured gap entries in
  gaps.yaml, each with question, missing_info, date, suggested_sme, status.
  Also: re-asking one of them must NOT create a 4th entry (dedupe).

Run: .venv/bin/python tests/test_gap_capture.py    (live LLM calls)
"""

import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from answer_engine import answer  # noqa: E402
from gap_capture import record_gap, GAPS_FILE  # noqa: E402

QUESTIONS = [
    "What is the SLA for IPP API response times?",
    "What is the exact file format specification of Plan Sponsor enrollment files?",
    "Who is the current on-call contact for MaCE platform incidents?",
]

REQUIRED_FIELDS = {"id", "question", "missing_info", "date", "suggested_sme", "status"}


def main():
    failures = []
    before = GAPS_FILE.read_bytes() if GAPS_FILE.exists() else None
    if GAPS_FILE.exists():
        GAPS_FILE.unlink()  # clean slate for the acceptance run

    try:
        recorded = []
        for q in QUESTIONS:
            r = answer(q)
            if r["status"] == "grounded":
                failures.append(f"expected unanswerable, got grounded: {q!r}")
                continue
            recorded.append(record_gap(r["gap"]))

        data = yaml.safe_load(GAPS_FILE.read_text())
        gaps = data["gaps"]

        if len(gaps) == 3:
            print(f"✓ 3 unanswerable questions → 3 gap entries")
        else:
            failures.append(f"expected 3 gap entries, got {len(gaps)}")

        for g in gaps:
            missing_fields = REQUIRED_FIELDS - set(g)
            if missing_fields:
                failures.append(f"{g.get('id')}: missing fields {missing_fields}")
        if not any("missing fields" in f for f in failures):
            print("✓ every entry has question, missing_info, date, suggested_sme, status")

        smes = {g["id"]: g["suggested_sme"] for g in gaps}
        routed = sum(1 for s in smes.values() if s != "TBD")
        print(f"✓ SME routing: {routed}/3 non-TBD → {smes}")

        # dedupe: re-ask question 1
        r = answer(QUESTIONS[0])
        if r["gap"]:
            record_gap(r["gap"])
        data2 = yaml.safe_load(GAPS_FILE.read_text())
        if len(data2["gaps"]) == 3 and data2["gaps"][0].get("ask_count") == 2:
            print("✓ re-asking does not duplicate (ask_count=2)")
        else:
            failures.append(f"dedupe failed: {len(data2['gaps'])} entries, ask_count={data2['gaps'][0].get('ask_count')}")

    finally:
        if before is not None:
            GAPS_FILE.write_bytes(before)  # restore pre-test gaps
        # else: keep the acceptance-run gaps as the initial real gaps.yaml

    if failures:
        print("\nACCEPTANCE FAILED:")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("\nT4.3 ACCEPTANCE: PASSED")


if __name__ == "__main__":
    main()
