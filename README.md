# Scout — Enterprise AI Supply Chain Copilot

- **`rag_pipeline/`** — backend. The existing guarded RAG + tool-use agent, plus a FastAPI layer (`rag_pipeline/api/`) that exposes it to the frontend: dashboard data (read from the CSVs in `data/tabular`), the AI assistant chat endpoint, and the escalation-email log.
- **`frontend/`** — Next.js app: landing page, `/dashboard`, `/assistant`.

## Run it

**Backend** (from `rag_pipeline/`):
```
pip install -r requirements.txt
uvicorn api.server:app --reload --port 8000
```

**Frontend** (from `frontend/`):
```
npm install
cp .env.local.example .env.local
npm run dev
```
Open http://localhost:3000.

The dashboard and escalations endpoints only need `pandas` + `fastapi` and work immediately. The `/assistant` chat endpoint additionally needs `langchain-core`, `langchain-ollama`, `langgraph`, `chromadb`, `sentence-transformers` (all in `requirements.txt`) and a running [Ollama](https://ollama.com) server with the model set in `config.py`. If those aren't available yet, `/assistant` degrades gracefully with a clear error instead of crashing the server — the rest of the app keeps working.

### Windows note: long path install failure

If `pip install -r requirements.txt` fails with `WinError 206: filename too long`, it's `torch`'s nested license folders hitting Windows' `MAX_PATH` limit — made worse by this project's long folder path. Fix either:
- Enable long paths: Local Group Policy Editor → Computer Configuration → Administrative Templates → System → Filesystem → "Enable Win32 long paths" → Enabled (then reboot), **or**
- `git config --global core.longpaths true` and move/clone the project to a shorter path (e.g. `C:\dev\scout`).

## Email escalation (human-in-the-loop)

When the assistant hits a request it can't authorize (refund, cancellation, override — anything guarded by `detect_escalation_request` in `guardrails/checks.py`), it drafts an email (via the LLM, falling back to a template if Ollama is unreachable) and sends it over SMTP. Configure in `rag_pipeline/.env`:

```
SMTP_USER=you@gmail.com
SMTP_PASSWORD=<Gmail App Password>
ESCALATION_RECIPIENT=team@yourcompany.com
```

Leave `SMTP_PASSWORD` blank to run in **dry-run mode** — every escalation is still drafted and logged to `rag_pipeline/api/data/escalations.json` (visible on the dashboard's Escalations tab), just not sent. `.env` is gitignored; `.env.example` documents every field.
