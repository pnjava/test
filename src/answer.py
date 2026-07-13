"""Grounded answering (M3): retrieve -> locked prompt -> Ollama -> validated answer.

Returns {answer, citations, gaps, retrieved_ids, status}.
status: grounded | not_in_kb | rejected | ollama_down

Contract enforced in code (not just prompt):
  - every [citation] must be a retrieved chunk id (one retry, then rejected)
  - rejected answers degrade to "Not in knowledge base." — never to fabrication
  - Ollama unreachable -> extractive fallback: top-3 chunks verbatim, cited

CLI:
    python -m src.answer "your question"
"""

import json
import re
import sys
import urllib.error
import urllib.request

from src import config
from src.prompts import (ANSWER_SYSTEM, ANSWER_USER_TEMPLATE, CHUNK_TEMPLATE,
                         RETRY_SUFFIX, GENERAL_SYSTEM, CHITCHAT_SYSTEM,
                         ENUM_EXTRACT)
from src.retrieve import retrieve

BRACKET_RE = re.compile(r"\[([A-Za-z0-9#,\s-]+)\]")
NOT_IN_KB = "Not in knowledge base."


def _extract_citations(text: str, retrieved_ids: list[str]) -> tuple[list[str], list[str]]:
    """Parse [..] citations, tolerating model variants:
    comma-separated lists, doc-level ids (no #nn -> resolved to a retrieved
    chunk of that doc), and 1-digit suffixes (#1 -> #01).
    Returns (valid_normalized_ids, invalid_tokens)."""
    by_doc: dict[str, list[str]] = {}
    for cid in retrieved_ids:
        by_doc.setdefault(cid.split("#")[0], []).append(cid)

    valid, invalid = [], []
    for bracket in BRACKET_RE.findall(text):
        for token in (t.strip() for t in bracket.split(",")):
            if not token or token.isdigit():
                continue
            if "#" in token:
                doc, _, num = token.partition("#")
                if num.isdigit():
                    token = f"{doc}#{int(num):02d}"
            if token in retrieved_ids:
                valid.append(token)
            elif token in by_doc:                      # doc-level citation
                valid.append(by_doc[token][0])
            elif re.fullmatch(r"(?:[A-Za-z0-9-]+#\d{2})|(?:register-[a-z0-9-]+)", token):
                invalid.append(token)                  # citation-shaped but not retrieved
            # anything else (prose in brackets) is ignored, not a citation
    return sorted(set(valid)), sorted(set(invalid))


def _render_chunks(results: list[dict]) -> str:
    # Render least->most important, GROUPED BY DOCUMENT, so the top document
    # arrives whole and adjacent to the question. Small models lose evidence
    # far from the generation point — observed three times: watchlist at rank
    # 1/12 ignored; forced register chunks ignored after naive reversal;
    # doc-06 sibling chunks (holding 4 of 6 enumeration answers) ignored when
    # rendered first. Doc importance = best rank of its chunks (forced beats
    # everything); chunks within a doc render in natural order.
    importance: dict[str, float] = {}
    by_doc: dict[str, list[dict]] = {}
    for rank, r in enumerate(results):
        doc = r["metadata"]["doc_id"]
        by_doc.setdefault(doc, []).append(r)
        score = -1.0 if r.get("forced") else float(rank)  # forced = most important
        importance[doc] = min(importance.get(doc, 1e9), score)
    docs_least_first = sorted(by_doc, key=lambda d: -importance[d])
    ordered: list[dict] = []
    for doc in docs_least_first:
        ordered.extend(sorted(by_doc[doc], key=lambda r: r["chunk_id"]))
    results = ordered
    return "\n\n".join(
        CHUNK_TEMPLATE.format(
            chunk_id=r["chunk_id"],
            state=r["metadata"].get("state", "unknown"),
            confidence=r["metadata"].get("confidence", "unknown"),
            source=r["metadata"].get("source", ""),
            text=r["text"],
        )
        for r in results
    )


