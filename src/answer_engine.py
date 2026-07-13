#!/usr/bin/env python3
"""
Grounded Answer Engine (T4.1)

question -> hybrid retrieve (T3.3) -> locked prompt (answer_prompt.md)
        -> local model via Ollama -> validated, cited answer.

Contract enforced in code, not just in the prompt:
  - every [chunk_id] citation must reference a retrieved chunk (no invented ids;
    one retry, then the answer is REJECTED and reported as ungrounded)
  - "Not in knowledge base." answers return a structured gap record
    (T4.3 appends these to gaps.yaml)

Usage:
    .venv/bin/python src/answer_engine.py "your question"
    .venv/bin/python src/answer_engine.py --model llama3.1:8b "your question"
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from retriever import retrieve  # noqa: E402

ROOT = Path(__file__).parent.parent
PROMPT_FILE = Path(__file__).parent / "answer_prompt.md"
OLLAMA_URL = "http://localhost:11434/api/chat"
# llama3.1:8b beats qwen2.5-coder:7b-instruct on needle-in-chunks reading
# (qwen missed 'DG is UniVerse DB' present in retrieved chunks; llama found it)
DEFAULT_MODEL = "llama3.1:8b"

CITATION_RE = re.compile(r"\[([A-Za-z0-9_.-]+::c\d{3})\]")
NOT_IN_KB = "Not in knowledge base."


def load_prompt_parts():
    text = PROMPT_FILE.read_text()
    system = text.split("## System prompt (verbatim)", 1)[1].split("## User prompt template", 1)[0].strip()
    user_tpl = text.split("## User prompt template (verbatim)", 1)[1].strip()
    return system, user_tpl


def render_chunks(chunks):
    parts = []
    for c in chunks:
        meta = c["metadata"]
        parts.append(
            f"[{c['chunk_id']}] (confidence: {meta['confidence']}; state: {meta['state']})\n{c['text']}"
        )
    return "\n\n---\n\n".join(parts)


def call_ollama(system, user, model, temperature=0.0):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": 8192},
    }
    req = urllib.request.Request(
        OLLAMA_URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())["message"]["content"].strip()


def validate(answer, retrieved_ids):
    """Return (ok, cited_ids, invalid_ids, is_not_in_kb, missing_lines)."""
    is_not_in_kb = answer.startswith(NOT_IN_KB)
    cited = CITATION_RE.findall(answer)
    invalid = sorted(set(cited) - set(retrieved_ids))
    missing = [ln.strip() for ln in answer.splitlines() if ln.strip().upper().startswith("MISSING")]
    if is_not_in_kb:
        ok = not invalid  # a not-in-KB answer must not fake citations either
    else:
        ok = bool(cited) and not invalid  # grounded answers need >=1 valid citation, 0 invented
    return ok, sorted(set(cited)), invalid, is_not_in_kb, missing


def answer(question, k=8, model=DEFAULT_MODEL):
    """Returns a dict:
    {question, answer, status: grounded|not_in_kb|rejected,
     citations: [chunk_id], chunks: {chunk_id: source_pointer}, gap: {...}|None}
    """
    chunks = retrieve(question, k=k)
    retrieved_ids = [c["chunk_id"] for c in chunks]
    system, user_tpl = load_prompt_parts()
    user = user_tpl.replace("{chunks}", render_chunks(chunks)).replace("{question}", question)

    text = call_ollama(system, user, model)
    ok, cited, invalid, is_not_in_kb, missing = validate(text, retrieved_ids)

    if not ok and not is_not_in_kb:
        # one retry with an explicit correction nudge
        correction = (
            user
            + "\n\nYour previous answer violated the rules"
            + (f" (invented citations: {invalid})" if invalid else " (no citations)")
            + ". Answer again following ALL rules exactly."
        )
        text = call_ollama(system, correction, model)
        ok, cited, invalid, is_not_in_kb, missing = validate(text, retrieved_ids)

    if is_not_in_kb:
        status = "not_in_kb"
    elif ok:
        status = "grounded"
    else:
        status = "rejected"
        text = (
            NOT_IN_KB
            + "\nMISSING: the model produced an ungrounded or miscited answer, which was rejected. "
            "Rephrase the question or add source material."
        )

    gap = None
    if status != "grounded":
        gap = {
            "question": question,
            "missing_info": missing or ["(model did not enumerate missing information)"],
            "retrieved_chunks_considered": retrieved_ids,
        }

    return {
        "question": question,
        "answer": text,
        "status": status,
        "model": model,
        "citations": cited if status == "grounded" else [],
        "chunks": {c["chunk_id"]: c["source_pointer"] for c in chunks},
        "gap": gap,
    }


def main():
    args = sys.argv[1:]
    model = DEFAULT_MODEL
    if "--model" in args:
        i = args.index("--model")
        model = args[i + 1]
        del args[i : i + 2]
    if not args:
        print(__doc__)
        sys.exit(2)

    result = answer(" ".join(args), model=model)
    print(f"status: {result['status']}   model: {result['model']}\n")
    print(result["answer"])
    if result["citations"]:
        print("\nsources:")
        for cid in result["citations"]:
            sp = result["chunks"].get(cid, {})
            print(f"  [{cid}] {sp.get('source_file', '?')} — {sp.get('heading', '?')}")


if __name__ == "__main__":
    main()
