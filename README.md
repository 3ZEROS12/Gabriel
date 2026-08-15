<p align="center">
  <img src="static/assets/pixel_q_rose_transparent.png" width="160" alt="Gabriel Mascot" style="margin-bottom: 8px;">
</p>

<h1 align="center">Gabriel 👼 (加百列)</h1>

<p align="center">
  <strong>The Zero-Intrusion Desktop GUI Sidecar & Cognitive Sandbox for CLI AI Agents.</strong><br>
  <em>"Keep the main flow unbroken; never lose the details."</em>
</p>

<p align="center">
  <a href="README_CN.md">🇨🇳 中文文档</a> •
  <a href="#-quick-start">🚀 Quick Start</a> •
  <a href="#-key-features">✨ Key Features</a> •
  <a href="#-the-origin-story">💡 Origin Story</a> •
  <a href="docs/LAUNCH_KIT.md">📢 Launch Kit</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License: AGPL-3.0"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/Python-3.10+-brightgreen.svg" alt="Python 3.10+"></a>
  <a href="tests/test_gabriel.py"><img src="https://img.shields.io/badge/Tests-39%20Passed-success.svg" alt="Tests: 39 Passed"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/Code%20Style-Ruff-000000.svg" alt="Code Style: Ruff"></a>
  <img src="https://img.shields.io/badge/Local%20First-Zero%20CDN-orange.svg" alt="Zero CDN Local First">
</p>

---

## 💡 The Origin Story: Why Gabriel Exists

Gabriel wasn't born out of theoretical speculation. It originated from a very real, everyday learning dilemma:

> 📖 **The IELTS Breakthrough & Cognitive Dilemma**:  
> While preparing for the IELTS exam, I used **Gemini 3.1 Pro** as an interactive tutor to practice advanced sentences and vocabulary.  
> Whenever Gemini gave high-level feedback on my essay, I frequently encountered specific words or subtle grammatical nuances I didn't understand. But Gemini assumed I knew them and kept advancing the main curriculum.  
> If I interrupted the conversation to ask basic vocabulary questions, **it derailed the entire evaluation flow and polluted the context window**. If I switched to a browser to search, **I was swamped by noisy dictionary ads and lost my mental focus**.

When autonomous CLI coding agents (**Claude Code, Antigravity, Cursor, Aider, OpenHands**) arrived, I realized **every software developer is trapped in the exact same cognitive dilemma every day**:

```
Primary Task Flow (Terminal)          Secondary Sidecar Sandbox (Gabriel)
┌────────────────────────────────┐     ┌────────────────────────────────┐
│ Claude / Antigravity Agent     │     │ Gabriel Sidecar (1/4 Screen)   │
│ Running 20-min long refactor...│ ──> │ Passive Telemetry Stream       │
│                                │     │                                │
│ 💥 ConnectionReset / Traceback │ ──> │ 🔴 Error Detected Pulse        │
│                                │     │ 📌 One-Click Snapshot Pinning  │
│ [Main loop keeps running!]     │     │ 💡 Ask Sidecar: "Why this bug?"│
└────────────────────────────────┘     └────────────────────────────────┘
```

* When your CLI Agent runs a 20-minute autonomous refactoring loop, **you dare not interrupt it** or inject side questions that bloat its expensive context window.
* When hundreds of lines of raw tool calls flood your terminal, **spotting errors is painful**.
* When the session exits, **all hard-won debugging lessons and token bills vanish into thin air**.

**Gabriel is the dedicated 1/4-screen desktop GUI sidecar that solves this.** It silently monitors local agent traces in the background, offering an isolated auxiliary sandbox, glanceable status alerts, and post-session knowledge crystallization.

---

## ✨ Key Features

### 1. 🟢 Glanceable Cockpit & Smart Collapsible Logs
* **Mini Status Banner**: Displays live agent status (`🟢 Running` / `🟡 Reasoning` / `🔴 Error detected`) and step count at a single glance.
* **Auto-Collapsible Details (`<details class="log-fold">`)**: Compresses verbose, multi-line tool outputs into single-line summaries (`▶ 🛠️ [Tool Output] (240 chars)`). Automatically expands and highlights errors in red.

### 2. 📌 Zero-Friction Error Snapshot Pinning
* Spot a tricky error or curious step in the terminal? Click **`📌 Pin Last Error`** or **`⚡ Pin Current Step`**.
* Gabriel extracts the exact trace snippet, mounts it above your prompt, and queries your auxiliary model (e.g., DeepSeek, GPT-4o-mini, Local Ollama) **without touching or polluting the main agent's terminal**.

