# Running EAIP on a Windows laptop (Docker)

## Prerequisites (one-time)

1. **Windows 10/11** with **WSL2** enabled
   (`wsl --install` in an admin PowerShell, then reboot).
2. **Docker Desktop for Windows** — install, and in Settings ensure
   "Use the WSL 2 based engine" is on.
3. **Memory**: give WSL at least **12 GB** (16 GB laptop minimum for CPU
   inference). Create `C:\Users\<you>\.wslconfig`:

   ```ini
   [wsl2]
   memory=12GB
   ```

   then `wsl --shutdown` and restart Docker Desktop.
4. Copy the whole `eaip/` folder to the laptop (everything except `.venv/`,
   `chroma_db/`, `knowledge/`, `artifacts/`, `new_work/` — the image and
   volumes recreate what's needed).

## Start

```powershell
cd eaip
docker compose up -d --build
```

First start (once): builds the app image (~3 GB, bakes the embedding model),
pulls `llama3.1:8b` (~5 GB) into a Docker volume, then builds the vector and
QA-bank indexes. **Allow 10–20 minutes.** Watch progress with:

```powershell
docker compose logs -f eaip
```

When you see `starting app on :8501` → open **http://localhost:8501**.

Subsequent starts take seconds (`docker compose up -d`).

## NVIDIA GPU (optional, much faster answers)

With a recent NVIDIA driver on Windows (CUDA in WSL2 is automatic):

```powershell
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

CPU-only inference works fine but expect ~30–90 s per fresh answer on a
typical laptop; QA-bank hits (⚡) are instant either way.

## Where your data lives

| What | Where | Survives restart? |
|---|---|---|
| Knowledge base (`kb/`) | host folder, bind-mounted | yes — editable on host |
| SME answers (`answers/`) | host folder | yes |
| Gaps / usage log / bank candidates | host files | yes |
| Vector + bank indexes | `eaip_index` volume | yes (delete volume to force rebuild) |
| LLM weights | `ollama_models` volume | yes |

After editing `kb/` on the host: `docker compose exec eaip python -m src.ingest`
then re-run the golden gate:
`docker compose exec eaip python -m pytest tests/test_golden.py -q -s`.

## Common issues

- **Port 8501 busy** → change `ports:` to `"8600:8501"` in docker-compose.yml.
- **Slow/failed model pull** → `docker compose exec ollama ollama pull llama3.1:8b`
  and restart: `docker compose restart eaip`.
- **Out of memory (container exits, no error)** → raise `.wslconfig` memory;
  the LLM alone wants ~7 GB.
- **Rebuild indexes from scratch** →
  `docker compose down && docker volume rm eaip_eaip_index && docker compose up -d`.
- **Corporate proxy/SSL** → Docker Desktop → Settings → Resources → Proxies;
  the first build needs PyPI + HuggingFace + ollama.com access. After that,
  everything runs fully offline.
