"""Phase 7 acceptance demos — Smart Loop 4 cases + REVIEW round-trip + insights.

Run: .venv/bin/python tests/demo_phase7.py
Content rule respected: every ingested "SME answer" comes from REAL phase-1
artifacts (RCS roadmap / enrollment diagram extractions) — nothing invented.
The deliberately-false CONFLICT case is ingested as state=disputed, then
CLEANED UP (doc + register entry removed) so the KB is not polluted.
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src import config, smart_loop, review, analytics  # noqa: E402
from src.answer import answer  # noqa: E402
from src.gaps import record_gap  # noqa: E402

PASS, FAIL = "✓", "✗"
failures: list[str] = []


def check(ok: bool, label: str) -> None:
    print(f"  {PASS if ok else FAIL} {label}")
    if not ok:
        failures.append(label)


# --------------------------------------------------------------- case 1
print("== SL case 1: CLEAN ACCEPT (real content: CSI Web ownership) ==")
q1 = "Who owns CSI Web and what technology is it built with?"
sub1 = ("CSI Web is owned by Chris Byrd. It is built with ASP.NET on SQL Server and "
        "hosted on-premise. It is an existing application that needs enhancement for "
        "member preference capture (cell phone, SMS consent, RCS and email preferences), "
        "with preferences stored in the same local SQL Server database. "
        "Source: Meritain RCS Solution Architecture component inventory (Narendra, 2026-03-26).")
v1 = smart_loop.validate_submission(q1, sub1)
check(not v1["blocked"], "SL3 PHI clean")
check(v1["relevance"]["verdict"] in ("RELEVANT", "PARTIAL"), f"SL1 = {v1['relevance']['verdict']}")
check(v1["consistency"]["verdict"] == "CONSISTENT", f"SL2 = {v1['consistency']['verdict']}")
p1 = smart_loop.save_and_ingest("gap-csiweb-owner", q1, sub1, "Narendra (RCS arch doc)", v1)
r1 = answer(q1)
check(r1["status"] == "grounded" and any("gap-csiweb-owner" in c for c in r1["citations"]),
      f"re-ask grounded, cites SME doc ({r1['citations']})")

# --------------------------------------------------------------- case 2
print("== SL case 2: OFF-TOPIC warned then FORCED (badge tracked) ==")
q2 = "What is the SLA for IPP API response times?"
sub2 = ("The Meritain cafeteria in Phoenix rotates its lunch menu weekly and Friday "
        "is bagel day for the architecture team.")
v2 = smart_loop.validate_submission(q2, sub2)
check(v2["relevance"]["verdict"] == "OFF-TOPIC", f"SL1 = {v2['relevance']['verdict']} ({v2['relevance']['reason'][:60]})")
p2 = smart_loop.save_and_ingest("gap-003-demo-forced", q2, sub2, "demo-user", v2, forced=True)
fm2 = yaml.safe_load(p2.read_text().split("---")[1])
check(fm2["confidence"] == "unverified-forced" and fm2.get("forced_by") == "demo-user",
      "frontmatter: confidence=unverified-forced + forced_by recorded")
import chromadb  # noqa: E402
coll = chromadb.PersistentClient(path=str(config.CHROMA_DIR)).get_collection(config.COLLECTION_NAME)
got2 = coll.get(where={"doc_id": fm2["id"]}, include=["metadatas"])
check(bool(got2["ids"]) and got2["metadatas"][0]["confidence"] == "unverified-forced",
      "ingested chunk carries unverified-forced (app shows ⚠ badge on citation)")

# --------------------------------------------------------------- case 3
print("== SL case 3: CONFLICT -> contradiction register + disputed ingest ==")
q3 = "How much repricing goes to BAMR?"
sub3 = "Only about 10% of DG transactions are repriced on BAMR; the vast majority price internally."
v3 = smart_loop.validate_submission(q3, sub3)
check(v3["consistency"]["verdict"] == "CONFLICT", f"SL2 = {v3['consistency']['verdict']} ({v3['consistency']['detail'][:60]})")
reg_before = len(yaml.safe_load(config.CONTRADICTION_REGISTER.read_text())["decisions"])
dec_id = smart_loop.record_contradiction("gap-004-demo", sub3[:60], v3["consistency"]["detail"])
reg_after = yaml.safe_load(config.CONTRADICTION_REGISTER.read_text())["decisions"]
check(len(reg_after) == reg_before + 1 and reg_after[-1]["status"] == "open",
      f"contradiction {dec_id} appended (status: open)")
p3 = smart_loop.save_and_ingest("gap-004-demo", q3, sub3, "demo-user", v3, disputed=True)
got3 = coll.get(where={"doc_id": yaml.safe_load(p3.read_text().split('---')[1])["id"]}, include=["metadatas"])
check(bool(got3["ids"]) and got3["metadatas"][0]["state"] == "disputed", "ingested as state=disputed")

# --------------------------------------------------------------- case 4
print("== SL case 4: PHI blocked, NO force option ==")
q4 = "Who are the Plan Build business resources?"
sub4 = "Lynn's member test record uses SSN 123-45-6789 and email lynn.f.test@gmail.com."
v4 = smart_loop.validate_submission(q4, sub4)
check(v4["blocked"] and not v4["phi"]["clean"], "SL3 blocked ingest entirely")
check(v4["relevance"] is None, "SL1/SL2 never ran (PHI short-circuits)")
masked = str(v4["phi"]["hits"])
check("123-45-6789" not in masked, "flagged lines masked (no raw PHI in report)")

# --------------------------------------------------------------- review round-trip
print("== REVIEW round-trip: UNANSWERED -> SL5 correction -> resolve ==")
q5 = "What channels does the Meritain RCS welcome campaign use?"
r5a = answer(q5)
if r5a["status"] != "grounded":
    record_gap(q5, r5a.get("gaps") or ["(none listed)"], r5a.get("retrieved_ids", []))
analytics.log_qa(q5, q5, r5a)
items = review.worklist()
check(any(q5.lower() == it["question"].lower() and it["type"] in ("UNANSWERED", "OPEN GAP")
          for it in items), "question appears in REVIEW worklist")

typo_sub = ("teh welcom campain uses RCS SMS and emale channles for newly enroled members, "
            "transactionl mesages only no marketing, mesages free of charge and branded as "
            "Meritain per TCPA. Sorce: Meritain RCS Roadmap slide 4 (2026).")
corrected = smart_loop.clean_submission(typo_sub)
check("welcome" in corrected.lower() and "email" in corrected.lower(),
      f"SL5 corrected typos ({corrected[:60]!r}…)")
check("meritain" in corrected.lower() and "rcs" in corrected.lower(), "SL5 preserved names/acronyms")

v5 = smart_loop.validate_submission(q5, corrected)
check(not v5["blocked"] and v5["relevance"]["verdict"] in ("RELEVANT", "PARTIAL"),
      f"validation on corrected text: {v5['relevance']['verdict']}")
p5 = smart_loop.save_and_ingest("gap-005-rcs", q5, corrected, "Narendra (RCS roadmap)", v5,
                                original_submission=typo_sub)
fm5 = yaml.safe_load(p5.read_text().split("---")[1])
check(fm5.get("original_submission", "").startswith("teh welcom"),
      "original_submission preserved in frontmatter (provenance)")
r5b = review.resolve_and_reask(q5)
check(r5b["status"] == "grounded" and "rcs" in r5b["answer"].lower(),
      f"re-ask grounded (confidence: {r5b.get('confidence')})")
review.add_bank_candidate(q5)

# --------------------------------------------------------------- insights
print("== INSIGHTS populate ==")
for q in ["What is DG?", "What is WebDE?", "How are ID cards printed?"]:
    analytics.log_qa(q, q, answer(q))
ins = analytics.insights()
check(ins["total"] >= 4, f"usage log populated ({ins['total']} entries)")
check(bool(ins["top_docs"]), f"top docs: {ins['top_docs'][:3]}")
check(isinstance(ins["gap_impact"], list), "gap impact ranking computed")

# --------------------------------------------------------------- cleanup case 3
print("== cleanup: remove disputed demo content ==")
coll.delete(where={"doc_id": "gap-004-demo-sme-answer"})
p3.unlink(missing_ok=True)
reg = yaml.safe_load(config.CONTRADICTION_REGISTER.read_text())
reg["decisions"] = [d for d in reg["decisions"] if d["id"] != dec_id]
config.CONTRADICTION_REGISTER.write_text(yaml.safe_dump(reg, sort_keys=False, width=110, allow_unicode=True))
print("  disputed demo doc + register entry removed")

print()
if failures:
    print(f"PHASE 7 ACCEPTANCE: {len(failures)} FAILURES")
    for f in failures:
        print(f"  ✗ {f}")
    sys.exit(1)
print("PHASE 7 ACCEPTANCE: ALL CASES PASSED")
