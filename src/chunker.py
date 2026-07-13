#!/usr/bin/env python3
"""
Chunker (T3.1)

Splits knowledge/markdown/*.md into 150-400 word self-contained chunks.
Every chunk carries:
  - the file's YAML frontmatter metadata
  - a source pointer (file + heading path + chunk sequence)
  - canonical system names mentioned (resolved via CONFIRMED aliases only)

Output: knowledge/chunks.jsonl (one JSON object per line) — input for T3.2.

Strategy:
  1. Split body at heading boundaries (#, ##, ###) — sections stay coherent.
  2. Pack adjacent small sections (same parent heading) up to MAX_WORDS.
  3. Split oversize sections at paragraph, then sentence boundaries.
  4. Prefix every chunk with its heading breadcrumb so it is self-contained.

Usage:
    python3 chunker.py            # chunk all of knowledge/markdown/
    python3 chunker.py <file.md>  # chunk specific file(s), print to stdout
"""

import json
import re
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
MARKDOWN_DIR = ROOT / "knowledge" / "markdown"
ALIASES = ROOT / "knowledge" / "aliases.yaml"
OUT_FILE = ROOT / "knowledge" / "chunks.jsonl"

MIN_WORDS = 150
MAX_WORDS = 400


def word_count(text):
    return len(text.split())


def load_confirmed_aliases():
    """canonical -> [all name variants], confirmed entries only."""
    reg = yaml.safe_load(open(ALIASES))
    lookup = {}
    for s in reg.get("systems", []):
        if s["status"] != "confirmed":
            continue
        names = [s["canonical_name"]] + s.get("aliases", [])
        lookup[s["canonical_name"]] = names
    return lookup


def systems_in(text, alias_lookup):
    """Canonical names of confirmed systems mentioned in text."""
    found = []
    for canonical, names in alias_lookup.items():
        for n in names:
            # word-boundary match; short all-caps names must match exactly
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(n)}(?![A-Za-z0-9])", text):
                found.append(canonical)
                break
    return sorted(found)


def parse_frontmatter(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return yaml.safe_load(parts[1]) or {}, parts[2]
    return {}, text


def split_sections(body):
    """Yield (heading_path, text) per heading-delimited section."""
    lines = body.splitlines()
    sections = []
    path = []  # [(level, title)]
    buf = []

    def flush():
        text = "\n".join(buf).strip()
        if text:
            sections.append((" > ".join(t for _, t in path), text))
        buf.clear()

    for line in lines:
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            flush()
            level = len(m.group(1))
            title = m.group(2).strip()
            while path and path[-1][0] >= level:
                path.pop()
            path.append((level, title))
        else:
            buf.append(line)
    flush()
    return sections


def split_oversize(text, limit):
    """Split text into pieces <= limit words: paragraphs first, sentences if needed."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces, current = [], []

    def flush():
        if current:
            pieces.append("\n\n".join(current))
            current.clear()

    for p in paras:
        if word_count(p) > limit:
            flush()
            # sentence-level hard split
            sentences = re.split(r"(?<=[.!?])\s+", p)
            acc = []
            for s in sentences:
                if word_count(" ".join(acc + [s])) > limit and acc:
                    pieces.append(" ".join(acc))
                    acc = [s]
                else:
                    acc.append(s)
            if acc:
                pieces.append(" ".join(acc))
        elif word_count("\n\n".join(current + [p])) > limit:
            flush()
            current.append(p)
        else:
            current.append(p)
    flush()
    return pieces


def chunk_file(path, alias_lookup):
    raw = Path(path).read_text(errors="replace")
    fm, body = parse_frontmatter(raw)
    source_file = fm.get("source_file", Path(path).name)
    kb_file = str(Path(path).relative_to(ROOT)) if str(path).startswith(str(ROOT)) else str(path)

    sections = split_sections(body)

    # Pack small adjacent sections; split big ones
    packed = []  # (heading_path, text)
    for heading, text in sections:
        if word_count(text) > MAX_WORDS:
            for i, piece in enumerate(split_oversize(text, MAX_WORDS), 1):
                packed.append((f"{heading} (part {i})" if heading else f"(part {i})", piece))
        elif (packed
              and word_count(packed[-1][1]) + word_count(text) <= MAX_WORDS
              and word_count(packed[-1][1]) < MIN_WORDS):
            prev_h, prev_t = packed[-1]
            joined_h = prev_h if heading.startswith(prev_h.split(" (part")[0]) or not heading else f"{prev_h} | {heading}"
            packed[-1] = (joined_h, prev_t + f"\n\n[{heading}]\n" + text if heading else prev_t + "\n\n" + text)
        else:
            packed.append((heading, text))

    chunks = []
    stem = Path(path).stem
    for i, (heading, text) in enumerate(packed, 1):
        breadcrumb = f"[Source: {source_file}" + (f" — {heading}]" if heading else "]")
        chunk_text = breadcrumb + "\n" + text
        # Breadcrumb may nudge over the limit — trim by sentence if so
        if word_count(chunk_text) > MAX_WORDS:
            words = chunk_text.split()
            chunk_text = " ".join(words[:MAX_WORDS])
        chunks.append(
            {
                "chunk_id": f"{stem}::c{i:03d}",
                "text": chunk_text,
                "words": word_count(chunk_text),
                "source_pointer": {
                    "kb_file": kb_file,
                    "source_file": source_file,
                    "heading": heading or "(document root)",
                    "sequence": i,
                },
                "metadata": {
                    "date": str(fm.get("date", "")),
                    "state": fm.get("state", "unknown"),
                    "owner": fm.get("owner", "TBD"),
                    "category": fm.get("category", ""),
                    "confidence": fm.get("confidence", "assumed"),
                    "tags": fm.get("tags", []),
                    "review_status": fm.get("review_status", ""),
                },
                "systems": systems_in(text, alias_lookup),
            }
        )
    return chunks


def main():
    args = sys.argv[1:]
    alias_lookup = load_confirmed_aliases()
    files = [Path(a) for a in args] if args else sorted(MARKDOWN_DIR.glob("*.md"))

    all_chunks = []
    for f in files:
        chunks = chunk_file(f, alias_lookup)
        all_chunks.extend(chunks)
        sizes = [c["words"] for c in chunks]
        print(f"✓ {f.name}: {len(chunks)} chunks (words min {min(sizes)} / max {max(sizes)})")

    if not args:
        with open(OUT_FILE, "w") as out:
            for c in all_chunks:
                out.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(f"\n{len(all_chunks)} chunks written to {OUT_FILE.relative_to(ROOT)}")

    oversize = [c for c in all_chunks if c["words"] > MAX_WORDS]
    missing_ptr = [c for c in all_chunks if not c["source_pointer"]["kb_file"] or not c["source_pointer"]["source_file"]]
    if oversize or missing_ptr:
        print(f"✗ VIOLATIONS: {len(oversize)} oversize, {len(missing_ptr)} missing source pointer")
        sys.exit(1)
    print("✓ All chunks ≤400 words, all carry source pointers")


if __name__ == "__main__":
    main()
