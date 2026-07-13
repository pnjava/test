# Meritain EAIP — Enterprise Architecture Intelligence Platform

Grounded Q&A + living wiki + knowledge-gap workflow over the Meritain
architecture KB. Every claim cites its source chunk; every unknown becomes a
tracked, SME-routed gap; every KB or prompt change is gated by a 20-question
golden regression suite.

**Stack:** Python 3.12 (`.venv/`) · ChromaDB (persistent) · sentence-transformers
all-MiniLM-L6-v2 · rank-bm25 · rapidfuzz · Ollama (local) · Streamlit · PyYAML · pytest.

---

## Quick start

```bash
cd ~/eaip
.venv/bin/python -m src.ingest                     # build/refresh index (idempotent)
.venv/bin/python -m src.qa_bank index              # (re)build QA-bank index
.venv/bin/python -m src.augment                    # synthetic-query augmentation (optional, slow)
.venv/bin/python -m streamlit run src/app.py       # the app (6 tabs)
.venv/bin/python -m pytest tests/ -q               # all gates (golden gate = live LLM, ~30 min)
```

Ollama must be running. If it is down, answers degrade to an extractive
fallback (top chunks verbatim, cited) — never an error-only screen (R8).

## Model

`config.OLLAMA_MODEL = "llama3.1:8b"`. Measured on the golden gate:
qwen2.5:7b 11/15 · qwen2.5:14b 14/15 (and OOM-killed jobs on this 24GB
machine) · **llama3.1:8b 15/15 (v2 gate) / 20/20 (v3 gate)**. Edit one
constant and rerun the gate to re-evaluate any model.

---

## The pipeline (a question's journey)

1. **Small-talk router** (R9): greetings get a canned/chat reply — no RAG.
2. **Query fix** (Phase 2): rapidfuzz vocabulary correction, then one locked
   LLM rewrite for what fuzzy can't fix. UI shows "Searching for: …".
3. **QA bank** (Phase 5): 112 curated Q&As, hybrid similarity match at 0.92 —
   hits answer instantly (⚡ badge, zero LLM); known-gap matches refuse with
   the right SME; misses are logged to `bank_candidates.yaml`.
4. **Hybrid retrieval** (Phase 3): alias expansion → vector top-12 (real
   chunks + 448 synthetic questions mapping to parents) + BM25 top-12 → RRF →
   top-12, then sibling expansion (multi-chunk docs arrive whole), register
   force-include on decision keywords, watchlist force-include (R6).
5. **Grounded answer** (Phase 6): chunks rendered least→most important and
   grouped by document (8B models lose evidence far from the question);
   enumeration questions use per-doc map-reduce extraction with code-side
   merge and verbatim grounding of every item; definitional questions get a
   completeness nudge; decision questions that the model wrongly refuses are
   answered deterministically from the register.
6. **Verification** (Phase 6): V1 citation integrity (fabricated citations
   stripped, uncited answers repaired once, then extractive downgrade) ·
   V2 evidence-based confidence chip (HIGH ≥2 docs / MEDIUM 1 doc / LOW
   single chunk or stale source — never model self-report) · V3 staleness
   warning (⏳) on 2014-era DRAFTS citations.
7. **Gap capture** (R7): every refusal/partial appends a structured,
   SME-routed entry to `gaps.yaml`; every Q&A is logged to `usage_log.yaml`.

## The app (six tabs)

- **💬 ASK** — chat; confidence/staleness/bank badges; corrected-query line;
  citation chips expand to chunk + source and jump to the WIKI page.
- **📚 WIKI** — generated from `kb/` at render time (nothing hand-written):
  nav tree Home/Current State/Target State/Governance, 31 page diagrams with
  zoom/download, status banners (proposed = warning; doc 05 = internal
  danger), cross-links, related-gaps footers, "Ask about this →".
- **▲ GAPS** — filterable register + per-SME chart + markdown export + Smart
  Loop intake on every open gap.
- **📥 REVIEW** — the knowledge inbox: UNANSWERED / LOW-CONFIDENCE / OPEN GAP
  merged worklist; intake adds SL5 side-by-side typo correction (both
  versions preserved; chosen text ingested, other kept as
  `original_submission`).
- **⚖ DECISIONS** — contradiction register as status-colored cards.
- **📈 INSIGHTS** — refusal rate, most-cited docs, LOW-confidence list,
  golden-set candidates (exported to `golden_set/candidates.yaml` for manual
  promotion — the 20-question gate is schema-locked), and GAP IMPACT RANKING
  for SME outreach priority.

## Smart Loop validation (before ANY ingest)

SL5 clean (review path, opt-in per submission) → **SL3 PHI scan (blocking,
no override)** → SL1 relevance (OFF-TOPIC warns; force-upload is tracked as
`unverified-forced` and badged wherever cited) → SL2 consistency (CONFLICT
offers contradiction-register tracking + `state=disputed` ingest) → SL4
partial answers keep the gap partially-open. Accepted answers land in
`answers/<gap-id>.md` with full provenance frontmatter and are ingested
incrementally (`python -m src.ingest --file …`).

