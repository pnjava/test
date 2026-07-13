#!/usr/bin/env python3
"""
Alias Scanner (T2.1)

Scans knowledge Markdown files for system-name candidates that are NOT in
knowledge/aliases.yaml and for definitional patterns suggesting two names
refer to the same system.

Output goes to knowledge/aliases_pending.yaml for HUMAN review.
This script NEVER modifies aliases.yaml — no auto-merging, by design.

Usage:
    python3 alias_scanner.py <file.md> [<file.md> ...]
    python3 alias_scanner.py --all          # scan all of knowledge/markdown/
"""

import re
import sys
import yaml
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
REGISTRY = ROOT / "knowledge" / "aliases.yaml"
PENDING = ROOT / "knowledge" / "aliases_pending.yaml"
MARKDOWN_DIR = ROOT / "knowledge" / "markdown"

# Candidate detectors
ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,7}\b")
CAMELCASE_RE = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][A-Za-z]+)+\b")

# Definitional patterns: (name_a, name_b) both captured; suggests same system.
# Names here may be acronyms, CamelCase words, or short Title Case phrases
# ending in a system-ish noun (database/DB/system/platform/app/tool).
NAME = r"[A-Z][A-Za-z0-9/&.-]*(?:\s+[A-Za-z0-9/&.-]+){0,3}"
DEFINITIONAL_PATTERNS = [
    # "DG is UniVerse DB", "X is the Y database"
    re.compile(
        rf"\b(?P<a>{NAME}?)\s+is\s+(?:the\s+|an?\s+)?(?P<b>{NAME}\s*(?:database|DB|system|platform|application|app|tool))",
        re.IGNORECASE,
    ),
    # "X a.k.a Y" / "X aka Y" / "X also known as Y"
    re.compile(rf"\b(?P<a>{NAME}?)\s+(?:a\.?k\.?a\.?|also known as)\s+(?P<b>{NAME})", re.IGNORECASE),
    # "IPP (Intelligent Preference Platform)" — acronym followed by Title Case expansion
    re.compile(r"\b(?P<a>[A-Z][A-Z0-9]{1,7})\s+\((?P<b>[A-Z][A-Za-z]+(?:\s+[A-Za-z][a-z]+){1,5})\)"),
]


def load_registry():
    with open(REGISTRY) as f:
        reg = yaml.safe_load(f)
    known = set()
    for s in reg.get("systems", []):
        known.add(s["canonical_name"].lower())
        for a in s.get("aliases", []):
            known.add(a.lower())
    ignore = {w.lower() for w in reg.get("scanner_ignore", [])}
    canonical_lookup = {s["canonical_name"].lower(): s["canonical_name"] for s in reg.get("systems", [])}
    for s in reg.get("systems", []):
        for a in s.get("aliases", []):
            canonical_lookup[a.lower()] = s["canonical_name"]
    return known, ignore, canonical_lookup


def normalize(name):
    return re.sub(r"\s+", " ", name.strip())


def is_known(name, known, ignore):
    n = name.lower().strip()
    return n in known or n in ignore


