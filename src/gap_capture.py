#!/usr/bin/env python3
"""
Gap Capture (T4.3)

Appends "Not in knowledge base" results to knowledge/gaps.yaml as structured
entries: question, missing info, date, suggested SME, status.

Duplicate questions (case-insensitive) update ask_count/last_asked instead of
creating a second entry.

SME suggestion is keyword-based (SME_ROUTING below) — a hint for the export
(T5.2), not an assignment.

Library use:
    from gap_capture import record_gap
    record_gap(result["gap"])          # result from answer_engine.answer()

CLI:
    .venv/bin/python src/gap_capture.py --list
    .venv/bin/python src/gap_capture.py --ask "unanswerable question"  # answer + record
"""

import re
import sys
import yaml
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
GAPS_FILE = ROOT / "knowledge" / "gaps.yaml"

# keyword (case-insensitive regex) -> suggested SME, first match wins
SME_ROUTING = [
    (r"\bIPP\b|preference platform|book of record", "IPP Team"),
    (r"\bDG\b|universe|pick|webde|draft process|adjudicat", "Bill Cadman / DG Team"),
    (r"\bCSI\b|preference api|local sql|consent captur", "Chris Byrd"),
    (r"\bMaCE\b|messag|infobip|\bCSG\b|\bRCS\b|\bSMS\b", "MaCE Team"),
    (r"biztalk|sterling|axway|\bITX\b|\bMALF\b|translation|file transfer", "Bob (integration SME — surname unknown)"),
    (r"\bIMI\b|proxy id|individual master", "IMI Team (contact TBD)"),
    (r"architect|roadmap|day 1|day 2|conceptual", "Muhammad Muddassar Ali"),
    (r"enroll|834|eligibility|plan sponsor", "Enrollment Process Team (TBD)"),
    (r"tcpa|compliance|consent|dnc|rnd", "Legal/Compliance (TBD)"),
]


def suggest_sme(question, missing_info):
    text = question + " " + " ".join(missing_info)
    for pattern, sme in SME_ROUTING:
        if re.search(pattern, text, re.IGNORECASE):
            return sme
    return "TBD"


def load_gaps():
    if GAPS_FILE.exists():
        data = yaml.safe_load(GAPS_FILE.read_text()) or {}
    else:
        data = {}
    data.setdefault("gaps", [])
    return data


def save_gaps(data):
    data["metadata"] = {
        "updated": date.today().isoformat(),
        "open": sum(1 for g in data["gaps"] if g["status"] == "open"),
        "answered": sum(1 for g in data["gaps"] if g["status"] == "answered"),
    }
    GAPS_FILE.write_text(yaml.safe_dump(data, sort_keys=False, width=110, allow_unicode=True))


def record_gap(gap):
    """gap = {question, missing_info, retrieved_chunks_considered} from answer_engine.
    Returns the gap entry (new or updated existing)."""
    data = load_gaps()
    qnorm = gap["question"].strip().lower()

    for g in data["gaps"]:
        if g["question"].strip().lower() == qnorm and g["status"] == "open":
            g["ask_count"] = g.get("ask_count", 1) + 1
            g["last_asked"] = date.today().isoformat()
            save_gaps(data)
            return g

    entry = {
        "id": f"gap{len(data['gaps']) + 1:03d}",
        "question": gap["question"],
        "missing_info": gap.get("missing_info", []),
        "date": date.today().isoformat(),
        "last_asked": date.today().isoformat(),
        "ask_count": 1,
        "suggested_sme": suggest_sme(gap["question"], gap.get("missing_info", [])),
        "status": "open",
        "retrieved_chunks_considered": gap.get("retrieved_chunks_considered", []),
    }
    data["gaps"].append(entry)
    save_gaps(data)
    return entry


def main():
    args = sys.argv[1:]
    if args[:1] == ["--list"]:
        data = load_gaps()
        for g in data["gaps"]:
            print(f"{g['id']} [{g['status']}] ({g['suggested_sme']}) {g['question']}")
        print(f"\n{data.get('metadata', {})}")
        return

    if args[:1] == ["--ask"] and len(args) > 1:
        sys.path.insert(0, str(Path(__file__).parent))
        from answer_engine import answer

        result = answer(" ".join(args[1:]))
        print(f"status: {result['status']}\n{result['answer']}\n")
        if result["gap"]:
            entry = record_gap(result["gap"])
            print(f"→ gap recorded: {entry['id']} (suggested SME: {entry['suggested_sme']})")
        return

    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
