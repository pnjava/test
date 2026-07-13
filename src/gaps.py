"""Gap register (M3, R6): append unanswered/partial questions to gaps.yaml.

Dedupe by normalized question text (re-asks bump ask_count).
suggested_sme mapping per spec keyword routing.

Library:
    from src.gaps import record_gap, load_gaps
CLI:
    python -m src.gaps --list
"""

import re
import sys
from datetime import date

import yaml

from src import config

# first regex match wins (case-insensitive)
SME_ROUTING: list[tuple[str, str]] = [
    (r"\bcdc\b|\bdata\b|kafka|outbox|rdrs|mongodb|datavision|cache", "Rakesh/Ali"),
    (r"\bdg\b|universe|pick|mvdb|webde|benton|drafts|adjudicat|backup|license", "DG SMEs"),
    (r"integration|biztalk|sterling|axway|\bitx\b|translation|file transfer|edi", "Bob's team"),
    (r"contact center|\bivr\b|edify|avaya|five9|telephony", "Sunil/Ramesh"),
    (r"strategy|north star|roadmap|modernization|target architecture|superapp", "Muhammad"),
    (r"plan build|plan sponsor setup|benefit build", "Lynn Fletcher/Terrie Nicks"),
]


def suggest_sme(question: str, missing: list[str]) -> str:
    text = question + " " + " ".join(missing)
    for pattern, sme in SME_ROUTING:
        if re.search(pattern, text, re.IGNORECASE):
            return sme
    return "TBD"


def load_gaps() -> dict:
    if config.GAPS_FILE.exists():
        data = yaml.safe_load(config.GAPS_FILE.read_text()) or {}
    else:
        data = {}
    data.setdefault("gaps", [])
    return data


def _save(data: dict) -> None:
    data["metadata"] = {
        "updated": date.today().isoformat(),
        "open": sum(1 for g in data["gaps"] if g["status"] == "open"),
        "answered": sum(1 for g in data["gaps"] if g["status"] == "answered"),
    }
    config.GAPS_FILE.write_text(yaml.safe_dump(data, sort_keys=False, width=110, allow_unicode=True))


def record_gap(question: str, missing_info: list[str], retrieved_ids: list[str] | None = None) -> dict:
    """Append (or bump) a gap entry. Returns the entry."""
    data = load_gaps()
    qnorm = question.strip().lower()

    for g in data["gaps"]:
        if g["question"].strip().lower() == qnorm and g["status"] == "open":
            g["ask_count"] = g.get("ask_count", 1) + 1
            g["last_asked"] = date.today().isoformat()
            _save(data)
            return g

    entry = {
        "id": f"gap-{len(data['gaps']) + 1:03d}",
        "question": question,
        "missing_info": missing_info or ["(not enumerated)"],
        "date": date.today().isoformat(),
        "last_asked": date.today().isoformat(),
        "ask_count": 1,
        "suggested_sme": suggest_sme(question, missing_info),
        "status": "open",
        "retrieved_ids": retrieved_ids or [],
    }
    data["gaps"].append(entry)
    _save(data)
    return entry


def seed_sme_questions() -> list[dict]:
    """The 29 curated questions from kb/knowledge/sme-questions.md as gap-like
    rows (read-only source; grouped-by-owner headers carry the SME)."""
    path = config.KB_DIR / "sme-questions.md"
    if not path.exists():
        return []
    rows, sme = [], "TBD"
    for line in path.read_text(errors="replace").splitlines():
        h = re.match(r"^##\s+(.*)$", line)
        if h:
            sme = h.group(1).strip()
            continue
        q = re.match(r"^(\d+)\.\s+(.*)$", line.strip())
        if q:
            rows.append({
                "id": f"smeq-{int(q.group(1)):02d}",
                "question": q.group(2).strip(),
                "suggested_sme": sme,
                "status": "open",
                "source": "sme-questions.md",
                "last_asked": "",
            })
    return rows


def qa_bank_gaps() -> list[dict]:
    """The QA bank's 27 known-unanswerable entries as gap-like rows."""
    if not config.QA_BANK.exists():
        return []
    bank = yaml.safe_load(config.QA_BANK.read_text())["qa_bank"]
    return [{
        "id": e["id"],
        "question": e["question"],
        "suggested_sme": e.get("suggested_sme") or "TBD",
        "status": "open",
        "source": "qa_bank.yaml",
        "last_asked": "",
    } for e in bank if e.get("answerable") == "N"]


def main() -> None:
    if sys.argv[1:2] == ["--list"]:
        data = load_gaps()
        for g in data["gaps"]:
            print(f"{g['id']} [{g['status']}] ({g['suggested_sme']}) {g['question']}")
        print(f"\n{data.get('metadata', {})}")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