def strip_body(text):
    """Remove YAML frontmatter and fenced code blocks (SQL schemas etc.)
    so scanning only sees prose content."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            text = parts[2]
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def load_dictionary():
    """Common-English filter for ALL-CAPS noise (e.g. 'ANSWER', 'BEFORE').
    Uses the system word list when present; harmless no-op otherwise."""
    words_file = Path("/usr/share/dict/words")
    if not words_file.exists():
        return frozenset()
    return frozenset(w.strip().lower() for w in words_file.read_text().splitlines() if len(w.strip()) >= 2)


ENGLISH_WORDS = load_dictionary()


LETTER_DIGIT_RE = re.compile(r"^[A-Z]{1,2}\d+$")  # Q1, P9, S3, PI80 — enumeration/hw fragments


def is_english_noise(cand):
    """True for pure-alpha ALL-CAPS tokens that are ordinary English words
    (including simple plural/past/gerund forms)."""
    if not (cand.isalpha() and cand.isupper()):
        return False
    w = cand.lower()
    forms = [w, w.rstrip("s"), w[:-2] if w.endswith(("ed", "es")) else w,
             w[:-3] if w.endswith("ing") else w]
    return any(f in ENGLISH_WORDS for f in forms)


def scan_file(path, known, ignore, canonical_lookup):
    text = strip_body(Path(path).read_text(errors="replace"))
    lines = text.splitlines()

    new_names = {}       # candidate -> {count, sample_context, first_file}
    merge_suggestions = {}  # (canonical, candidate) -> context

    for line_no, line in enumerate(lines, 1):
        # --- new-name candidates ---
        for rx in (ACRONYM_RE, CAMELCASE_RE):
            for m in rx.finditer(line):
                cand = normalize(m.group())
                if is_known(cand, known, ignore):
                    continue
                if len(cand) < 2 or is_english_noise(cand) or LETTER_DIGIT_RE.match(cand):
                    continue
                entry = new_names.setdefault(
                    cand, {"count": 0, "context": line.strip()[:160], "line": line_no}
                )
                entry["count"] += 1

        # --- merge suggestions from definitional patterns ---
        for rx in DEFINITIONAL_PATTERNS:
            for m in rx.finditer(line):
                a, b = normalize(m.group("a")), normalize(m.group("b"))
                a_known, b_known = a.lower() in canonical_lookup, b.lower() in canonical_lookup
                # Suggest only when exactly one side is already in the registry:
                # the unknown side is a candidate alias for the known side.
                if a_known == b_known:
                    continue
                canonical = canonical_lookup[a.lower()] if a_known else canonical_lookup[b.lower()]
                candidate = b if a_known else a
                if is_known(candidate, known, ignore):
                    continue
                key = (canonical, candidate.lower())
                if key not in merge_suggestions:
                    merge_suggestions[key] = {
                        "canonical": canonical,
                        "candidate_alias": candidate,
                        "context": line.strip()[:200],
                        "file": str(path),
                        "line": line_no,
                    }

    return new_names, merge_suggestions


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    files = sorted(MARKDOWN_DIR.glob("*.md")) if args[0] == "--all" else [Path(a) for a in args]

    known, ignore, canonical_lookup = load_registry()

    all_new = {}
    all_merges = {}
    for f in files:
        new_names, merges = scan_file(f, known, ignore, canonical_lookup)
        for cand, info in new_names.items():
            agg = all_new.setdefault(cand, {**info, "files": []})
            agg["count"] = agg.get("count", 0) if cand in all_new else 0
            agg["files"].append(f.name)
        for key, sug in merges.items():
            all_merges.setdefault(key, sug)

    report = {
        "scanned_on": date.today().isoformat(),
        "scanned_files": [f.name for f in files],
        "status": "pending_human_review",
        "note": "NOTHING here has been merged into aliases.yaml. Review each item; move confirmed ones into the registry manually.",
        "new_name_candidates": [
            {"name": cand, "files": sorted(set(info["files"])), "sample_context": info["context"]}
            for cand, info in sorted(all_new.items())
        ],
        "merge_suggestions": [
            {
                "canonical": s["canonical"],
                "candidate_alias": s["candidate_alias"],
                "evidence": s["context"],
                "file": s["file"],
                "line": s["line"],
                "status": "pending",
            }
            for s in all_merges.values()
        ],
    }
    with open(PENDING, "w") as f:
        yaml.safe_dump(report, f, sort_keys=False, width=120)

    print(f"Scanned {len(files)} file(s).")
    print(f"  New name candidates : {len(report['new_name_candidates'])}")
    print(f"  Merge suggestions   : {len(report['merge_suggestions'])} (all pending — nothing auto-merged)")
    for s in report["merge_suggestions"]:
        print(f"    ? {s['canonical']}  <->  {s['candidate_alias']}   [{s['evidence'][:80]}]")
    print(f"Report written to {PENDING.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
