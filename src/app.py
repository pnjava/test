"""EAIP — three-workspace app (UI architecture v2).

Workspaces (jobs, not modules):
  ✦ Ask        chat + persistent evidence rail (citations open beside the answer)
  ✦ Knowledge  wiki + decision register merged, cross-linked, right-rail context
  ✦ Workbench  gaps + review inbox + SME intake as one owner-grouped queue,
               with an analytics strip on top

Global omnisearch routes automatically: question -> Ask, doc match ->
Knowledge, gap match -> Workbench.

Design tokens: three surface elevations (page/card/nested); indigo accent
reserved for interactive elements; semantic colors (emerald/amber/rose)
reserved for trust states (confidence, staleness, disputed) only.

Run:  .venv/bin/python -m streamlit run src/app.py
"""

import sys
from pathlib import Path

import streamlit as st
import yaml

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src import config, wiki, smart_loop, review, analytics          # noqa: E402
from src.answer import answer                                        # noqa: E402
from src.gaps import record_gap, load_gaps, seed_sme_questions, qa_bank_gaps  # noqa: E402

ACCENT = "#8b96ff"                     # brighter indigo: 7.1:1 on CARD
GREEN, AMBER, DANGER = "#4ade80", "#fcd34d", "#fb8f8f"   # all >=7:1 on CARD
BG, CARD, NESTED = "#0e1117", "#171c26", "#212836"
TEXT, TEXT_DIM = "#f0f3f9", "#c2cbd9"  # body 13.9:1, secondary 8.6:1 on CARD
BORDER = "rgba(255,255,255,0.12)"
WORKSPACES = ["✦ Ask", "✦ Knowledge", "✦ Workbench"]

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"], .stMarkdown, .stTextInput, .stButton, label,
[data-testid="stExpander"], [data-testid="stChatInput"] textarea,
[data-testid="stTextArea"] textarea, [data-testid="stMetric"] {{
    font-family: 'Inter', -apple-system, sans-serif !important; }}
