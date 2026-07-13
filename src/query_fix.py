"""Query fixing (Phase 2): typo/voice-transcription robustness.

Stage 1 — rapidfuzz: correct query tokens against the KB vocabulary
(aliases.yaml canonicals + aliases + doc tags). Only tokens that are NOT
ordinary English words and NOT already vocabulary terms are eligible, so
clean queries pass through untouched ("data" never becomes "DataVision").

Stage 2 — LLM rewrite: if garbled tokens remain that Stage 1 could not
match, ONE Ollama call with the locked QUERY_REWRITE prompt (temperature 0).

Returns {original, corrected, method}; method in
none | fuzzy | llm | fuzzy+llm | llm-failed(<reason>).

CLI:
    python -m src.query_fix "wat is BAMER"
"""

import json
import re
import sys
import urllib.error
import urllib.request
from functools import lru_cache
from pathlib import Path

import yaml
from rapidfuzz import fuzz, process

from src import config
from src.prompts import QUERY_REWRITE

_WORDS_FILE = Path("/usr/share/dict/words")


@lru_cache(maxsize=1)
def _english() -> frozenset:
    if not _WORDS_FILE.exists():
        return frozenset()
    return frozenset(w.strip().lower() for w in _WORDS_FILE.read_text().splitlines())


@lru_cache(maxsize=1)
def vocabulary() -> tuple:
    """Canonical names + aliases + doc tags. Order stable for the prompt."""
    vocab: list[str] = []
    reg = yaml.safe_load(config.ALIASES_FILE.read_text())["aliases"]
    for entry in reg:
        vocab.append(str(entry["canonical"]))
        vocab.extend(str(a) for a in entry.get("aka", []))
    for p in sorted(config.MARKDOWN_DIR.glob("*.md")):
        parts = p.read_text(errors="replace").split("---")
        if len(parts) >= 3:
            for t in (yaml.safe_load(parts[1]).get("tags") or []):
                vocab.append(str(t))
    seen, out = set(), []
    for v in vocab:
        if v.lower() not in seen:
            seen.add(v.lower())
            out.append(v)
    return tuple(out)


def _is_clean(token: str) -> bool:
    """Token needs no correction: numeric, short, English word, or exact vocab."""
    tl = token.lower()
    if len(token) <= 2 or not token.isalpha():
        return True
    if tl in {v.lower() for v in vocabulary()}:
        return True
    return tl in _english() or tl.rstrip("s") in _english()


def _fuzzy_stage(query: str) -> tuple[str, bool, bool]:
    """Returns (corrected, changed, garble_remaining)."""
    tokens = re.findall(r"\w+|\W+", query)  # preserve separators
    changed = False
    garble = False
    vocab = vocabulary()
    for i, tok in enumerate(tokens):
        if not tok.strip() or not re.match(r"\w", tok) or _is_clean(tok):
            continue
        match = process.extractOne(tok, vocab, scorer=fuzz.WRatio,
                                   score_cutoff=config.FUZZY_THRESHOLD)
        if match:
            tokens[i] = match[0]
            changed = True
        else:
            garble = True
    return "".join(tokens), changed, garble


def _llm_stage(query: str) -> str:
    vocab_str = ", ".join(vocabulary())
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": QUERY_REWRITE.format(vocab=vocab_str)},
            {"role": "user", "content": query},
        ],
        "stream": False,
        "options": {"temperature": 0.0},
    }
    req = urllib.request.Request(
        f"{config.OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        out = json.loads(resp.read())["message"]["content"].strip()
    return out.splitlines()[0].strip().strip('"')


def fix_query(query: str) -> dict:
    corrected, fuzzy_changed, garble = _fuzzy_stage(query)
    method = "fuzzy" if fuzzy_changed else "none"

    if garble:
        try:
            llm_out = _llm_stage(corrected)
            if llm_out and llm_out.lower() != corrected.lower():
                corrected = llm_out
                method = "fuzzy+llm" if fuzzy_changed else "llm"
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            method += f"+llm-failed({type(e).__name__})"

    return {"original": query, "corrected": corrected, "method": method}


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    r = fix_query(" ".join(sys.argv[1:]))
    print(f"original : {r['original']}")
    print(f"corrected: {r['corrected']}")
    print(f"method   : {r['method']}")


if __name__ == "__main__":
    main()
