"""Wiki data layer (Phase 7): Confluence-style pages generated from kb/ at
render time. Nothing hand-written — delete + regenerate = identical.

Provides doc models for app.py to render:
  {doc_id, title, group, state, confidence, source, tags, body, images,
   sensitive, related_docs, related_gaps}

Groups: Home (doc 00) / Current State / Target State / Governance.
Doc 26 (lucidchart template) is skipped per spec.
"""

import re
from functools import lru_cache
from pathlib import Path

import yaml

from src import config

SKIP_DOCS = {"26-lucidchart-template"}


def _group(state: str, doc_id: str) -> str:
    if doc_id.startswith("00-"):
        return "Home"
    s = (state or "").lower()
    if s.startswith("proposed"):
        return "Target State"
    if s.startswith(("register", "governance")):
        return "Governance"
    return "Current State"


@lru_cache(maxsize=1)
def _image_map() -> dict:
    if config.IMAGE_MAP.exists():
        return yaml.safe_load(config.IMAGE_MAP.read_text()).get("mappings", {})
    return {}


@lru_cache(maxsize=1)
def _sensitive_docs() -> set:
    """Docs flagged in image-map.yaml comments or frontmatter as internal."""
    sensitive = set()
    if config.IMAGE_MAP.exists():
        for line in config.IMAGE_MAP.read_text().splitlines():
            if "SENSITIVITY" in line.upper() and ":" in line:
                m = re.match(r"\s*([0-9a-z-]+):", line)
                if m:
                    sensitive.add(m.group(1))
    sensitive.add("05-plan-build-process")  # spec: danger banner — employee names
    return sensitive


def _parse(path: Path) -> dict | None:
    text = path.read_text(errors="replace")
    fm, body = {}, text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            fm, body = yaml.safe_load(parts[1]) or {}, parts[2]
    doc_id = fm.get("id", path.stem)
    if doc_id in SKIP_DOCS:
        return None
    title_m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    state = str(fm.get("state", "unknown"))
    images = [config.ASSETS_DIR / img for img in _image_map().get(doc_id, [])]
    return {
        "doc_id": doc_id,
        "title": title_m.group(1).strip() if title_m else doc_id,
        "group": _group(state, doc_id),
        "state": state,
        "confidence": str(fm.get("confidence", "unknown")),
        "source": str(fm.get("source", "")),
        "tags": [str(t) for t in fm.get("tags", [])],
        "body": body.strip(),
        "images": [p for p in images if p.exists()],
        "sensitive": doc_id in _sensitive_docs(),
    }


@lru_cache(maxsize=1)
def load_docs() -> tuple:
    docs = []
    for p in sorted(config.MARKDOWN_DIR.glob("*.md")):
        d = _parse(p)
        if d:
            docs.append(d)
    # governance registries rendered as wiki pages too
    for p, title in ((config.KB_DIR / "sme-questions.md", "Open SME Questions"),
                     (config.EXTRACTION_NOTES, "Extraction Notes & Watchlist")):
        if p.exists():
            docs.append({
                "doc_id": p.stem, "title": title, "group": "Governance",
                "state": "governance", "confidence": "verified",
                "source": p.name, "tags": ["governance"],
                "body": p.read_text(errors="replace"),
                "images": [], "sensitive": False,
            })
    return tuple(docs)  # tuple: lru_cache-friendly


def doc_ids() -> list[str]:
    return [d["doc_id"] for d in load_docs()]


def get_doc(doc_id: str) -> dict | None:
    for d in load_docs():
        if d["doc_id"] == doc_id:
            return d
    return None


def cross_links(doc: dict) -> list[str]:
    """Other doc ids referenced in this doc's body, plus alias-name hits."""
    body = doc["body"]
    links = {d for d in doc_ids() if d != doc["doc_id"] and d in body}
    try:
        aliases = yaml.safe_load(config.ALIASES_FILE.read_text())["aliases"]
        for entry in aliases:
            names = [entry["canonical"]] + [str(a) for a in entry.get("aka", [])]
            if any(re.search(rf"(?<![A-Za-z0-9]){re.escape(n)}(?![A-Za-z0-9])", body) for n in names):
                # link to docs whose tags mention the canonical name
                for d in load_docs():
                    if d["doc_id"] != doc["doc_id"] and entry["canonical"].lower() in ",".join(d["tags"]).lower():
                        links.add(d["doc_id"])
    except Exception:
        pass
    return sorted(links)


def related_gaps(doc: dict) -> list[dict]:
    """Open gaps whose retrieved docs or question text touch this doc."""
    if not config.GAPS_FILE.exists():
        return []
    gaps = (yaml.safe_load(config.GAPS_FILE.read_text()) or {}).get("gaps", [])
    out = []
    for g in gaps:
        if g.get("status") != "open":
            continue
        gap_docs = {c.split("#")[0] for c in g.get("retrieved_ids", [])}
        if doc["doc_id"] in gap_docs or any(
                t and t.lower() in g["question"].lower() for t in doc["tags"][:4]):
            out.append(g)
    return out


def search(query: str) -> list[dict]:
    q = query.lower()
    return [d for d in load_docs()
            if q in d["doc_id"].lower() or q in d["title"].lower()
            or q in ",".join(d["tags"]).lower() or q in d["body"].lower()]
