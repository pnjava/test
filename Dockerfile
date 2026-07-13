FROM python:3.12-slim

WORKDIR /app

# system deps kept minimal; curl for the healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# bake the embedding model into the image so first boot works offline
RUN python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('all-MiniLM-L6-v2')"

# application code + knowledge base + curated data
COPY src/ src/
COPY kb/ kb/
COPY golden_set/ golden_set/
COPY tests/ tests/
COPY qa_bank.yaml .
COPY .streamlit/ .streamlit/
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && mkdir -p answers chroma_db build

ENV OLLAMA_URL=http://ollama:11434 \
    PYTHONUNBUFFERED=1 \
    HF_HUB_OFFLINE=1

EXPOSE 8501
# generous start period: first boot pulls the LLM (~5GB) and builds indexes
HEALTHCHECK --interval=30s --timeout=5s --start-period=1200s \
  CMD curl -sf http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