## REGRESSION RULE (mandatory)

After EVERY KB change, prompt version bump, or SME ingest:

```bash
.venv/bin/python -m pytest tests/test_golden.py -q -s
```

All 20 must pass (10 answerable, 3 decision-status, 2 must-say-unknown,
5 typo/voice robustness). The suite runs the FULL pipeline including query
fixing and the QA bank; run it with the bank toggled too when bank content
changes (`config.QA_BANK_ENABLED`).

## Confluence publishing (Phase 8 — run on approval)

```bash
.venv/bin/python -m src.confluence_publish            # dry run -> build/confluence-preview/
CONFLUENCE_BASE_URL=… CONFLUENCE_SPACE_KEY=… CONFLUENCE_EMAIL=… CONFLUENCE_API_TOKEN=… \
.venv/bin/python -m src.confluence_publish --publish  # real (idempotent by title)
```

Markdown stays the source of truth; banners become Confluence info/warning
macros at publish time; diagrams upload as attachments; frontmatter becomes
labels (`state-*`, `confidence-*`, `tag-*`, `sme-*`).

---

## Demo script (final acceptance walkthrough)

1. **Wiki home**: WIKI tab → `00-stitched-architecture-overview` → expand the
   landscape diagram (page-19.png), zoom/download.
2. **DG page**: WIKI → `06-dg-current-state-landscape` → info banner, related
   docs buttons, related-gaps footer.
3. **Decision register**: DECISIONS tab → CDC-PATTERN card is amber/OPEN with
   RDRS + Outbox options listed.
4. **Grounded decision answer**: ASK → "Which CDC approach was selected?" →
   answer states **open**, mentions RDRS and Outbox, cites the register →
   click the citation's "→ wiki" button.
5. **Smart Loop live**: GAPS tab → "Answer this" on an open gap → paste an SME
   answer → validation chips → Accept & ingest → re-ask shows the cited
   answer. (Off-topic text triggers the warning + force path; forced content
   is badged ⚠ unverified-forced wherever cited.)
6. **REVIEW round-trip**: ASK an unanswerable question → REVIEW tab shows it
   as UNANSWERED → submit a typo-heavy answer → SL5 shows ORIGINAL vs
   CORRECTED side by side → accept corrected → validation → ingest → re-ask
   is grounded; `answers/<id>.md` keeps `original_submission`.
7. **Insights**: INSIGHTS tab → refusal rate, most-cited docs, gap-impact
   ranking populated from the session's questions.
8. **Confluence preview**: `build/confluence-preview/` holds storage-format
   XHTML for all 28 wiki pages + the Knowledge Gaps page + `_hierarchy.yaml`.

Automated versions of 5–7: `.venv/bin/python tests/demo_phase7.py`
(4 Smart-Loop cases incl. PHI block with no force option, REVIEW round-trip,
insights — all content sourced from real artifacts; the deliberate
CONFLICT demo is ingested as disputed and then cleaned up).

## Layout

```
kb/knowledge/markdown/   27 extraction docs (source of truth)
kb/knowledge/*.yaml|md   aliases / contradiction-register / sme-questions / extraction-notes
kb/assets/               31 page PNGs + image-map.yaml
golden_set/questions.yaml  20-question regression gate (schema-locked)
qa_bank.yaml             112 curated Q&As (69 Y / 16 P / 27 N)
answers/                 SME answer docs (loop output)
src/                     config prompts ingest query_fix retrieve augment
                         qa_bank answer verify gaps smart_loop review wiki
                         analytics confluence_publish app
tests/                   golden gate + phase acceptance suites + demo_phase7
chroma_db/               vector store (56 chunks + 448 synthetic + 112 bank)
gaps.yaml usage_log.yaml bank_candidates.yaml
```

Legacy note: `knowledge/`, `artifacts/`, and phase-1 `src/` modules
(chunker, embed_store, retriever, answer_engine, gap_capture,
text_extractor, alias_scanner…) are the previous iteration, kept for
reference; `src/phi_pii_scanner.py` is still live (SL3 reuses it).

## Hard-won engineering notes

- 8B models lose evidence far from the generation point: render chunks
  least→most important, grouped by doc, best doc adjacent to the question.
- Never trust model-formatted citations: normalize doc-level cites, strip
  fabricated ones (don't reject good answers), assign enumeration citations
  by verbatim search.
- Enumeration across many chunks needs map-reduce, not prompt begging.
- `num_predict` caps runaway temp-0 generation loops; 16k ctx prevents
  silent truncation of force-included chunks.
- Word-boundary matching everywhere: "ERP" must never match "Enterprise" —
  a substring check in the test harness produced a multi-hour ghost hunt.
- Evidence-based confidence (doc counts) beats model self-report.
