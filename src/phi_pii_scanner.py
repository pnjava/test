#!/usr/bin/env python3
"""
PHI/PII Scanner (T1.1)

Scans text files for PHI/PII patterns defined in phi_patterns.yaml.
Files with hits are moved to knowledge/quarantine/ and the reason is
appended to knowledge/quarantine/quarantine_log.yaml.

Usage:
    python3 phi_pii_scanner.py <file> [<file> ...]        # scan + quarantine on hit
    python3 phi_pii_scanner.py --dry-run <file> [...]     # report only, don't move

Exit codes: 0 = all files clean, 1 = one or more files quarantined/hit
"""

import re
import sys
import shutil
import yaml
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
PATTERNS_FILE = Path(__file__).parent / "phi_patterns.yaml"
QUARANTINE_DIR = ROOT / "knowledge" / "quarantine"
QUARANTINE_LOG = QUARANTINE_DIR / "quarantine_log.yaml"


def load_patterns():
    with open(PATTERNS_FILE) as f:
        config = yaml.safe_load(f)
    compiled = []
    for p in config["patterns"]:
        compiled.append(
            {
                "name": p["name"],
                "regex": re.compile(p["regex"]),
                "description": p["description"],
                "severity": p["severity"],
            }
        )
    return compiled


def mask(match_text):
    """Mask matched text so the quarantine log itself never stores raw PHI."""
    if len(match_text) <= 4:
        return "*" * len(match_text)
    return match_text[:2] + "*" * (len(match_text) - 4) + match_text[-2:]


def scan_text(text, patterns):
    """Return list of hits: {pattern, severity, line, masked_sample, count}."""
    hits = []
    for p in patterns:
        matches = []
        for line_no, line in enumerate(text.splitlines(), 1):
            for m in p["regex"].finditer(line):
                matches.append((line_no, mask(m.group())))
        if matches:
            hits.append(
                {
                    "pattern": p["name"],
                    "description": p["description"],
                    "severity": p["severity"],
                    "count": len(matches),
                    "first_line": matches[0][0],
                    "masked_samples": [s for _, s in matches[:3]],
                }
            )
    return hits


def quarantine_file(filepath, hits):
    """Move file to quarantine dir and append reason to the log."""
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    dest = QUARANTINE_DIR / filepath.name
    shutil.move(str(filepath), str(dest))

    log_entries = []
    if QUARANTINE_LOG.exists():
        with open(QUARANTINE_LOG) as f:
            log_entries = yaml.safe_load(f) or []

    log_entries.append(
        {
            "filename": filepath.name,
            "original_path": str(filepath),
            "quarantined_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "hits": hits,
        }
    )
    with open(QUARANTINE_LOG, "w") as f:
        yaml.safe_dump(log_entries, f, sort_keys=False)
    return dest


def scan_file(filepath, patterns, dry_run=False):
    """Scan one file. Returns True if clean, False if hits found."""
    filepath = Path(filepath)
    try:
        text = filepath.read_text(errors="replace")
    except Exception as e:
        print(f"  ERROR reading {filepath}: {e} — treating as quarantine candidate")
        return False

    hits = scan_text(text, patterns)
    if not hits:
        print(f"✓ CLEAN: {filepath.name}")
        return True

    print(f"✗ PHI/PII DETECTED: {filepath.name}")
    for h in hits:
        print(
            f"    [{h['severity']}] {h['pattern']} ×{h['count']} "
            f"(first at line {h['first_line']}): {', '.join(h['masked_samples'])}"
        )
    if dry_run:
        print("    (dry-run: file NOT moved)")
    else:
        dest = quarantine_file(filepath, hits)
        print(f"    → moved to {dest.relative_to(ROOT)}")
        print(f"    → reason logged in {QUARANTINE_LOG.relative_to(ROOT)}")
    return False


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    files = [a for a in args if not a.startswith("--")]
    if not files:
        print(__doc__)
        sys.exit(2)

    patterns = load_patterns()
    all_clean = True
    for f in files:
        if not scan_file(f, patterns, dry_run=dry_run):
            all_clean = False
    sys.exit(0 if all_clean else 1)


if __name__ == "__main__":
    main()
