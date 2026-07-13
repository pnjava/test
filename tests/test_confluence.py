"""Phase 8 acceptance: dry-run emits valid storage-format for all docs +
governance pages; one doc round-trips headings, table, image ref, labels.

Run: .venv/bin/python -m pytest tests/test_confluence.py -v
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src import wiki  # noqa: E402
from src.confluence_publish import dry_run, render_page, PREVIEW_DIR  # noqa: E402

NAMESPACE_WRAP = ('<root xmlns:ac="urn:x" xmlns:ri="urn:y">{}</root>')


def _parses(xhtml: str) -> bool:
    ET.fromstring(NAMESPACE_WRAP.format(xhtml))
    return True


def test_dry_run_emits_all_pages():
    out = dry_run()
    pages = list(out.glob("*.storage.xhtml"))
    docs = len(wiki.load_docs())
    assert len(pages) == docs + 1, f"{len(pages)} pages vs {docs} docs + gaps page"
    assert (out / "_hierarchy.yaml").exists()


def test_all_pages_are_valid_xml():
    bad = []
    for p in PREVIEW_DIR.glob("*.storage.xhtml"):
        try:
            _parses(p.read_text())
        except ET.ParseError as e:
            bad.append(f"{p.name}: {e}")
    assert not bad, "invalid storage XML:\n" + "\n".join(bad[:5])


def test_roundtrip_headings_table_image_labels():
    # image + headings + labels via doc 06 (the landscape)
    doc = wiki.get_doc("06-dg-current-state-landscape")
    page = render_page(doc)
    s = page["storage"]
    assert _parses(s)
    assert "<h1>" in s or "<h2>" in s, "no headings"
    assert 'ri:filename="page-19.png"' in s, "diagram attachment ref missing"
    assert any(l.startswith("state-") for l in page["labels"])
    assert any(l.startswith("confidence-") for l in page["labels"])
    assert any(l.startswith("tag-") for l in page["labels"])
    assert page["attachments"], "attachment list empty"

    # table round-trip via a doc that actually contains a markdown table
    table_doc = next(d for d in wiki.load_docs() if "\n|" in d["body"])
    ts = render_page(table_doc)["storage"]
    assert _parses(ts)
    assert "<table>" in ts and "<th>" in ts, f"table not rendered for {table_doc['doc_id']}"


def test_banners_are_macros_not_markdown():
    proposed = next(d for d in wiki.load_docs() if d["state"].lower().startswith("proposed"))
    s = render_page(proposed)["storage"]
    assert 'ac:name="warning"' in s
    sensitive = wiki.get_doc("05-plan-build-process")
    assert 'ac:name="warning"' in render_page(sensitive)["storage"]
