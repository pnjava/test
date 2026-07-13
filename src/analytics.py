"""Usage analytics (Phase 7 INSIGHTS).

Every Q&A is logged to usage_log.yaml:
  {question, corrected, answered, refused, confidence, bank_hit, docs_cited, ts}

Insights computed here:
  - most-asked topics (by cited doc)
  - refusal rate
  - low-confidence answers
  - golden-set candidates (frequent or refused questions)
  - GAP IMPACT RANKING: gaps ordered by how many distinct user questions
    touched them (retrieval overlap), for SME outreach prioritization.
"""

from collections import Counter
from datetime import datetime

import yaml

from src import config

USAGE_LOG = config.ROOT / "usage_log.yaml"


def log_qa(question: str, corrected: str, result: dict) -> None:
    data = yaml.safe_load(USAGE_LOG.read_text()) if USAGE_LOG.exists() else None
    data = data or {"log": []}
    data["log"].append({
        "question": question,
        "corrected": corrected if corrected != question else None,
        "status": result.get("status"),
        "confidence": result.get("confidence", "n/a"),
        "bank_hit": bool(result.get("bank_hit")),
        "docs_cited": sorted({c.split("#")[0] for c in result.get("citations", [])}),
        "retrieved": result.get("retrieved_ids", []),
        "ts": datetime.now().isoformat(timespec="seconds"),
    })
    USAGE_LOG.write_text(yaml.safe_dump(data, sort_keys=False, width=110, allow_unicode=True))


def load_log() -> list[dict]:
    if not USAGE_LOG.exists():
        return []
    return (yaml.safe_load(USAGE_LOG.read_text()) or {}).get("log", [])


def insights() -> dict:
    log = load_log()
    if not log:
        return {"total": 0, "refusal_rate": 0.0, "top_docs": [], "low_confidence": [],
                "golden_candidates": [], "gap_impact": []}

    total = len(log)
    refused = [e for e in log if e["status"] in ("not_in_kb", "rejected")]
    low_conf = [e for e in log if e.get("confidence") == "LOW" and e["status"] == "grounded"]

    doc_counter = Counter(d for e in log for d in e.get("docs_cited", []))

    q_counter = Counter(e["question"].strip().lower() for e in log)
    frequent = [q for q, n in q_counter.most_common() if n >= 2]
    refused_qs = [e["question"] for e in refused]
    golden_candidates = list(dict.fromkeys(frequent + refused_qs))[:10]

    # gap impact: overlap between each open gap's retrieved docs and user questions
    gap_impact = []
    if config.GAPS_FILE.exists():
        gaps = (yaml.safe_load(config.GAPS_FILE.read_text()) or {}).get("gaps", [])
        for g in gaps:
            if g.get("status") != "open":
                continue
            gap_docs = {c.split("#")[0] for c in g.get("retrieved_ids", [])}
            touches = sum(
                1 for e in log
                if gap_docs & set(e.get("docs_cited", []))
                or g["question"].strip().lower() == e["question"].strip().lower()
            )
            gap_impact.append({"id": g["id"], "question": g["question"],
                               "sme": g.get("suggested_sme", "TBD"), "impact": touches})
        gap_impact.sort(key=lambda x: -x["impact"])

    return {
        "total": total,
        "refusal_rate": round(len(refused) / total, 3),
        "top_docs": doc_counter.most_common(8),
        "low_confidence": [{"question": e["question"], "docs": e["docs_cited"]} for e in low_conf][:10],
        "golden_candidates": golden_candidates,
        "gap_impact": gap_impact[:10],
    }