def _call_ollama(system: str, user: str) -> str:
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        # 16k ctx: sibling expansion can produce 15+ chunks; 8k truncated the
        # tail (forced register/watchlist chunks). num_predict caps runaway
        # generation — small models can loop indefinitely on enumeration
        # questions at temperature 0 (observed: retry call exceeding 300s).
        "options": {"temperature": 0.0, "num_ctx": 16384, "num_predict": 2048},
    }
    req = urllib.request.Request(
        f"{config.OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())["message"]["content"].strip()


def _parse_gaps(text: str) -> list[str]:
    m = re.search(r"^GAPS:\s*(.*)$", text, re.MULTILINE)
    if not m:
        return []
    if m.group(1).strip().lower() == "none":
        return []
    gaps = []
    for line in text[m.end():].splitlines():
        line = line.strip()
        if line.startswith("- "):
            gaps.append(line[2:].strip())
        elif line and not line.startswith("-"):
            break
    return gaps


def _validate(text: str, retrieved_ids: list[str]) -> tuple[bool, list[str], list[str], bool]:
    """(ok, citations, invalid_citations, is_not_in_kb)."""
    is_nk = text.startswith(NOT_IN_KB)
    cited, invalid = _extract_citations(text, retrieved_ids)
    ok = (not invalid) if is_nk else (bool(cited) and not invalid)
    return ok, cited, invalid, is_nk


def _enforce_register_status(text: str, results: list[dict], cited: list[str],
                             question: str = "") -> str:
    """R3 in code: if a cited register chunk's STATUS word is absent from the
    answer, append the status line deterministically (sourced from the register)."""
    from src.retrieve import _register_hits
    keyword_regs = set(_register_hits(question))
    additions = []
    for r in results:
        relevant = r["chunk_id"] in cited or r["chunk_id"] in keyword_regs
        if relevant and r["metadata"].get("state") == "register":
            m = re.search(r"^STATUS:\s*(.+)$", r["text"], re.MULTILINE)
            if m:
                status_word = m.group(1).split()[0].strip().lower()
                if status_word not in text.lower():
                    topic = r["metadata"].get("title", r["chunk_id"]).removeprefix("Decision: ")
                    additions.append(f"Decision status — {topic}: {m.group(1).strip()} [{r['chunk_id']}]")
    if not additions:
        return text
    block = "\n".join(additions)
    if re.search(r"^GAPS:", text, re.MULTILINE):
        return re.sub(r"(^GAPS:)", block + "\n\n\\1", text, count=1, flags=re.MULTILINE)
    return text + "\n\n" + block


ENUM_LINE_RE = re.compile(r"^(.{2,80}?)\s*\[([A-Za-z0-9#-]+)\]\s*$")


def _enum_answer(question: str, results: list[dict]) -> dict | None:
    """Enumeration map-reduce: extract names per document (small contexts an
    8B model handles reliably), merge + dedupe in code, verify every name
    appears verbatim in its cited chunk. Returns None on total extraction
    failure (caller falls back to the normal path)."""
    by_doc: dict[str, list[dict]] = {}
    for r in results:
        by_doc.setdefault(r["metadata"]["doc_id"], []).append(r)

    items: dict[str, tuple[str, str]] = {}   # casefolded name -> (name, chunk_id)
    calls_ok = 0
    for doc_id, chunks in by_doc.items():
        rendered = "\n\n".join(f"<chunk id=\"{c['chunk_id']}\">\n{c['text']}\n</chunk>" for c in chunks)
        try:
            out = _call_ollama(ENUM_EXTRACT.format(question=question, chunks=rendered), "Extract now.")
        except (urllib.error.URLError, OSError, TimeoutError):
            continue
        calls_ok += 1
        chunk_texts = {c["chunk_id"]: c["text"].lower() for c in chunks}

        def _ground(name: str) -> str | None:
            """Find the chunk (in this doc group) containing the name verbatim.
            Tries the full name, then parts split on ( ) / — e.g.
            'Lyric (ClaimsXten)' grounds via either token."""
            candidates = [name] + [p.strip() for p in re.split(r"[()/]", name) if len(p.strip()) >= 3]
            for cand in candidates:
                rx = re.compile(rf"(?<![a-z0-9]){re.escape(cand.lower())}(?![a-z0-9])")
                for cid, text in chunk_texts.items():
                    if rx.search(text):       # word-boundary: 'ERP' must NOT match 'enterprise'
                        return cid
            return None

        for line in out.splitlines():
            line = line.strip().lstrip("-*0123456789. ").strip()
            if not line or line.upper() == "NONE" or len(line) > 80:
                continue
            m = ENUM_LINE_RE.match(line)
            name = m.group(1).strip() if m else line
            cid = _ground(name)               # citation assigned by verbatim search
            if cid:
                items.setdefault(name.casefold(), (name, cid))

    if not calls_ok or not items:
        return None

    lines = [f"- {name} [{cid}]" for name, cid in sorted(items.values(), key=lambda x: x[0].casefold())]
    text = ("Systems named in the knowledge base for this question "
            "(aggregated across all retrieved chunks):\n" + "\n".join(lines) + "\n\nGAPS: none")
    return {
        "answer": text,
        "citations": sorted({cid for _, cid in items.values()}),
        "gaps": [],
        "retrieved_ids": [r["chunk_id"] for r in results],
        "status": "grounded",
        "stripped_citations": [],
        "badges": ["≡ enumeration (per-doc extraction, code-side merge; every name verified in its chunk)"],
    }


def _extractive_fallback(results: list[dict]) -> str:
    """Ollama down: top-3 chunks verbatim with citations — never silence, never invention."""
    lines = ["(Ollama unavailable — extractive fallback: top retrieved chunks verbatim)\n"]
    for r in results[:3]:
        lines.append(f"[{r['chunk_id']}] (state={r['metadata'].get('state')})\n{r['text']}\n")
    lines.append("GAPS:\n- generated answer unavailable (Ollama down)")
    return "\n".join(lines)


DECISION_WORDS = {"selected", "confirmed", "decided", "decision", "approach",
                  "status", "chosen", "finalized", "approved", "agreed"}

ENUM_WORDS = {"systems", "interacts", "integrations", "integrates", "vendors",
              "list", "flows", "interfaces", "partners", "connects"}


def _looks_enumeration(question: str) -> bool:
    return bool(ENUM_WORDS & set(re.findall(r"[a-z]+", question.lower())))


DEFINITIONAL_RE = re.compile(r"^\s*(what\s+is|what's|describe|tell\s+me\s+about|explain)\b",
                             re.IGNORECASE)


def _looks_definitional(question: str) -> bool:
    return bool(DEFINITIONAL_RE.match(question))


def _looks_decision_shaped(question: str) -> bool:
    return bool(DECISION_WORDS & set(re.findall(r"[a-z]+", question.lower())))


GREETINGS = {
    "hi", "hello", "hey", "yo", "hola", "test", "thanks", "thank you",
    "good morning", "good evening", "ok", "okay", "help",
}
_STOPWORDS = {"what", "is", "the", "a", "an", "of", "for", "and", "or", "in",
              "on", "to", "how", "who", "which", "are", "do", "does", "it"}

HELP_TEXT = (
    "This is a knowledge-base query interface for the Meritain architecture "
    "docs — it answers questions, it doesn't chat.\n\n"
    "Try questions like:\n"
    "- What is DG?\n"
    "- How do ID cards get printed?\n"
    "- Which CDC approach was selected?\n\n"
    "GAPS: none"
)


def _is_query(question: str) -> bool:
    """False for greetings/empty/no-content inputs — don't run the pipeline
    (retrieval always returns *something*, and the model would summarize
    arbitrary chunks)."""
    q = question.strip().lower().rstrip("?!. ")
    if not q or q in GREETINGS:
        return False
    content = [t for t in re.findall(r"[a-z0-9]+", q) if t not in _STOPWORDS and len(t) > 1]
    return bool(content)


def general_answer(question: str) -> dict:
    """Model's OWN knowledge — never blended with KB answers. Returns
    {answer, confidence, status:'general'}. Confidence is the model's
    self-assessment (high/medium/low) — an honesty signal, not a guarantee."""
    try:
        text = _call_ollama(GENERAL_SYSTEM, question)
    except (urllib.error.URLError, OSError, TimeoutError):
        return {"answer": "(general-knowledge answer unavailable — Ollama down)",
                "confidence": "n/a", "status": "general"}
    m = re.search(r"^CONFIDENCE:\s*(high|medium|low)\s*[—-]?\s*(.*)$",
                  text, re.MULTILINE | re.IGNORECASE)
    confidence = m.group(1).lower() if m else "unstated"
    reason = m.group(2).strip() if m else ""
    body = text[:m.start()].strip() if m else text
    return {"answer": body, "confidence": confidence,
            "confidence_reason": reason, "status": "general"}


def _bank_result(question: str, hit: dict) -> dict:
    """Serve a QA-bank match: Y/P -> stored answer (no LLM); N -> known gap."""
    entry = hit["entry"]
    badge = f"⚡ verified Q&A bank (matched: {hit['matched_question']})"
    if entry["answerable"] in ("Y", "P"):
        gaps = []
        if entry["answerable"] == "P":
            gaps = [f"partially answered in the bank; remaining detail: {entry.get('suggested_sme') or 'SME TBD'}"]
        return {"answer": entry["answer"], "citations": entry["citations_resolved"],
                "gaps": gaps, "retrieved_ids": [], "status": "grounded",
                "bank_hit": True, "badges": [badge],
                "decision_status": entry.get("decision_status")}
    # known gap (N)
    sme = entry.get("suggested_sme") or "TBD"
    text = (f"{NOT_IN_KB}\nThis is a KNOWN gap ({entry['id']}); suggested SME: {sme}.\n"
            f"GAPS:\n- {entry['question']}")
    return {"answer": text, "citations": [], "gaps": [entry["question"]],
            "retrieved_ids": [], "status": "not_in_kb",
            "bank_hit": True, "badges": [badge], "suggested_sme": sme}


def answer(question: str, k: int = config.TOP_K, use_bank: bool | None = None) -> dict:
    """Full pipeline + Phase 6 verification decoration (V2 confidence chip,
    V3 staleness warning). Confidence comes from retrieval evidence only."""
    result = _answer_core(question, k=k, use_bank=use_bank)
    result.setdefault("corrected_query", None)
    from src.verify import confidence, staleness_note
    if result.get("status") == "grounded":
        result["confidence"] = confidence(result["citations"])
        note = staleness_note(result["citations"])
        if note:
            result.setdefault("badges", []).append(note)
            result["answer"] += f"\n\n{note}"
    else:
        result.setdefault("confidence", "n/a")
    result.setdefault("badges", [])
    result.setdefault("stripped_citations", [])
    result.setdefault("bank_hit", False)
    return result


def _answer_core(question: str, k: int = config.TOP_K, use_bank: bool | None = None) -> dict:
    if not _is_query(question):
        try:
            text = _call_ollama(CHITCHAT_SYSTEM, question)
        except (urllib.error.URLError, OSError, TimeoutError):
            text = HELP_TEXT
        return {"answer": text, "citations": [], "gaps": [],
                "retrieved_ids": [], "status": "chitchat"}

    # Pipeline order (Phase 6): small-talk -> query_fix -> qa_bank -> retrieve
    from src.query_fix import fix_query
    fx = fix_query(question)
    q_search = fx["corrected"]
    corrected_display = q_search if q_search != fx["original"] else None

    # QA-bank fast path (Phase 5): before any retrieval or generation
    use_bank = config.QA_BANK_ENABLED if use_bank is None else use_bank
    if use_bank:
        from src import qa_bank
        hit = qa_bank.lookup(q_search)
        if hit:
            out = _bank_result(question, hit)
            out["corrected_query"] = corrected_display
            return out
        qa_bank.record_candidate(question)

    results = retrieve(q_search, k=k)
    retrieved_ids = [r["chunk_id"] for r in results]

    if _looks_enumeration(question):
        enum = _enum_answer(q_search, results)
        if enum is not None:
            enum["corrected_query"] = corrected_display
            return enum

    user = ANSWER_USER_TEMPLATE.format(chunks=_render_chunks(results), question=question)
    if _looks_definitional(question):
        user += ("\n\nGive a COMPLETE definition from the chunks: what it is, its "
                 "technology stack (databases, ETL, tools, platforms) as stated in "
                 "the chunks, its role, and any stated future direction — every "
                 "fact cited. Do not stop at a one-sentence summary.")

    try:
        text = _call_ollama(ANSWER_SYSTEM, user)
    except (urllib.error.URLError, OSError, TimeoutError):
        return {
            "answer": _extractive_fallback(results),
            "citations": [r["chunk_id"] for r in results[:3]],
            "gaps": ["generated answer unavailable (Ollama down)"],
            "retrieved_ids": retrieved_ids,
            "status": "ollama_down",
        }

    ok, cited, invalid, is_nk = _validate(text, retrieved_ids)
    stripped: list[str] = []
    if invalid and cited:
        # V1: strip fabricated citations rather than rejecting an otherwise
        # well-cited answer (long enumerations often include one stray id;
        # full rejection degraded good answers to false refusals).
        for bad in invalid:
            text = text.replace(f"[{bad}]", "").replace("[" + bad + ",", "[").replace(", " + bad + "]", "]")
        stripped = invalid
        ok, cited, invalid, is_nk = _validate(text, retrieved_ids)
    if not ok:
        reason = f"invented citations: {invalid}" if invalid else "no citations on factual claims"
        text = _call_ollama(ANSWER_SYSTEM, user + RETRY_SUFFIX.format(reason=reason))
        ok, cited, invalid, is_nk = _validate(text, retrieved_ids)
        if invalid and cited:
            for bad in invalid:
                text = text.replace(f"[{bad}]", "")
            stripped += invalid
            ok, cited, invalid, is_nk = _validate(text, retrieved_ids)

    if is_nk and _looks_decision_shaped(question):
        # Deterministic rescue (R4): the model refused, but a query-matched
        # register chunk was retrieved — answer decision-status questions
        # straight from the register (grounded by construction).
        from src.retrieve import _register_hits
        reg_ids = [rid for rid in _register_hits(question) if rid in retrieved_ids]
        if reg_ids:
            by_id = {r["chunk_id"]: r for r in results}
            lines = []
            for rid in reg_ids:
                lines.append(by_id[rid]["text"] + f"\n[{rid}]")
            text = ("Decision status (from the decision register):\n\n"
                    + "\n\n".join(lines) + "\n\nGAPS: none")
            ok, cited, invalid, is_nk = _validate(text, retrieved_ids)

    if is_nk:
        status = "not_in_kb"
    elif ok:
        status = "grounded"
        text = _enforce_register_status(text, results, cited, question)
    else:
        status = "rejected"
        text = NOT_IN_KB + "\nGAPS:\n- model produced an ungrounded/miscited answer (rejected by validator)"

    gaps = _parse_gaps(text)
    return {
        "answer": text,
        "citations": cited if status == "grounded" else [],
        "gaps": gaps,
        "retrieved_ids": retrieved_ids,
        "status": status,
        "stripped_citations": stripped,
        "corrected_query": corrected_display,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    result = answer(" ".join(sys.argv[1:]))
    print(f"status: {result['status']}\n")
    print(result["answer"])
    if result["citations"]:
        print(f"\ncitations: {result['citations']}")
    print(f"retrieved: {result['retrieved_ids']}")


if __name__ == "__main__":
    main()
