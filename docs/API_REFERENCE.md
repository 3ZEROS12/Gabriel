# API Reference

Gabriel's backend is powered by FastAPI. All API routes and WebSockets require authentication via the `X-Gabriel-Token` header (or `?token=` query parameter for WebSockets).

## Security
If a request is unauthenticated or uses an invalid token, the server will return `403 Forbidden`.

---

## 📡 REST API Endpoints

### 1. Ping
Check if the Gabriel server is alive and reachable.
*   **Method**: `GET`
*   **Path**: `/api/ping`
*   **Returns**: `{"status": "ok"}`

### 2. Configuration (`/api/config`)
Manage the global AI provider settings (Base URL, API Key, Model name).
*   **GET**: Returns the current configuration settings.
*   **POST**: Updates the settings. Expects a JSON body matching the configuration schema. Does an atomic file write to `config.json`.

### 3. Knowledge Base (`/api/kb`)
Interact with the local FTS5 SQLite Knowledge Base.
*   **GET**: Retrieves the current insights/documents from the database.
*   **POST**: Inserts a new insight/document into the Knowledge Base. Expects `{"content": "..."}`.

---

## 🔌 WebSockets

### 1. Main Data Stream
*   **Path**: `/ws?token={your_secure_token}`
*   **Behavior**: Upon connection, the server sends a `context_update` packet with initial state. It then streams `log` packets (terminal updates) and `ai_response_chunk` packets in real-time.

## 🤖 Model Context Protocol (MCP)

Gabriel implements an MCP server (`src/mcp_server.py`) with the following tools:
*   `query_knowledge(query: str)`: Allows external agents to search Gabriel's FTS5 database via natural language keywords.
