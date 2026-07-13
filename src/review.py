"""REVIEW inbox (Phase 7): one worklist of everything needing knowledge
attention, merged from three sources (linked, not duplicated in storage):

  UNANSWERED       usage_log entries whose answer was a refusal
  LOW-CONFIDENCE   usage_log grounded answers with confidence LOW or staleness
  OPEN GAP         gaps.yaml open entries

Each item carries enough context for the Smart Loop intake panel
(question, what was answered, retrieved docs). SL5 paragraph correction is
provided by smart_loop.clean_submission; resolution helpers re-run the
original question and update the relevant stores.
"""

from datetime import datetime

import yaml

from src import config
from src.analytics import load_log
from src.verify import STALE_NOTE


def worklist() -> list[dict]:
    items: list[dict] = []
    seen_questions: set[str] = set()

    # (a) + (b) from usage log — newest first, deduped by question
    for e in reversed(load_log()):
        qn = e["question"].strip().lower()
        if qn in seen_questions:
            continue
        if e["status"] in ("not_in_kb", "rejected"):
            seen_questions.add(qn)
            items.append({
                "type": "UNANSWERED",
                "question": e["question"],
                "answered": "(refused: Not in knowledge base.)",
                "retrieved": e.get("retrieved", []),
                "sme": "TBD",
                "date": e["ts"][:10],
                "key": f"ua::{qn}",
            })
        elif e["status"] == "grounded" and e.get("confidence") == "LOW":
            seen_questions.add(qn)
            items.append({
                "type": "LOW-CONFIDENCE",
                "question": e["question"],
                "answered": f"grounded but LOW confidence (docs: {', '.join(e.get('docs_cited', []))})",
                "retrieved": e.get("retrieved", []),
                "sme": "TBD",
                "date": e["ts"][:10],
                "key": f"lc::{qn}",
            })

    # (c) open gaps
    if config.GAPS_FILE.exists():
        for g in (yaml.safe_load(config.GAPS_FILE.read_text()) or {}).get("gaps", []):
            if g.get("status") != "open":
                continue
            qn = g["question"].strip().lower()
            if qn in seen_questions:
                # merge: keep the gap id on the existing row
                for it in items:
                    if it["question"].strip().lower() == qn:
                        it["gap_id"] = g["id"]
                        it["sme"] = g.get("suggested_sme", "TBD")
                continue
            items.append({
                "type": "OPEN GAP",
                "question": g["question"],
                "answered": "; ".join(g.get("missing_info", []))[:150],
                "retrieved": g.get("retrieved_ids", []),
                "sme": g.get("suggested_sme", "TBD"),
                "date": g.get("last_asked", g.get("date", "")),
                "gap_id": g["id"],
                "key": f"gap::{g['id']}",
            })
    return items


def resolve_and_reask(question: str) -> dict:
    """After new evidence is ingested, re-run the original question and
    return the fresh result (the panel shows before/after)."""
    from src.answer import answer
    return answer(question)


def add_bank_candidate(question: str) -> None:
    from src.qa_bank import record_candidate
    record_candidate(question)