### 3. 📊 Post-Session War Report & Token Ledger (`/digest`)
* Type `/digest` or click **`📊 War Report`** to generate an instant, structured Post-Mortem Markdown summary:
  * 🎯 **Core Goal & Completion State**
  * 🛠️ **Key Execution Paths & Touched Files**
  * ⚠️ **Bottlenecks & Root Causes**
  * 💰 **Token Consumption & Cost Breakdown**
  * 💾 **One-Click Save to Knowledge Base** (`knowledge.db`)

### 4. 🚢 Multi-Agent Fleet Tab Bar
* Running multiple agents concurrently? Gabriel's Linear-style **Fleet Tab Bar** automatically tracks all active sessions:
  * `⚡ Auto-Follow` (Follows the newest active terminal)
  * `[🟢 Antigravity]` `[🟣 Claude Code]` `[⚡ Aider]` `[🤖 OpenHands]` `[✨ Gemini CLI]`
  * One-click tab switching to lock onto any specific session.

### 5. 📐 Mini Pill Capsule Mode (`Ctrl + M`)
* Shrinks the entire 1/4 screen UI into an unobtrusive 36px floating capsule at the edge of your screen.
* Unobtrusive during deep coding flow; pulses gently only when attention is needed.

### 6. 🧠 Dual RRF Hybrid Knowledge Base (FTS5 + Vector)
* Built-in `sqlite-vec` semantic embeddings + `jieba` FTS5 keyword search fused via Reciprocal Rank Fusion (RRF).
* Automatically suggests historical solutions when similar errors reoccur across projects.

### 7. 🛡️ 100% Local-First & Zero CDN
* Zero external CDN dependencies (bundled fonts, local Marked.js, local Highlight.js, local DOMPurify).
* Strict CSP security headers and token authentication.

---

## 🚀 Quick Start

### Method 1: Windows Standalone (No Python Setup Required)
1. Download `Gabriel-v4.0.0-Windows.zip` from [GitHub Releases](https://github.com/3ZEROS12/Gabriel/releases).
2. Extract and double-click `Gabriel.exe`.

---

### Method 2: From Source (Python 3.10+)

```bash
# 1. Clone repository
git clone https://github.com/3ZEROS12/Gabriel.git
cd Gabriel

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
pip install -e .              # Optional: install `gabriel` CLI globally

# 4. Launch Gabriel
gabriel                        # Or: python -m src.main --port 8080
```

* **Desktop Mode**: Run `python src/run.py` to open Gabriel inside a frameless native desktop window.
* **Browser Access**: Open `http://127.0.0.1:8080` with the random security token printed in the terminal.

---

## 🔌 Supported CLI Agents & Ecosystem

Gabriel passively tails local trajectory files without requiring any IDE extensions or proxy configurations:

| Agent | Target Trajectory Logs | Parser Engine |
| :--- | :--- | :--- |
| **Antigravity** | `~/.gemini/antigravity-cli/brain/*/logs/*.jsonl` | `AntigravityParser` |
| **Claude Code** | `~/.claude/projects/*/*.jsonl`, `~/.claude/logs/*.jsonl` | `ClaudeCodeParser` |
| **Cursor CLI** | `~/.cursor/logs/*.log`, `~/.config/Cursor/logs/*.log` | `CursorParser` |
| **Aider** | `.aider.chat.history.md`, `.aider.input.history` | `AiderParser` |
| **OpenHands** | `~/.openhands/logs/*.jsonl`, `~/.openhands/sessions/*/*.jsonl` | `OpenHandsParser` |
| **Gemini CLI** | `~/.gemini/logs/*.jsonl`, `~/.gemini/transcripts/*.jsonl` | `GeminiCLIParser` |
| **Plain Logs** | Standard stdout/stderr text files | `PlainTextFallbackParser` |

---

## ⌨️ Shortcuts & Hotkeys

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + M` | Toggle Mini Pill Capsule Mode / Full 1/4 Screen |
| `Ctrl + [` | Toggle Left Sidebar Fold / Expand |
| `Ctrl + B` | Toggle Terminal Context Panel Fold / Expand |
| `Ctrl + Enter` | Send Chat Prompt to Auxiliary Brain |
| `/digest` or `/d` | Generate Instant Post-Session War Report |
| `/clear` | Clear Auxiliary Chat History |
| `/help` | Open Keyboard Shortcuts & Guidance Modal |

---

## 🛡️ Quality & Test Suite

Gabriel is engineered with rigorous automated testing and static analysis:

```bash
# Run 39 automated unit & integration tests
pytest tests/ -q

# Run Ruff linter
ruff check src tests

# Verify zero CDN frontend syntax
node --check static/script.js static/icons.js
```

---

## 📄 License

Gabriel is licensed under the [AGPL-3.0 License](LICENSE).
