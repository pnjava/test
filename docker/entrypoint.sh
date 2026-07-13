#!/bin/sh
set -e

echo "[eaip] waiting for Ollama at ${OLLAMA_URL} ..."
until curl -sf "${OLLAMA_URL}/api/tags" > /dev/null 2>&1; do
  sleep 2
done
echo "[eaip] Ollama is up."

MODEL="${OLLAMA_MODEL:-llama3.1:8b}"
if ! curl -sf "${OLLAMA_URL}/api/tags" | grep -q "\"${MODEL}\""; then
  echo "[eaip] pulling model ${MODEL} (first run only — several GB, be patient)..."
  curl -sf -X POST "${OLLAMA_URL}/api/pull" -d "{\"name\":\"${MODEL}\"}" | tail -1 || true
fi

# build indexes on first boot (volume starts empty); idempotent afterwards
if [ ! -f /app/chroma_db/.initialized ]; then
  echo "[eaip] first boot: building chroma index + QA bank index..."
  python -m src.ingest
  python -m src.qa_bank index
  touch /app/chroma_db/.initialized
  echo "[eaip] indexes built."
else
  echo "[eaip] indexes present — skipping build (delete chroma_db volume to rebuild)."
fi

echo "[eaip] starting app on :8501"
exec python -m streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
