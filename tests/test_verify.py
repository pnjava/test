"""Phase 6 acceptance (fast, no LLM):
  V1 fabricated citations caught (strip/reject machinery)
  V2 evidence-based confidence: HIGH >=2 docs, MEDIUM 1 doc multi-chunk,
     LOW single chunk or stale source
  V3 staleness note fires exactly for stale_risk docs (23-drafts-process)

Run: .venv/bin/python -m pytest tests/test_verify.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.answer import _extract_citations, _validate  # noqa: E402
from src.verify import confidence, staleness_note, stale_doc_ids, STALE_NOTE  # noqa: E402

RETRIEVED = ["06-dg-current-state-landscape#01", "06-dg-current-state-landscape#02",
             "11-webde#01", "23-drafts-process#01"]


def test_v1_fabricated_citation_detected():
    valid, invalid = _extract_citations(
        "DG is X [06-dg-current-state-landscape#01]. Also Y [99-made-up#01].", RETRIEVED)
    assert valid == ["06-dg-current-state-landscape#01"]
    assert invalid == ["99-made-up#01"]


def test_v1_uncited_answer_fails_validation():
    ok, cited, invalid, is_nk = _validate("DG runs UniVerse and Pick.", RETRIEVED)
    assert not ok and not cited


def test_v1_doc_level_citation_resolves():
    valid, invalid = _extract_citations("ID cards go via Axway [11-webde].", RETRIEVED)
    assert valid == ["11-webde#01"] and not invalid


def test_v2_confidence_high_two_docs():
    assert confidence(["06-dg-current-state-landscape#01", "11-webde#01"]) == "HIGH"


def test_v2_confidence_medium_one_doc_multichunk():
    assert confidence(["06-dg-current-state-landscape#01",
                       "06-dg-current-state-landscape#02"]) == "MEDIUM"


def test_v2_confidence_low_single_chunk():
    assert confidence(["11-webde#01"]) == "LOW"


def test_v2_confidence_low_when_stale():
    assert "23-drafts-process" in stale_doc_ids()
    assert confidence(["23-drafts-process#01", "22-benton-queues#01"]) == "LOW"


def test_v3_staleness_note():
    assert staleness_note(["23-drafts-process#01"]) == STALE_NOTE
    assert staleness_note(["11-webde#01"]) is None
