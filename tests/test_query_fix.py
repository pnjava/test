"""Phase 2 acceptance: the 5 golden typo/voice cases correct properly;
clean queries pass unchanged.

Run: .venv/bin/python -m pytest tests/test_query_fix.py -v -s
(g16/g17 may invoke one live Ollama call each for the LLM rewrite stage.)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.query_fix import fix_query  # noqa: E402

GARBLED_TOKENS = ["tele", "teh", "interctas", "vizualisation", "BAMER", "vison", "tablo"]


def test_g16_voice_transcription():
    r = fix_query("can you tele me teh systems DG interctas with?")
    c = r["corrected"].lower()
    assert r["corrected"] != r["original"], r
    assert "dg" in c
    assert "intercta" not in c and "teh " not in c, r
    print(f"  g16: {r['method']}: {r['corrected']!r}")


def test_g17_vizualisation():
    r = fix_query("DG vizualisation")
    c = r["corrected"].lower()
    assert "vizualisation" not in c, r
    assert "visual" in c or "datavision" in c or "analytics" in c, r
    print(f"  g17: {r['method']}: {r['corrected']!r}")


def test_g18_bamer():
    r = fix_query("wat is BAMER")
    assert "bamr" in r["corrected"].lower(), r
    print(f"  g18: {r['method']}: {r['corrected']!r}")


def test_g19_data_vison_tablo():
    r = fix_query("data vison tablo reports")
    c = r["corrected"].lower()
    assert "tableau" in c or "datavision" in c, r
    print(f"  g19: {r['method']}: {r['corrected']!r}")


def test_g20_clean_control_unchanged():
    r = fix_query("What is DataVision?")
    assert r["corrected"] == r["original"], r
    assert r["method"] == "none", r
    print(f"  g20: unchanged ✓")


def test_more_clean_queries_unchanged():
    for q in ["Which CDC approach was selected?",
              "How much repricing goes to BAMR?",
              "data platform strategy"]:
        r = fix_query(q)
        assert r["corrected"] == r["original"], f"clean query altered: {r}"
