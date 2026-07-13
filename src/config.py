"""Central configuration for the EAIP pipeline (paths, models, tuning).

All modules import from here — no path or model literals elsewhere.
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent

# --- knowledge base (source of truth) ---
KB_DIR = ROOT / "kb" / "knowledge"
MARKDOWN_DIR = KB_DIR / "markdown"
ALIASES_FILE = KB_DIR / "aliases.yaml"
CONTRADICTION_REGISTER = KB_DIR / "contradiction-register.yaml"
EXTRACTION_NOTES = KB_DIR / "extraction-notes.md"

# --- outputs / state ---
CHROMA_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "meritain"
GAPS_FILE = ROOT / "gaps.yaml"
GOLDEN_SET = ROOT / "golden_set" / "questions.yaml"
SME_EXPORT = ROOT / "sme-export.md"

# --- chunking (T-spec: 150-400 word self-contained chunks) ---
CHUNK_MIN_WORDS = 150
CHUNK_MAX_WORDS = 400

# --- retrieval ---
TOP_K = 12                # final merged results (master spec)
VECTOR_POOL = 12          # candidates from vector search
BM25_POOL = 12            # candidates from BM25
RRF_K = 60                # reciprocal-rank-fusion constant

# --- query fixing (Phase 2) ---
FUZZY_THRESHOLD = 85      # rapidfuzz token-correction score threshold

# --- QA bank fast path (Phase 5) ---
QA_BANK = ROOT / "qa_bank.yaml"
BANK_CANDIDATES = ROOT / "bank_candidates.yaml"
QA_MATCH_THRESHOLD = 0.92
QA_COLLECTION = "qa_bank"
QA_BANK_ENABLED = True

# --- assets / wiki (Phase 7) ---
ASSETS_DIR = ROOT / "kb" / "assets"          # meritain-kb-images.zip contents (MISSING as of 2026-07-13)
IMAGE_MAP = ASSETS_DIR / "image-map.yaml"
USAGE_LOG = ROOT / "usage_log.yaml"

# --- staleness (Phase 1) ---
STALE_YEAR_MAX = 2015     # doc source year <= this => stale_risk=true

# Queries containing any of these force-include the matching register chunks
DECISION_KEYWORDS = [
    "cdc", "kafka", "outbox", "rdrs", "five9", "avaya", "biztalk",
    "banktec", "zelis", "nextgen", "superapp", "mvis",
]

# R5 acronym-collision watchlist (extraction-notes.md): when queried, the best
# chunk containing the exact token is force-included so answers can keep the
# entities distinct. ("Image" omitted: too generic a token.)
WATCHLIST_ACRONYMS = ["MCI", "MICS", "MCMM", "1mage"]

# --- embeddings ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # sentence-transformers, local

# --- answer generation (Ollama, local) ---
# Env-overridable for containers: compose sets OLLAMA_URL=http://ollama:11434
import os as _os
OLLAMA_URL = _os.environ.get("OLLAMA_URL", "http://localhost:11434")
# Golden-gate history (identical prompts/retrieval, 2026-07-12, 15-Q gate):
#   qwen2.5:7b   = 11/15 (over-refuses)   qwen2.5:14b = 14/15
#   llama3.1:8b  = 15/15
# 2026-07-13: user switched to llama3.1:8b — best gate score AND qwen2.5:14b
# (10GB) caused OOM kills on this 24GB machine when the app + gate + model
# ran together. Re-evaluate any model:
#   .venv/bin/python -m pytest tests/test_golden.py -s  (after editing this)
OLLAMA_MODEL = _os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

# Register chunks get ids like: register-cdc-pattern (decision id lowercased)
REGISTER_DOC_PREFIX = "register"
