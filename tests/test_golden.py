"""THE REGRESSION GATE (v3, 20 questions): run after EVERY KB or prompt change.

    .venv/bin/python -m pytest tests/test_golden.py -v -s

Handles all four question types:
  answerable/decision — answer() must be grounded with expected mentions + citations
  unknown             — answer() must refuse with "Not in knowledge base."
  robustness          — query_fix() then retrieve(); expected docs must be
                        retrieved; if expected_mentions present, the full
                        answer is also checked (incl. forbidden_mentions);
                        must_pass_unchanged asserts query_fix is a no-op
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from src import config  # noqa: E402
from src.answer import answer, NOT_IN_KB  # noqa: E402
from src.query_fix import fix_query  # noqa: E402
from src.retrieve import retrieve  # noqa: E402


def _cited_docs(citations: list[str]) -> set[str]:
    return {c.split("#")[0] for c in citations}


def _check_mentions(q: dict, text: str) -> list[str]:
    problems = []
    tl = text.lower()
    for m in q.get("expected_mentions", []):
        if m.lower() not in tl:
            problems.append(f"missing mention {m!r}")
    any_m = q.get("expected_any_mentions", [])
    if any_m and not any(m.lower() in tl for m in any_m):
        problems.append(f"none of any-mentions present: {any_m}")
    import re as _re
    for m in q.get("forbidden_mentions", []):
        # word-boundary: forbidden 'ERP' must not match 'Enterprise'
        if _re.search(rf"(?<![A-Za-z0-9]){_re.escape(m.lower())}(?![A-Za-z0-9])", tl):
            problems.append(f"forbidden mention present: {m!r}")
    return problems


def _check(q: dict, notes: list[str]) -> list[str]:
    """Returns failure reasons (empty = pass); appends display notes."""
    if q["type"] == "unknown":
        result = answer(q["question"])
        if not result["answer"].startswith(NOT_IN_KB):
            return [f"expected refusal, got: {result['answer'][:80]!r}"]
        return []

    if q["type"] == "robustness":
        problems = []
        fx = fix_query(q["question"])
        if q.get("must_pass_unchanged") and fx["corrected"] != fx["original"]:
            problems.append(f"clean query was altered: {fx['corrected']!r}")
        corrected = fx["corrected"]
        if fx["method"] != "none":
            notes.append(f"fix[{fx['method']}]: {corrected!r}")
        expected_docs = set(q.get("expected_retrieve_docs_any", []))
        if expected_docs:
            got = {r["metadata"]["doc_id"] for r in retrieve(corrected)}
            if not (got & expected_docs):
                problems.append(f"retrieval missed {sorted(expected_docs)}")
        if q.get("expected_mentions") or q.get("forbidden_mentions"):
            result = answer(corrected)
            problems += _check_mentions(q, result["answer"])
        return problems

    # answerable / decision
    result = answer(q["question"])
    if result["status"] != "grounded":
        return [f"status={result['status']} (expected grounded): {result['answer'][:80]!r}"]
    if result.get("bank_hit"):
        notes.append("⚡bank")
    problems = _check_mentions(q, result["answer"])
    expected_docs = set(q.get("expected_cite_docs_any", []))
    if expected_docs and not (_cited_docs(result["citations"]) & expected_docs):
        problems.append(f"no citation from {sorted(expected_docs)}; cited={result['citations']}")
    return problems


def test_golden_set():
    qs = yaml.safe_load(config.GOLDEN_SET.read_text())["questions"]
    rows, failures = [], []

    for q in qs:
        notes: list[str] = []
        try:
            problems = _check(q, notes)
        except Exception as e:  # a crashed question is a failed question
            problems = [f"ERROR {type(e).__name__}: {e}"]
        rows.append((q["id"], q["type"], "PASS" if not problems else "FAIL",
                     "; ".join(problems + notes)[:110]))
        if problems:
            failures.append(f"{q['id']}: {'; '.join(problems)}")

    print("\n" + "=" * 110)
    print(f"{'id':<5} {'type':<11} {'result':<7} notes")
    print("-" * 110)
    for r in rows:
        print(f"{r[0]:<5} {r[1]:<11} {r[2]:<7} {r[3]}")
    passed = sum(1 for r in rows if r[2] == "PASS")
    print("-" * 110)
    print(f"{passed}/{len(rows)} passed")
    print("=" * 110)

    assert not failures, f"{len(failures)} golden failures:\n" + "\n".join(failures)
