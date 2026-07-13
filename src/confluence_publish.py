"""Confluence publisher (Phase 8). Build now, RUN ON APPROVAL.

Markdown + frontmatter stays the single source of truth. Docs are converted
to Confluence storage-format XHTML at publish time; banners become
Confluence info/warning macros (never written into the markdown).

Hierarchy: Space -> "Meritain EAIP" -> Current State / Target State /
Governance / Knowledge Gaps -> doc pages. Create-or-update by title
(idempotent; page ids cached in confluence-pages.yaml). Diagrams uploaded
as attachments and referenced via <ac:image><ri:attachment/>.
Frontmatter -> labels (state-*, confidence-*, tag-*, sme-* on gaps).

Config via env: CONFLUENCE_BASE_URL, CONFLUENCE_SPACE_KEY,
CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN.

CLI:
    python -m src.confluence_publish            # DRY RUN (default) -> build/confluence-preview/
    python -m src.confluence_publish --publish  # real REST calls (needs env config)
"""

import html
import os
import re
import sys
from pathlib import Path

import yaml

from src import config, wiki

PREVIEW_DIR = config.ROOT / "build" / "confluence-preview"
PAGE_IDS = config.ROOT / "confluence-pages.yaml"

_MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITAL = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_CODE = re.compile(r"`([^`]+)`")


