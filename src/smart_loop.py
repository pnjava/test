"""Smart Loop intake (Phase 7): validated SME answer ingestion.

Validation chain before ANY ingest:
  SL5 (review path) clean_submission(): LLM-corrected text, user picks —
      never silently rewritten; both versions preserved.
  SL1 relevance:   VALIDATE_ANSWER -> RELEVANT / PARTIAL / OFF-TOPIC (+reason)
                   OFF-TOPIC may be force-uploaded (tracked as unverified-forced).
  SL2 consistency: CONTRADICTION_CHECK vs retrieved KB chunks -> CONSISTENT /
                   CONFLICT. Conflict does NOT refuse: it can be recorded in
                   the contradiction register and ingested as state=disputed.
  SL3 PHI scan:    regex screen (SSN / member id / DOB / personal email) —
                   NON-OVERRIDABLE. Hits block ingest, flagged lines returned.
  SL4 completeness: PARTIAL keeps the gap partially-open with a note.

On accept: answers/<gap-id>.md with full provenance frontmatter ->
ingest --file (incremental) -> gap status update.
"""

import json
import re
import urllib.request
from datetime import date, datetime
from pathlib import Path

import yaml

from src import config
from src.prompts import VALIDATE_ANSWER, CONTRADICTION_CHECK, CLEAN_SUBMISSION

# SL3 reuses the seeded-and-tested PHI patterns from the phase-1 build
from src.phi_pii_scanner import load_patterns, scan_text


def _llm(prompt: str) -> str:
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 512},
    }
    req = urllib.request.Request(f"{config.OLLAMA_URL}/api/chat",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())["message"]["content"].strip()


def clean_submission(text: str) -> str:
    """SL5: corrected text (facts/names/numbers preserved per locked prompt)."""
    return _llm(CLEAN_SUBMISSION.format(text=text))


def check_relevance(question: str, submission: str) -> dict:
    """SL1 -> {verdict: RELEVANT|PARTIAL|OFF-TOPIC, reason}."""
    out = _llm(VALIDATE_ANSWER.format(question=question, submission=submission))
    m = re.match(r"\s*(RELEVANT|PARTIAL|OFF-TOPIC)\b[\s—-]*(.*)", out, re.IGNORECASE | re.DOTALL)
    verdict = m.group(1).upper() if m else "PARTIAL"
    reason = (m.group(2).strip() if m else out)[:300]
    return {"verdict": verdict, "reason": reason}


def check_consistency(submission: str) -> dict:
    """SL2 -> {verdict: CONSISTENT|CONFLICT, detail}."""
    from src.retrieve import retrieve
    chunks = retrieve(submission, k=6)
    rendered = "\n\n".join(f"[{c['chunk_id']}]\n{c['text'][:600]}" for c in chunks)
    out = _llm(CONTRADICTION_CHECK.format(submission=submission, chunks=rendered))
    m = re.match(r"\s*(CONSISTENT|CONFLICT)\b[\s—-]*(.*)", out, re.IGNORECASE | re.DOTALL)
    verdict = m.group(1).upper() if m else "CONSISTENT"
    detail = (m.group(2).strip() if m else out)[:400]
    return {"verdict": verdict, "detail": detail}


def check_phi(text: str) -> dict:
    """SL3 (non-overridable) -> {clean: bool, hits: [...]}."""
    hits = scan_text(text, load_patterns())
    return {"clean": not hits, "hits": hits}


def validate_submission(question: str, submission: str) -> dict:
    """Run SL3 (blocking) + SL1 + SL2. PHI short-circuits everything."""
    phi = check_phi(submission)
    if not phi["clean"]:
        return {"phi": phi, "relevance": None, "consistency": None, "blocked": True}
    return {
        "phi": phi,
        "relevance": check_relevance(question, submission),
        "consistency": check_consistency(submission),
        "blocked": False,
    }


def record_contradiction(gap_id: str, submission_summary: str, conflict_detail: str) -> str:
    """SL2 CONFLICT path: append an open decision to the contradiction register."""
    reg = yaml.safe_load(config.CONTRADICTION_REGISTER.read_text())
    dec_id = f"SME-{gap_id.upper()}-{len(reg['decisions']) + 1:02d}"
    reg["decisions"].append({
        "id": dec_id,
        "topic": f"SME submission conflicts with KB ({gap_id}): {submission_summary[:80]}",
        "status": "open",
        "notes": conflict_detail[:300],
    })
    config.CONTRADICTION_REGISTER.write_text(yaml.safe_dump(reg, sort_keys=False, width=110, allow_unicode=True))
    return dec_id


def save_and_ingest(gap_id: str, question: str, body: str, contributor: str,
                    validation: dict, forced: bool = False,
                    disputed: bool = False, original_submission: str | None = None) -> Path:
    """Persist answers/<gap-id>.md with provenance frontmatter and ingest it."""
    fm = {
        "id": f"{gap_id}-sme-answer",
        "source": f"SME {contributor} {date.today().isoformat()}",
        "state": "disputed" if disputed else "current",
        "confidence": "unverified-forced" if forced else "verified",
        "tags": ["sme-answer", gap_id],
        "gap_question": question,
        "validation": {
            "relevance": (validation.get("relevance") or {}).get("verdict"),
            "consistency": (validation.get("consistency") or {}).get("verdict"),
            "phi": "clean",
        },
    }
    if forced:
        fm["forced_by"] = contributor
        fm["forced_at"] = datetime.now().isoformat(timespec="seconds")
    if original_submission is not None:
        fm["original_submission"] = original_submission

    path = config.ROOT / "answers" / f"{gap_id}.md"
    path.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False, width=110, allow_unicode=True)
                    + "---\n\n# SME answer: " + question + "\n\n" + body + "\n")

    from src.ingest import chunk_doc, upsert_doc, get_collection
    upsert_doc(get_collection(), chunk_doc(path))
    # retrieval + verify caches predate this ingest — refresh them
    from src.retrieve import _corpus
    _corpus.cache_clear()
    from src.verify import stale_doc_ids
    stale_doc_ids.cache_clear()
    return path


def update_gap_status(gap_id: str, status: str, note: str = "") -> None:
    if not config.GAPS_FILE.exists():
        return
    data = yaml.safe_load(config.GAPS_FILE.read_text()) or {"gaps": []}
    for g in data["gaps"]:
        if g["id"] == gap_id:
            g["status"] = status
            if note:
                g["resolution_note"] = note
    config.GAPS_FILE.write_text(yaml.safe_dump(data, sort_keys=False, width=110, allow_unicode=True))