.stApp {{ background: radial-gradient(1100px 500px at 20% -10%, #1a1e3a55, transparent), {BG}; color: {TEXT}; }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stToolbar"] {{ display: none; }}
[data-testid="stSidebar"] {{ display: none; }}

.stMarkdown p, .stMarkdown li, [data-testid="stChatMessage"] p {{
    color: {TEXT} !important; font-size: 0.94rem; line-height: 1.7; }}
.stMarkdown strong {{ color: {TEXT}; font-weight: 600; }}
h1 {{ background: linear-gradient(90deg, {ACCENT}, #c4b5fd);
     -webkit-background-clip: text; -webkit-text-fill-color: transparent;
     font-weight: 700 !important; letter-spacing: -0.5px; }}
h2, h3 {{ color: {TEXT} !important; font-weight: 600 !important; }}

/* elevation system: page -> card (only bordered surface) -> nested (fill only) */
[data-testid="stChatMessage"] {{ background: {CARD} !important; border: 1px solid {BORDER};
    border-radius: 14px; box-shadow: 0 2px 14px rgba(0,0,0,0.28); }}
[data-testid="stExpander"] {{ border: 1px solid {BORDER} !important;
    background: {CARD} !important; border-radius: 12px; overflow: hidden; }}
[data-testid="stExpander"] summary span {{ color: {TEXT} !important; font-size: 0.86rem; }}
[data-testid="stExpander"] summary:hover span {{ color: {ACCENT} !important; }}
[data-testid="stExpander"] pre, [data-testid="stText"] {{
    font-family: 'JetBrains Mono', monospace !important; color: {TEXT} !important;
    background: {NESTED} !important; font-size: 0.82rem !important;
    white-space: pre-wrap; border-radius: 8px; border: none; }}

/* interactive = accent, always */
.stButton > button {{ background: {NESTED}; color: {TEXT}; border: 1px solid transparent;
    font-size: 0.8rem; font-weight: 500; border-radius: 9px; transition: all .15s ease; }}
.stButton > button:hover {{ color: {ACCENT}; border-color: {ACCENT}55;
    box-shadow: 0 0 0 3px {ACCENT}1a; background: {NESTED}; }}
.stButton > button[kind="primary"] {{ background: {ACCENT}; color: #0b0d14; font-weight: 600; }}
.stButton > button[kind="primary"]:hover {{ filter: brightness(1.08); color: #0b0d14; }}

[data-testid="stChatInput"] {{ background: {CARD}; border: 1px solid {BORDER};
    border-radius: 14px; box-shadow: 0 6px 22px rgba(0,0,0,0.35); }}
[data-testid="stChatInput"] textarea {{ background: transparent !important;
    color: {TEXT} !important; caret-color: {ACCENT}; }}

/* workspace pills */
div[role="radiogroup"] {{ gap: 0.3rem; background: {CARD}; padding: 0.28rem;
    border-radius: 12px; border: 1px solid {BORDER}; width: fit-content; }}
div[role="radiogroup"] label {{ background: transparent; border: none;
    border-radius: 9px; padding: 0.3rem 1rem; transition: all .15s ease; }}
div[role="radiogroup"] label:hover {{ background: {NESTED}; }}
div[role="radiogroup"] label:has(input:checked) {{ background: {ACCENT}22;
    outline: 1px solid {ACCENT}66; }}
div[role="radiogroup"] label p {{ font-size: 0.86rem !important; font-weight: 500; }}

[data-testid="stMetricValue"] {{ color: {ACCENT} !important; font-size: 1.5rem !important; }}
[data-testid="stMetricLabel"] p {{ color: {TEXT_DIM} !important; }}
[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 12px; overflow: hidden; }}
[data-testid="stTextInput"] input {{ background: {CARD}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 10px; }}
[data-testid="stTextInput"] input:focus {{ border-color: {ACCENT}; box-shadow: 0 0 0 3px {ACCENT}1a; }}

/* trust-state semantics (the ONLY use of green/amber/rose) */
.evi-head-HIGH {{ color: {GREEN}; }} .evi-head-MEDIUM {{ color: {AMBER}; }}
.evi-head-LOW {{ color: {DANGER}; }} .evi-head-na {{ color: {TEXT_DIM}; }}
.chip {{ display: inline-flex; align-items: center; border-radius: 999px;
    padding: 0.15rem 0.7rem; font-size: 0.78rem; font-weight: 600; margin: 0 0.3rem 0.3rem 0; }}
.chip-HIGH {{ color: {GREEN}; background: {GREEN}1a; }}
.chip-MEDIUM {{ color: {AMBER}; background: {AMBER}1a; }}
.chip-LOW {{ color: {DANGER}; background: {DANGER}1a; }}
.chip-type {{ color: {TEXT_DIM}; background: {NESTED}; }}
.evi-pill {{ display: inline-flex; font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem; color: {TEXT}; background: {NESTED};
    border-radius: 6px; padding: 0.1rem 0.5rem; margin: 0 0.25rem 0.25rem 0; }}
.gap-block {{ border: 1px solid {AMBER}66; color: {AMBER}; padding: 0.65rem 1rem;
    margin: 0.5rem 0; font-size: 0.88rem; background: {AMBER}1a; border-radius: 12px; }}
.banner-info {{ border-left: 3px solid {ACCENT}; background: {ACCENT}1a; color: {TEXT};
    padding: 0.6rem 1rem; margin: 0.5rem 0; border-radius: 0 10px 10px 0; }}
.banner-warn {{ border-left: 3px solid {AMBER}; background: {AMBER}1f; color: {AMBER};
    padding: 0.6rem 1rem; margin: 0.5rem 0; border-radius: 0 10px 10px 0; }}
.banner-danger {{ border-left: 3px solid {DANGER}; background: {DANGER}1f; color: {DANGER};
    padding: 0.6rem 1rem; margin: 0.5rem 0; border-radius: 0 10px 10px 0; }}
.retrieved {{ font-family: 'JetBrains Mono', monospace; color: {TEXT_DIM};
    font-size: 0.75rem; margin-top: 0.6rem; opacity: 0.85; }}
.stat {{ color: {TEXT_DIM}; font-size: 0.85rem; line-height: 1.8; }}
.rail {{ position: sticky; top: 1rem; }}
/* every text-bearing Streamlit primitive, explicitly */
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p
    {{ color: {TEXT_DIM} !important; font-size: 0.8rem !important; }}
[data-testid="stWidgetLabel"] p, label p {{ color: {TEXT} !important; font-size: 0.84rem; }}
[data-testid="stFileUploaderDropzone"] {{ background: {NESTED} !important;
    border: 1px dashed {BORDER}; border-radius: 10px; }}
[data-testid="stFileUploaderDropzone"] span, [data-testid="stFileUploaderDropzone"] small
    {{ color: {TEXT_DIM} !important; }}
[data-testid="stTextArea"] textarea {{ background: {NESTED} !important; color: {TEXT} !important;
    border-radius: 10px; }}
[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{ background: {NESTED};
    border-color: {BORDER}; color: {TEXT}; }}
button[kind="pills"], button[kind="pillsActive"] {{ background: {NESTED} !important;
    color: {TEXT} !important; border: 1px solid {BORDER} !important; border-radius: 999px !important; }}
button[kind="pillsActive"] {{ border-color: {ACCENT} !important; color: {ACCENT} !important;
    background: {ACCENT}22 !important; }}
[data-testid="stMetricLabel"] p {{ color: {TEXT_DIM} !important; font-size: 0.82rem !important; }}
hr {{ border-color: {BORDER}; }}
</style>
"""


@st.cache_data
def _chunk_lookup() -> dict:
    import chromadb
    coll = chromadb.PersistentClient(path=str(config.CHROMA_DIR)).get_collection(config.COLLECTION_NAME)
    got = coll.get(include=["documents", "metadatas"])
    return {cid: (doc, meta) for cid, doc, meta in zip(got["ids"], got["documents"], got["metadatas"])}


def nav_to(ws: str, **state) -> None:
    st.session_state.nav = ws
    for k, v in state.items():
        st.session_state[k] = v
    st.rerun()


def _confidence_why(result: dict) -> str:
    docs = {c.split("#")[0] for c in result.get("citations", [])}
    conf = result.get("confidence", "n/a")
    if conf == "HIGH":
        return f"{len(docs)} independent docs agree"
    if conf == "MEDIUM":
        return "single document, multiple chunks"
    if conf == "LOW":
        from src.verify import stale_doc_ids
        return ("cites a 2014-era source — verify currency"
                if docs & stale_doc_ids() else "single chunk of evidence")
    return "no grounded citations"


# ------------------------------------------------------------------ ASK

def _evidence_rail() -> None:
    """Persistent right rail: evidence for the selected citation / last answer."""
    st.markdown("<div class='rail'>", unsafe_allow_html=True)
    hist = st.session_state.history
    if not hist:
        st.markdown("<div class='banner-info'>Evidence appears here. Ask something — "
                    "then click any citation pill to inspect its source.</div>",
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    result = hist[-1]["result"]
    conf = result.get("confidence", "n/a")
    head_cls = f"evi-head-{conf if conf in ('HIGH', 'MEDIUM', 'LOW') else 'na'}"
    st.markdown(f"<h3 class='{head_cls}'>● {conf} confidence</h3>"
                f"<div class='stat'>{_confidence_why(result)}</div>", unsafe_allow_html=True)
    for b in result.get("badges", []):
        st.markdown(f"<span class='chip chip-type'>{b}</span>", unsafe_allow_html=True)

    cid = st.session_state.get("evidence_cid")
    citations = result.get("citations", [])
    if cid not in citations:
        cid = citations[0] if citations else None
    if not cid:
        st.markdown("<div class='stat'>no citations for this answer</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    chunk_text, meta = _chunk_lookup().get(cid, ("(chunk not in index)", {}))
    doc_id = cid.split("#")[0]
    st.markdown(f"<span class='evi-pill'>{cid}</span>"
                f"<span class='evi-pill'>{meta.get('state', '?')}</span>"
                f"<span class='evi-pill'>{meta.get('confidence', '?')[:24]}</span>",
                unsafe_allow_html=True)
    st.caption(meta.get("source", ""))
    if meta.get("confidence") == "unverified-forced":
        st.markdown("<div class='banner-warn'>⚠ unverified-forced content</div>", unsafe_allow_html=True)
    if meta.get("state") == "disputed":
        st.markdown("<div class='banner-danger'>⚠ DISPUTED — see decision register</div>", unsafe_allow_html=True)

    st.text(chunk_text[:1600])

    doc = wiki.get_doc(doc_id)
    if doc:
        for img in doc["images"][:1]:
            st.image(str(img), caption=img.name, width="stretch")
        if st.button("Open full page →", key=f"rail_open_{cid}"):
            nav_to("✦ Knowledge", k_doc=doc_id)
        gaps = wiki.related_gaps(doc)
        if gaps:
            st.markdown(f"<div class='stat'>related open gaps: {len(gaps)} → Workbench</div>",
                        unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_answer(item_idx: int, result: dict) -> None:
    if result.get("corrected_query"):
        st.caption(f"Searching for: {result['corrected_query']}")
    st.markdown(result["answer"].replace("\n", "  \n"))
    if result.get("gaps"):
        items = "".join(f"<div>▸ {g}</div>" for g in result["gaps"])
        st.markdown(f"<div class='gap-block'>⚠ NOT FULLY IN KNOWLEDGE BASE{items}</div>",
                    unsafe_allow_html=True)
    citations = result.get("citations", [])
    if citations:
        cols = st.columns(min(4, len(citations)) or 1)
        for i, cid in enumerate(citations):
            if cols[i % len(cols)].button(cid.split("#")[0][:24] + ("#" + cid.split("#")[1] if "#" in cid else ""),
                                          key=f"cite{item_idx}_{i}", help="inspect in evidence rail"):
                st.session_state.evidence_cid = cid
                st.rerun()


def ws_ask() -> None:
    chat_col, rail_col = st.columns([13, 7], gap="large")
    with chat_col:
        for idx, item in enumerate(st.session_state.history):
            with st.chat_message("user"):
                st.markdown(item["question"])
            with st.chat_message("assistant"):
                _render_answer(idx, item["result"])
        question = st.chat_input("Ask the knowledge base…") or st.session_state.pop("ask_prefill", None)
        if question:
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("retrieving + answering…"):
                    result = answer(question)
                    if result.get("gaps"):
                        record_gap(question, result["gaps"], result.get("retrieved_ids", []))
                    analytics.log_qa(question, result.get("corrected_query") or question, result)
            st.session_state.history.append({"question": question, "result": result})
            st.session_state.evidence_cid = (result.get("citations") or [None])[0]
            st.rerun()
    with rail_col:
        _evidence_rail()


# -------------------------------------------------------------- KNOWLEDGE

def _decision_cards() -> None:
    st.header("Decision register")
    reg = yaml.safe_load(config.CONTRADICTION_REGISTER.read_text())["decisions"]
    for d in reg:
        status = str(d["status"])
        color = {"open": AMBER, "selected": GREEN, "rejected": DANGER}.get(
            status.split()[0].split("(")[0].strip(), TEXT_DIM)
        strike = "text-decoration: line-through;" if status.startswith("rejected") else ""
        st.markdown(
            f"<div style='background:{CARD}; border:1px solid {BORDER}; border-left:4px solid {color};"
            f" border-radius:12px; padding:0.7rem 1rem; margin:0.5rem 0;'>"
            f"<span style='color:{color}; font-weight:600'>{d['id']} — {status.upper()}</span><br>"
            f"<span style='{strike}'>{d['topic']}</span></div>", unsafe_allow_html=True)
        detail = d.get("evidence") or d.get("notes") or ""
        if detail:
            st.caption(str(detail)[:220])
        for opt in d.get("options", []):
            st.markdown(f"- {opt['name']} — *{opt['status']}*")


def ws_knowledge() -> None:
    nav_col, doc_col, rail_col = st.columns([4, 12, 5], gap="large")
    docs = wiki.load_docs()
    with nav_col:
        q = st.text_input("filter", key="wiki_search", placeholder="filter docs…",
                          label_visibility="collapsed")
        matches = wiki.search(q) if q else docs
        if st.button("⚖ Decision register", key="nav_decisions",
                     type="primary" if st.session_state.get("k_doc") == "__decisions__" else "secondary"):
            st.session_state.k_doc = "__decisions__"
            st.rerun()
        for group in ("Home", "Current State", "Target State", "Governance"):
            group_docs = [d for d in matches if d["group"] == group]
            if not group_docs:
                continue
            st.markdown(f"**{group}**")
            for d in group_docs:
                if st.button(d["doc_id"], key=f"nav{d['doc_id']}"):
                    st.session_state.k_doc = d["doc_id"]
                    st.rerun()

    selected = st.session_state.get("k_doc") or "00-stitched-architecture-overview"
    if selected == "__decisions__":
        with doc_col:
            _decision_cards()
        with rail_col:
            st.markdown("<div class='banner-info'>Every answer touching these topics states "
                        "the decision status automatically.</div>", unsafe_allow_html=True)
        return

    doc = wiki.get_doc(selected)
    with doc_col:
        if not doc:
            st.info("select a document")
            return
        st.header(doc["title"])
        if doc["state"].lower().startswith("proposed"):
            st.markdown("<div class='banner-warn'>⚠ PROPOSED — target architecture, not implemented</div>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='banner-info'>state: {doc['state']} · confidence: "
                        f"{doc['confidence']} · {doc['source']}</div>", unsafe_allow_html=True)
        if doc["sensitive"]:
            st.markdown("<div class='banner-danger'>🔒 INTERNAL — employee names/screenshots. "
                        "Do not distribute.</div>", unsafe_allow_html=True)
        for img in doc["images"]:
            with st.expander(f"diagram · {img.name}", expanded=False):
                st.image(str(img), width="stretch")
                st.download_button(f"download {img.name}", img.read_bytes(),
                                   file_name=img.name, key=f"dl{doc['doc_id']}{img.name}")
        st.markdown(doc["body"])

    with rail_col:
        if not doc:
            return
        st.markdown("<div class='rail'>", unsafe_allow_html=True)
        if st.button("Ask about this →", key=f"ask{doc['doc_id']}", type="primary"):
            nav_to("✦ Ask", ask_prefill=f"Tell me about {doc['title']}")
        links = wiki.cross_links(doc)
        if links:
            st.markdown("**Related docs**")
            for l in links[:8]:
                if st.button(l, key=f"xl{doc['doc_id']}{l}"):
                    st.session_state.k_doc = l
                    st.rerun()
        gaps = wiki.related_gaps(doc)
        if gaps:
            st.markdown("**Open gaps on this page**")
            for g in gaps[:5]:
                st.markdown(f"<div class='gap-block'>▸ {g['question'][:90]}<br>"
                            f"<small>{g.get('suggested_sme', 'TBD')}</small></div>",
                            unsafe_allow_html=True)
            if st.button("Work these →", key=f"wb{doc['doc_id']}"):
                nav_to("✦ Workbench")
        st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------- WORKBENCH

def render_intake(question: str, gap_id: str, key: str) -> None:
    ss = st.session_state
    text = st.text_area("SME answer (paste text)", key=f"{key}_text", height=130)
    uploaded = st.file_uploader("…or upload md/txt", type=["md", "txt"], key=f"{key}_file")
    contributor = st.text_input("contributor", key=f"{key}_who")
    submission = (uploaded.read().decode(errors="replace") if uploaded else text or "").strip()

    if submission and st.button("Clean & compare (optional)", key=f"{key}_sl5"):
        with st.spinner("correcting typos/transcription…"):
            ss[f"{key}_corrected"] = smart_loop.clean_submission(submission)
            ss[f"{key}_original"] = submission
    if ss.get(f"{key}_corrected"):
        c1, c2 = st.columns(2)
        c1.markdown("**ORIGINAL**")
        c1.text(ss[f"{key}_original"][:1400])
        c2.markdown("**CORRECTED**")
        c2.text(ss[f"{key}_corrected"][:1400])
        pick = st.radio("use which?", ["Use corrected", "Keep original"],
                        key=f"{key}_pick", horizontal=True)
        submission = ss[f"{key}_corrected"] if pick == "Use corrected" else ss[f"{key}_original"]

    if submission and contributor and st.button("Validate", key=f"{key}_val", type="primary"):
        with st.spinner("PHI scan → relevance → consistency…"):
            ss[f"{key}_validation"] = smart_loop.validate_submission(question, submission)
            ss[f"{key}_submission"] = submission

    v = ss.get(f"{key}_validation")
    if not v:
        return
    submission = ss[f"{key}_submission"]

    if v["blocked"]:
        st.markdown("<div class='banner-danger'>⛔ PHI DETECTED — ingest blocked (no override).</div>",
                    unsafe_allow_html=True)
        for h in v["phi"]["hits"]:
            st.markdown(f"- `{h['pattern']}` ×{h['count']}: {', '.join(h['masked_samples'])}")
        return

    rel, con = v["relevance"], v["consistency"]
    st.markdown(f"<span class='chip chip-{'HIGH' if rel['verdict'] == 'RELEVANT' else 'MEDIUM' if rel['verdict'] == 'PARTIAL' else 'LOW'}'>"
                f"relevance: {rel['verdict']}</span>"
                f"<span class='chip chip-{'HIGH' if con['verdict'] == 'CONSISTENT' else 'LOW'}'>"
                f"consistency: {con['verdict']}</span>", unsafe_allow_html=True)
    st.caption(f"{rel['reason'][:140]} · {con['detail'][:100]}")
    original_sub = ss.get(f"{key}_original") if ss.get(f"{key}_corrected") else None

    def _finish(forced: bool = False, disputed: bool = False) -> None:
        path = smart_loop.save_and_ingest(gap_id, question, submission, contributor, v,
                                          forced=forced, disputed=disputed,
                                          original_submission=original_sub)
        new_status = "partially-answered" if rel["verdict"] == "PARTIAL" else "answered"
        smart_loop.update_gap_status(gap_id, new_status, note=path.name)
        review.add_bank_candidate(question)
        with st.spinner("re-asking with the new evidence…"):
            after = review.resolve_and_reask(question)
        st.success(f"ingested {path.name} → {new_status}")
        st.markdown(f"**Answer now** (confidence: {after.get('confidence')}):")
        st.markdown(after["answer"][:700].replace("\n", "  \n"))
        for k in [k for k in ss if k.startswith(key)]:
            del ss[k]

    if rel["verdict"] == "OFF-TOPIC":
        st.markdown(f"<div class='banner-warn'>⚠ Doesn't appear to answer the question — "
                    f"seems to be about: {rel['reason'][:110]}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("Revise", key=f"{key}_rev"):
            del ss[f"{key}_validation"]
            st.rerun()
        if c2.button("Force upload anyway", key=f"{key}_force"):
            _finish(forced=True)
        return
    if con["verdict"] == "CONFLICT":
        st.markdown(f"<div class='banner-warn'>⚠ Conflicts with KB: {con['detail'][:180]}</div>",
                    unsafe_allow_html=True)
        if st.button("Track contradiction + ingest as disputed", key=f"{key}_dis"):
            dec = smart_loop.record_contradiction(gap_id, submission[:80], con["detail"])
            st.info(f"contradiction recorded: {dec}")
            _finish(disputed=True)
        return
    if st.button("Accept & ingest", key=f"{key}_ok", type="primary"):
        _finish()


def ws_workbench() -> None:
    # analytics strip (insights in context of the work)
    ins = analytics.insights()
    live = [dict(g, source="gaps.yaml") for g in load_gaps()["gaps"]]
    answered_ids = {p.stem for p in (config.ROOT / "answers").glob("*.md")}
    live_qs = {g["question"].strip().lower() for g in live}
    seeds = [g for g in seed_sme_questions() + qa_bank_gaps()
             if g["question"].strip().lower() not in live_qs and g["id"] not in answered_ids]
    all_items = live + seeds
    open_items = [g for g in all_items if g["status"] == "open"]

    c = st.columns(5)
    c[0].metric("open questions", len(open_items))
    c[1].metric("answered", sum(1 for g in all_items if str(g["status"]).startswith(("answered", "partially"))))
    c[2].metric("asked (session)", ins["total"])
    c[3].metric("refusal rate", f"{ins['refusal_rate']:.0%}")
    c[4].metric("low-confidence", len(ins["low_confidence"]))

    if ins["gap_impact"]:
        with st.expander(f"📈 gap impact ranking (top: {ins['gap_impact'][0]['question'][:50]}…)"):
            st.dataframe(ins["gap_impact"], width="stretch", hide_index=True)

    # queue filters
    inbox = review.worklist()
    inbox_qs = {i["question"].strip().lower() for i in inbox}
    kinds = st.pills("filter", ["Unanswered (live)", "Low-confidence", "Open gaps", "SME seed questions"],
                     selection_mode="multi", key="wb_kinds", label_visibility="collapsed")
    smes = sorted({g.get("suggested_sme", "TBD") for g in open_items})
    f_sme = st.multiselect("owner", smes, key="wb_sme", placeholder="filter by SME/owner…")

    if st.button("Export SME questions (markdown)"):
        by_sme: dict[str, list] = {}
        for g in open_items:
            by_sme.setdefault(g.get("suggested_sme", "TBD"), []).append(g)
        lines = ["# SME Question Export", ""]
        for sme in sorted(by_sme):
            lines.append(f"## {sme}")
            lines += [f"- **{g['id']}**: {g['question']}" for g in by_sme[sme]]
            lines.append("")
        config.SME_EXPORT.write_text("\n".join(lines))
        st.success(f"→ {config.SME_EXPORT.name}")

    # merged queue rows (inbox first, then seeds), grouped by owner
    def _want(kind: str) -> bool:
        return not kinds or kind in kinds

    rows: list[tuple[str, str, str, str, list]] = []
    for it in inbox:
        kind = "Unanswered (live)" if it["type"] == "UNANSWERED" else \
               "Low-confidence" if it["type"] == "LOW-CONFIDENCE" else "Open gaps"
        if _want(kind):
            rows.append((it.get("sme", "TBD"), it["type"], it["question"],
                         it.get("gap_id") or f"rv-{abs(hash(it['key'])) % 10_000:04d}",
                         it.get("retrieved", [])))
    for g in seeds:
        if g["status"] == "open" and _want("SME seed questions"):
            rows.append((g.get("suggested_sme", "TBD"), f"seed · {g['source']}",
                         g["question"], g["id"], []))

    if f_sme:
        rows = [r for r in rows if r[0] in f_sme]

    by_owner: dict[str, list] = {}
    for r in rows:
        by_owner.setdefault(r[0], []).append(r)
    for owner in sorted(by_owner):
        st.markdown(f"### {owner} <span class='chip chip-type'>{len(by_owner[owner])}</span>",
                    unsafe_allow_html=True)
        for sme, typ, question, gap_id, retrieved in by_owner[owner]:
            with st.expander(f"{typ} · {question[:85]}"):
                if retrieved:
                    st.markdown(f"<div class='retrieved'>retrieved: {' '.join(retrieved[:8])}</div>",
                                unsafe_allow_html=True)
                render_intake(question, gap_id, key=f"wb_{gap_id}")


# ------------------------------------------------------------------ shell

def _omnisearch_route(q: str) -> None:
    ql = q.strip()
    if not ql:
        return
    doc_hits = wiki.search(ql)
    exactish = [d for d in doc_hits if ql.lower() in d["doc_id"].lower() or ql.lower() in d["title"].lower()]
    if exactish and len(ql.split()) <= 3 and "?" not in ql:
        nav_to("✦ Knowledge", k_doc=exactish[0]["doc_id"])
    open_gaps = [g for g in load_gaps()["gaps"] if g["status"] == "open"
                 and ql.lower() in g["question"].lower()]
    if open_gaps and "?" not in ql and len(ql.split()) <= 4:
        nav_to("✦ Workbench")
    nav_to("✦ Ask", ask_prefill=ql)


def main() -> None:
    st.set_page_config(page_title="Meritain EAIP", page_icon="✦", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("nav", WORKSPACES[0])

    head_l, head_m, head_r = st.columns([5, 8, 7], gap="large")
    with head_l:
        st.markdown("<h1 style='margin:0; font-size:1.6rem'>✦ Meritain EAIP</h1>"
                    f"<span class='stat'>{config.OLLAMA_MODEL} · "
                    f"{len(wiki.load_docs())} docs</span>", unsafe_allow_html=True)
    with head_m:
        nav = st.radio("nav", WORKSPACES, horizontal=True, label_visibility="collapsed",
                       index=WORKSPACES.index(st.session_state.nav), key="nav_radio")
        if nav != st.session_state.nav:
            st.session_state.nav = nav
    with head_r:
        q = st.text_input("omni", key="omni", placeholder="Search or ask anything — routes automatically…",
                          label_visibility="collapsed")
        if q and q != st.session_state.get("_omni_last"):
            st.session_state._omni_last = q
            _omnisearch_route(q)

    st.markdown("<hr style='margin:0.4rem 0 1rem 0'>", unsafe_allow_html=True)

    {"✦ Ask": ws_ask, "✦ Knowledge": ws_knowledge, "✦ Workbench": ws_workbench}[st.session_state.nav]()


if __name__ == "__main__":
    main()