def _md_table_to_xhtml(lines: list[str]) -> str:
    rows = [ln for ln in lines if ln.strip().startswith("|")]
    out = ["<table><tbody>"]
    for i, row in enumerate(rows):
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue  # separator row
        tag = "th" if i == 0 else "td"
        out.append("<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITAL.sub(r"<em>\1</em>", text)
    text = _CODE.sub(r"<code>\1</code>", text)
    text = _MD_LINK.sub(r'<a href="\2">\1</a>', text)
    return text


def md_to_storage(body: str) -> str:
    """Markdown -> Confluence storage-format XHTML. Only Confluence-compatible
    constructs are emitted: headings, paragraphs, lists, tables, code blocks."""
    out: list[str] = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            code: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            out.append('<ac:structured-macro ac:name="code"><ac:plain-text-body>'
                       f"<![CDATA[{chr(10).join(code)}]]></ac:plain-text-body></ac:structured-macro>")
        elif ln.strip().startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            out.append(_md_table_to_xhtml(tbl))
            continue
        elif m := re.match(r"^(#{1,4})\s+(.*)$", ln):
            out.append(f"<h{len(m.group(1))}>{_inline(m.group(2))}</h{len(m.group(1))}>")
        elif ln.strip().startswith(("- ", "* ")):
            items = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                items.append(f"<li>{_inline(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif ln.strip():
            out.append(f"<p>{_inline(ln.strip())}</p>")
        i += 1
    return "\n".join(out)


def _banner(doc: dict) -> str:
    if doc["sensitive"]:
        return ('<ac:structured-macro ac:name="warning"><ac:rich-text-body>'
                "<p><strong>INTERNAL</strong> — contains employee names/screenshots. "
                "Do not distribute.</p></ac:rich-text-body></ac:structured-macro>")
    if doc["state"].lower().startswith("proposed"):
        return ('<ac:structured-macro ac:name="warning"><ac:rich-text-body>'
                "<p><strong>PROPOSED</strong> — target architecture, not implemented.</p>"
                "</ac:rich-text-body></ac:structured-macro>")
    return ('<ac:structured-macro ac:name="info"><ac:rich-text-body>'
            f"<p>state: {html.escape(doc['state'])} · confidence: {html.escape(doc['confidence'])}"
            f" · source: {html.escape(doc['source'])}</p></ac:rich-text-body></ac:structured-macro>")


def _images_block(doc: dict) -> str:
    return "\n".join(
        f'<ac:image ac:width="900"><ri:attachment ri:filename="{img.name}"/></ac:image>'
        for img in doc["images"])


def labels_for(doc: dict) -> list[str]:
    state_slug = re.sub(r"[^a-z0-9]+", "-", doc["state"].lower()).strip("-")[:40]
    conf_slug = re.sub(r"[^a-z0-9]+", "-", doc["confidence"].lower()).strip("-")[:40]
    labels = [f"state-{state_slug}", f"confidence-{conf_slug}"]
    labels += [f"tag-{re.sub(r'[^a-z0-9]+', '-', str(t).lower()).strip('-')[:40]}" for t in doc["tags"][:8]]
    return labels


def render_page(doc: dict) -> dict:
    """One doc -> {title, group, storage_xhtml, labels, attachments}."""
    storage = _banner(doc) + "\n" + _images_block(doc) + "\n" + md_to_storage(doc["body"])
    return {
        "title": doc["title"][:250],
        "group": doc["group"] if doc["group"] != "Home" else "Current State",
        "storage": storage,
        "labels": labels_for(doc),
        "attachments": [str(p) for p in doc["images"]],
    }


def render_gaps_page() -> dict:
    gaps = []
    if config.GAPS_FILE.exists():
        gaps = (yaml.safe_load(config.GAPS_FILE.read_text()) or {}).get("gaps", [])
    rows = ["| id | status | suggested SME | question |", "|---|---|---|---|"]
    rows += [f"| {g['id']} | {g['status']} | {g.get('suggested_sme', 'TBD')} | {g['question']} |"
             for g in gaps]
    return {
        "title": "Knowledge Gaps",
        "group": "Knowledge Gaps",
        "storage": md_to_storage("\n".join(rows)),
        "labels": ["knowledge-gaps"] + sorted({
            f"sme-{re.sub(r'[^a-z0-9]+', '-', str(g.get('suggested_sme', 'tbd')).lower()).strip('-')[:40]}"
            for g in gaps if g.get("status") == "open"}),
        "attachments": [],
    }


def dry_run() -> Path:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    pages = [render_page(d) for d in wiki.load_docs()] + [render_gaps_page()]
    for p in pages:
        slug = re.sub(r"[^a-z0-9]+", "-", p["title"].lower()).strip("-")[:60]
        (PREVIEW_DIR / f"{slug}.storage.xhtml").write_text(p["storage"])
        (PREVIEW_DIR / f"{slug}.meta.yaml").write_text(
            yaml.safe_dump({k: p[k] for k in ("title", "group", "labels", "attachments")},
                           sort_keys=False, allow_unicode=True))
    index = {"space": os.environ.get("CONFLUENCE_SPACE_KEY", "(unset)"),
             "root": "Meritain EAIP",
             "groups": sorted({p["group"] for p in pages}),
             "pages": [p["title"] for p in pages]}
    (PREVIEW_DIR / "_hierarchy.yaml").write_text(yaml.safe_dump(index, sort_keys=False, allow_unicode=True))
    print(f"✓ dry-run: {len(pages)} pages -> {PREVIEW_DIR.relative_to(config.ROOT)}")
    return PREVIEW_DIR


def publish() -> None:
    import requests

    base = os.environ.get("CONFLUENCE_BASE_URL")
    space = os.environ.get("CONFLUENCE_SPACE_KEY")
    email = os.environ.get("CONFLUENCE_EMAIL")
    token = os.environ.get("CONFLUENCE_API_TOKEN")
    if not all((base, space, email, token)):
        sys.exit("CONFLUENCE_BASE_URL/SPACE_KEY/EMAIL/API_TOKEN must be set — aborting.")
    auth = (email, token)
    ids = yaml.safe_load(PAGE_IDS.read_text()) if PAGE_IDS.exists() else {}
    ids = ids or {}

    def upsert(title: str, storage: str, parent_id: str | None, labels: list[str]) -> str:
        page_id = ids.get(title)
        payload = {"type": "page", "title": title, "space": {"key": space},
                   "body": {"storage": {"value": storage, "representation": "storage"}}}
        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]
        if page_id:
            cur = requests.get(f"{base}/rest/api/content/{page_id}", auth=auth,
                               params={"expand": "version"}).json()
            payload["version"] = {"number": cur["version"]["number"] + 1}
            r = requests.put(f"{base}/rest/api/content/{page_id}", json=payload, auth=auth)
        else:
            r = requests.post(f"{base}/rest/api/content", json=payload, auth=auth)
        r.raise_for_status()
        pid = r.json()["id"]
        ids[title] = pid
        if labels:
            requests.post(f"{base}/rest/api/content/{pid}/label",
                          json=[{"name": l} for l in labels], auth=auth)
        return pid

    root = upsert("Meritain EAIP", "<p>Generated by EAIP — do not edit by hand.</p>", None, [])
    group_ids = {}
    pages = [render_page(d) for d in wiki.load_docs()] + [render_gaps_page()]
    for group in sorted({p["group"] for p in pages}):
        group_ids[group] = upsert(group, "<p/>", root, [])
    for p in pages:
        pid = upsert(p["title"], p["storage"], group_ids[p["group"]], p["labels"])
        for att in p["attachments"]:
            with open(att, "rb") as f:
                requests.post(f"{base}/rest/api/content/{pid}/child/attachment",
                              files={"file": f}, headers={"X-Atlassian-Token": "nocheck"}, auth=auth)
    PAGE_IDS.write_text(yaml.safe_dump(ids, sort_keys=False))
    print(f"✓ published {len(pages)} pages under 'Meritain EAIP' in space {space}")


if __name__ == "__main__":
    if "--publish" in sys.argv:
        publish()
    else:
        dry_run()
