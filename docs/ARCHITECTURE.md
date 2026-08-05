# Gabriel Architecture

Gabriel is designed as a **Zero-Intrusion GUI Sidecar**. It operates entirely independently of your primary CLI agent, utilizing file-system tailing and WebSocket broadcasting to achieve a real-time, responsive frontend.

## 🏗️ Core Components

### 1. The FastAPI Backend (`src/main.py`)
The backend is a lightweight, strictly-local Uvicorn server.
*   **Security First**: On startup, it generates a random 16-byte hex token. All HTTP endpoints and WebSocket connections strictly require this token via the `X-Gabriel-Token` header or URL parameter.
*   **Zero-Intrusion Tailing (`EventBroker`)**: Gabriel monitors a specific local directory (e.g., `.gemini/antigravity-cli/brain`) for `.jsonl` or `.log` transcripts. It does not hook into PTY, STDOUT, or terminal APIs, meaning it literally cannot crash your main CLI agent.
*   **WebSocket Pub/Sub**: When new lines are detected in the transcript, the `EventBroker` parses them and broadcasts them to all connected frontend clients via WebSockets.

### 2. The SQLite FTS5 Knowledge Base
Gabriel includes a fully-functional Knowledge Base powered by SQLite's FTS5 (Full-Text Search) extension.
*   **Schema**: A virtual table `insights_fts` stores markdown-formatted insights.
*   **Concurrency**: Designed with `check_same_thread=False` to handle async FastAPI threads safely.
*   **Performance**: FTS5 allows Gabriel to search thousands of snippets in milliseconds without the overhead of external vector databases.

### 3. The Vanilla Frontend (`static/`)
To keep the project lightweight and maintainable, the MVP uses a Vanilla JS frontend.
*   **DOMPurify**: All incoming logs and Markdown strings are sanitized before being assigned to `innerHTML`, completely neutralizing XSS risks.
*   **No Heavy Frameworks**: (Currently) no React, Vue, or Webpack. Just standard HTML/CSS/JS.

### 4. MCP Server (`src/mcp_server.py`)
Gabriel exposes its Knowledge Base via the **Model Context Protocol (MCP)**.
*   This allows other AI agents (like Claude or Cursor) to dynamically query Gabriel's SQLite database to retrieve insights you've saved.

## 🔄 Data Flow (Log Tailing)

1. Main CLI Agent (e.g., `agy`) writes to `transcript.jsonl`.
2. `EventBroker` (in `main.py`) detects file modification via a polling/stat loop.
3. `EventBroker` reads the new lines and parses the JSON.
4. `EventBroker` broadcasts `{type: "log", content: "..."}` to the WebSocket.
5. `script.js` receives the message, sanitizes it with `DOMPurify`, and appends it to the DOM.
