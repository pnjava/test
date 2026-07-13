#!/usr/bin/env python3
"""
T4.1 acceptance test:
  1. validate() contract (no LLM): invented citations rejected, uncited
     answers rejected, proper answers accepted
  2. LIVE: question with no relevant chunks -> "Not in knowledge base."
     + structured gap record (never a fabricated answer)
  3. LIVE: known-answer question -> grounded status, >=1 citation, every
     citation resolves to a retrieved chunk

Run: .venv/bin/python tests/test_answer_engine.py         (includes live LLM calls)
     .venv/bin/python tests/test_answer_engine.py --fast  (contract checks only)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from answer_engine import validate, answer, NOT_IN_KB  # noqa: E402

RETRIEVED = ["doc_a::c001", "doc_a::c002", "doc_b::c001"]


def contract_checks():
    failures = []

    ok, cited, invalid, nk, _ = validate("DG runs UniVerse [doc_a::c001].", RETRIEVED)
    if not (ok and cited == ["doc_a::c001"] and not nk):
        failures.append("valid cited answer was not accepted")

    ok, _, invalid, _, _ = validate("DG runs UniVerse [made_up::c999].", RETRIEVED)
    if ok or invalid != ["made_up::c999"]:
        failures.append("invented citation was not rejected")

    ok, _, _, _, _ = validate("DG runs UniVerse and Pick.", RETRIEVED)
    if ok:
        failures.append("uncited factual answer was not rejected")

    ok, _, _, nk, missing = validate(
        NOT_IN_KB + "\nMISSING: IPP SLA figures", RETRIEVED
    )
    if not (ok and nk and missing):
        failures.append("proper not-in-KB answer was not accepted")

    return failures


def live_checks():
    failures = []

    # unanswerable: nothing in the KB about this
    r = answer("What is the exact monthly licensing cost of the MaCE platform?")
    if r["status"] == "grounded":
        failures.append(f"unanswerable question got a grounded answer: {r['answer'][:200]}")
    else:
        if not r["answer"].startswith(NOT_IN_KB) and r["status"] != "rejected":
            failures.append(f"unanswerable: unexpected answer format: {r['answer'][:200]}")
        if not r["gap"] or r["gap"]["question"] != "What is the exact monthly licensing cost of the MaCE platform?":
            failures.append("no structured gap record for unanswerable question")
        else:
            print(f"✓ unanswerable → {r['status']}, gap recorded ({r['gap']['missing_info'][:1]})")

    # answerable: known fact with verbatim source
    r2 = answer("What technology is DG built on?")
    if r2["status"] != "grounded":
        failures.append(f"known-answer question not grounded: status={r2['status']}")
    else:
        bad = [c for c in r2["citations"] if c not in r2["chunks"]]
        if bad:
            failures.append(f"citations not in retrieved set: {bad}")
        elif "universe" not in r2["answer"].lower():
            failures.append(f"grounded answer missing expected fact: {r2['answer'][:200]}")
        else:
            print(f"✓ known question → grounded, cites {r2['citations']}")

    return failures


def main():
    failures = contract_checks()
    if not failures:
        print("✓ citation contract: invented/uncited rejected, valid accepted")

    if "--fast" not in sys.argv:
        failures += live_checks()

    if failures:
        print("\nACCEPTANCE FAILED:")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("\nT4.1 ACCEPTANCE: PASSED")


if __name__ == "__main__":
    main()
