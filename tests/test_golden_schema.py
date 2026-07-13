"""Phase 0 acceptance: golden_set/questions.yaml schema validation (v3, 20 questions).

Run: .venv/bin/python -m pytest tests/test_golden_schema.py -v
"""

import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import config  # noqa: E402

VALID_TYPES = {"answerable", "decision", "unknown", "robustness"}


def load():
    return yaml.safe_load(config.GOLDEN_SET.read_text())


def test_file_exists_and_parses():
    data = load()
    assert isinstance(data, dict) and "questions" in data


def test_question_count_and_mix():
    qs = load()["questions"]
    assert len(qs) == 20
    by_type = {t: [q for q in qs if q["type"] == t] for t in VALID_TYPES}
    assert len(by_type["answerable"]) == 10
    assert len(by_type["decision"]) == 3
    assert len(by_type["unknown"]) == 2
    assert len(by_type["robustness"]) == 5


def test_ids_unique_and_wellformed():
    qs = load()["questions"]
    ids = [q["id"] for q in qs]
    assert len(ids) == len(set(ids))
    assert all(re.fullmatch(r"g\d{2}", i) for i in ids)


def test_required_fields_per_type():
    for q in load()["questions"]:
        assert q["type"] in VALID_TYPES, q["id"]
        assert q.get("question", "").strip(), q["id"]
        if q["type"] == "unknown":
            assert q.get("expected_answer") == "unknown", q["id"]
        elif q["type"] == "robustness":
            assert q.get("expected_retrieve_docs_any") or q.get("expected_mentions"), \
                f"{q['id']}: robustness needs a retrieval or mention expectation"
        else:
            assert q.get("expected_mentions"), f"{q['id']}: expected_mentions required"
            assert q.get("expected_cite_docs_any"), f"{q['id']}: expected_cite_docs_any required"


def test_exactly_one_unchanged_control():
    qs = load()["questions"]
    controls = [q for q in qs if q.get("must_pass_unchanged")]
    assert len(controls) == 1 and controls[0]["type"] == "robustness"


def test_referenced_docs_exist():
    """Every doc id referenced must be a markdown doc, register decision, or watchlist."""
    register = yaml.safe_load(config.CONTRADICTION_REGISTER.read_text())
    valid_ids = {f"{config.REGISTER_DOC_PREFIX}-{d['id'].lower()}" for d in register["decisions"]}
    valid_ids.add("watchlist-acronyms")
    valid_ids |= {p.stem for p in config.MARKDOWN_DIR.glob("*.md")}
    for q in load()["questions"]:
        for field in ("expected_cite_docs_any", "expected_retrieve_docs_any"):
            for doc in q.get(field, []):
                assert doc in valid_ids, f"{q['id']}: unknown doc id {doc!r} in {field}"
