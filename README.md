# Gabriel 👼

A lightweight, **zero-intrusion GUI sidecar** for CLI-based AI agents (Antigravity, Claude Code, Cursor).

Gabriel runs independently alongside your terminal, tailing agent transcripts in real time to provide a dedicated dashboard for state monitoring, side-brain Q&A, session statistics, and knowledge base management — without ever blocking or hooking into your main CLI workflow.

## ✨ Features

- **Zero-Intrusion Tailing** — Watches only known agent transcript paths (e.g. `~/.gemini/antigravity-cli/brain/**/logs/transcript.jsonl`, `~/.claude/projects/**/*.jsonl`, `~/.cursor/logs/*.log`). No PTY / STDOUT / terminal hooks, so it physically cannot crash your main agent. Byte-offset incremental reads keep tailing cheap even on huge transcripts.
- **Real-time WebSocket Dashboard** — Parsed log lines are broadcast to the browser over a single WebSocket with a bounded non-blocking queue (slow clients drop frames instead of stalling the broker).
- **Mission Control Grid** — Multiple active agent sessions side by side in a CSS Grid dashboard, each with its own live terminal card, scroll-lock, and one-click Markdown export.
- **Side-brain Chat** — Ask "what is it doing?", "any errors?", or debug a stack trace without polluting the main agent's context. Optional terminal-snapshot attachment, streaming markdown responses, and SQLite-persisted chat history (40 turns per agent).
- **Hybrid Knowledge Base (FTS5 + Vector RRF)** — Chinese-aware jieba tokenization + local vector search (`sqlite-vec` + `fastembed` BAAI/bge-small-zh-v1.5) fused via Reciprocal Rank Fusion (RRF). Proactive toast recommendations on repeated errors with graceful pure FTS5 offline fallback.
- **Structured 4-Section Insights** — Insights automatically parse into structured `{problem, cause, solution, tags}` with tag chip rendering and legacy Markdown compatibility.
- **Resilient AI Pipeline** — Exponential backoff retries via `tenacity` for API connections, rate limits, and network timeouts.
- **Session Analytics** — `/api/stats` aggregates turns / characters / estimated cost per session; `/api/sessions` and `/api/sessions/{id}/transcript` expose full history.
- **MCP Server** — Stdio MCP server (`src/mcp_server.py`) and optional `--http` transport lets Claude Code / Cursor query the knowledge base directly.
- **Local-first & Secure** — Token auth on every API route and WebSocket (constant-time comparison); all frontend libs (DOMPurify, marked, highlight.js) vendored locally — **zero CDN dependencies**, fully offline; API key lives only in `.env`, never persisted to `config.json`.
- **Standardized Toolchain** — Built with `pytest` for unit testing and `ruff` for fast linting.

## 🚀 Quickstart

**Prerequisites:** Python 3.10+

```bash
git clone https://github.com/3ZEROS12/Gabriel.git
cd Gabriel
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -e .
```

Configure environment:

```bash
cp .env.example .env
# Optional: set GABRIEL_TOKEN (otherwise a random session token is generated)
# Optional: set OPENAI_API_KEY (preferred over the Settings UI — never written to disk config)
```

Run the server:

```bash
gabriel          # or: python -m src.main --port 8080
```

Open `http://127.0.0.1:8080` in your browser and paste the security token printed in the terminal. Start your CLI agent in another terminal — Gabriel auto-detects the newest transcript and begins tailing.

> **Desktop mode (optional):** `python src/run.py` launches the same UI inside a pywebview window instead of a browser tab.

## 🖥️ Dashboard

| View | What it does |
|---|---|
| 💬 Control Center | Split view: live agent terminal cards (grid) + side-brain chat with quick prompts, model switch, attach-snapshot / keep-history toggles, KB merge & export |
| 📡 Agent Radar | Agent list with lock-to-agent, sortable by activity / volume, real stats-driven telemetry |
| 📖 Knowledge Base | Global insight graph (click a card to load the draft) + editor with markdown preview and "Copy Injection Command" |
| ⚙️ Settings | OpenAI-compatible endpoint config, merge strategy, language, token management |

## 📡 API Overview

All `/api/*` endpoints require the token via the `X-Gabriel-Token` header; the WebSocket uses `?token=` (both compared constant-time).

| Endpoint | Description |
|---|---|
| `GET /api/ping` · `GET /api/health` | Liveness & tailer heartbeat |
| `GET/POST /api/config` | Read / atomically update provider settings |
| `POST /api/auth/ticket` | One-time WS auth ticket |
| `GET /api/agents` | Active agent sessions (path, mtime, steps) |
| `GET /api/knowledge` · `GET/POST /api/kb` | Knowledge base listing / CRUD |
| `POST /api/kb/feedback` | Weighted re-ranking of KB entries |
| `GET /api/stats` | Per-session turns / chars / est. cost |
| `GET /api/sessions` · `GET /api/sessions/{id}/transcript` | Session history |
| `POST /api/feedback` | User feedback (secrets redacted, stored locally) |
| `WS /ws` | Log stream, chat, KB merge, insight injection |

**MCP:** run `python -m src.mcp_server` as an stdio MCP server — exposes the `read_gabriel_kb` tool to external agents.

## 📁 Project Structure

```
Gabriel/
├── src/
│   ├── main.py            # FastAPI backend: REST + WebSocket + log tailer + FTS5 KB
│   ├── mcp_server.py      # stdio MCP server for external agents
│   └── run.py             # optional pywebview desktop wrapper
├── static/
│   ├── index.html         # dashboard UI (4 views + token login)
│   ├── script.js          # frontend logic (WS client, sanitized rendering, i18n)
│   ├── style.css          # Light Indigo theme (design tokens, parser CSS classes)
│   ├── splash.html        # boot splash
│   └── vendor/            # local copies of DOMPurify / marked / highlight.js — no CDN
├── tests/
│   └── test_gabriel.py    # 15 unit tests (auth, parsers, KB, WS, sessions, stats)
├── docs/                  # architecture, API reference, optimization plans
├── scripts/               # Windows autostart, snapshot generator
├── requirements.txt
├── setup.py               # `pip install -e .` → `gabriel` command
└── .env.example           # GABRIEL_TOKEN / OPENAI_API_KEY
```

## 🛠️ Development

```bash
# Run the full test suite (pytest)
venv\Scripts\python.exe -m pytest tests/ -q

# Code linter check (ruff)
venv\Scripts\python.exe -m ruff check src tests

# Frontend syntax check
node --check static/script.js
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and [docs/](docs/) for the architecture & API reference.

## 🔒 Security Notes

- Every API route is behind the `verify_token` dependency; the WebSocket rejects bad tokens with code 1008 before accepting.
- All log/chat content is sanitized with a locally vendored DOMPurify before touching `innerHTML` (fallback: plain text).
- Runtime artifacts (`knowledge.db`, `config.json`, `Gabriel_Insight.md`, logs, `.env`) are git-ignored; API keys are kept in the environment only.
- No telemetry, no external calls — everything runs strictly local.

## 📄 License

AGPL-3.0 — see [LICENSE](LICENSE).
