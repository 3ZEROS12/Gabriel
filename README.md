# Gabriel

A lightweight, non-intrusive GUI sidecar for CLI-based AI agents (e.g., Antigravity, Claude Code). 

Gabriel runs independently alongside your terminal, tailing agent logs in real-time to provide a dedicated dashboard for state monitoring, API configuration, and knowledge base management without blocking your CLI workflow.

## 🚀 Quickstart

**Prerequisites:** Python 3.10+

1. **Clone & Install**
   ```bash
   git clone https://github.com/your-username/gabriel.git
   cd gabriel
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Copy the example environment file and optionally set a secure token:
   ```bash
   cp .env.example .env
   ```

3. **Run the Server**
   ```bash
   python src/main.py
   ```
   *The server will generate a session token (if not set in `.env`) and print a local URL (e.g., `http://127.0.0.1:8080/?token=...`). Click it to open the dashboard.*

4. **Connect**
   Start your CLI agent in a separate terminal. Gabriel will automatically detect the newest log file and begin tailing.

## ✨ Core Capabilities

*   **Zero-Intrusion Tailing:** Automatically detects and tails the most recent `.jsonl` or `.log` transcripts.
    *   **Privacy & Boundary Note:** Gabriel *only* scans for specific agent transcript files (e.g., inside `.gemini/antigravity-cli/brain/`). It does **not** read your generic system logs, browser history, or arbitrary files on your machine. All data processing is strictly local.
*   **FTS5 Knowledge Base:** Integrated SQLite with Full-Text Search (FTS5) for fast snippet retrieval and injection.
*   **MCP Support:** Includes a Model Context Protocol (MCP) server (`src/mcp_server.py`) for external tool integration.
*   **Secure Local Architecture:** Enforces token-based authentication on all API and WebSocket endpoints. Frontend rendering uses DOMPurify to mitigate log-based XSS.

## 🛠️ Development

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed setup and contribution guidelines.

### Running Tests
The test suite covers configuration, database operations, and authentication.
```bash
python -m unittest discover tests -v
```

## 📄 License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.
