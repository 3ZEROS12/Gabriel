# Gabriel

A lightweight, non-intrusive GUI sidecar for CLI-based AI agents (e.g., Antigravity, Claude Code, Cursor). 

Gabriel runs independently alongside your terminal, tailing agent logs in real-time to provide a dedicated dashboard for state monitoring, API configuration, and knowledge base management without blocking your CLI workflow.

## 🚀 Quickstart

**Prerequisites:** Python 3.10+

1. **Clone & Install**
   ```bash
   git clone https://github.com/your-username/gabriel.git
   cd gabriel
   pip install -e .
   ```

2. **Configure Environment**
   Copy the example environment file and optionally set a secure token:
   ```bash
   cp .env.example .env
   ```

3. **Run the Server**
   ```bash
   gabriel
   ```
   *The server will generate a session token (if not set in `.env`) and print a local URL (e.g., `http://127.0.0.1:8080`). Enter the token in the dashboard to connect.*

4. **Connect**
   Start your CLI agent in a separate terminal. Gabriel will automatically detect the newest log file and begin tailing.

## ✨ Core Capabilities

*   **Zero-Intrusion Tailing:** Automatically detects and tails the most recent `.jsonl` or `.log` transcripts from supported agents.
    *   **Privacy & Boundary Note:** Gabriel *only* scans for specific agent transcript files (e.g., inside `.gemini/antigravity-cli/brain/` or `.cursor/logs/`). All data processing is strictly local.
*   **Mission Control (Multi-Agent Grid):** Concurrently monitor multiple active agent sessions in a unified, interference-free CSS Grid dashboard.
*   **Active Knowledge Base (FTS5):** Integrated SQLite with Full-Text Search (FTS5). The engine extracts context keywords and *proactively* recommends historical solutions via toast notifications when you encounter similar errors.
*   **Secure Local Architecture:** Enforces token-based authentication on all API and WebSocket endpoints. Frontend rendering falls back safely to text content if DOMPurify is unavailable, preventing XSS.

## 🛠️ Development

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed setup and contribution guidelines.

### Running Tests
The test suite covers configuration, database operations, and authentication.
```bash
python -m unittest discover tests -v
```

## 📄 License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.
