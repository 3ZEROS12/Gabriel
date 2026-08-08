"""Gabriel MCP server — official MCP Python SDK (v2).

Exposes Gabriel's local SQLite FTS5 knowledge base to external agents
(Claude Code, Cursor, Antigravity, ...) via the Model Context Protocol.

Run:
    python -m src.mcp_server            # stdio (default — Claude Code / Cursor)
    python -m src.mcp_server --http     # Streamable HTTP (experimental)

Test with the MCP Inspector:
    uvx mcp dev src/mcp_server.py
"""
import argparse
import os
import sqlite3
import time

from mcp.server import MCPServer
from src.main import save_insight, init_schema, check_active_kb, search_kb, ROOT_DIR

DB_PATH = os.path.join(ROOT_DIR, "knowledge.db")

mcp = MCPServer(
    "gabriel-kb",
    title="Gabriel Knowledge Base",
    description="Read and search insights from Gabriel's local SQLite FTS5 knowledge base.",
    version="2.0.0",
)


@mcp.tool(
    name="read_gabriel_kb",
    description=(
        "Search Gabriel's knowledge base for insights matching a query. "
        "Returns up to 5 most relevant entries using FTS5 + Vector RRF search + feedback re-ranking, "
        "or the 5 latest if no query is given. Use this to recall previously solved problems and their fixes."
    ),
)
def read_gabriel_kb(query: str = "") -> str:
    """Read the latest or query-matched insights from Gabriel's Knowledge Base."""
    try:
        if query and query.strip():
            hits = search_kb(query.strip(), limit=5)
            if hits:
                return "\n\n".join(h[1] for h in hits)
            return "No insights found."

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM insights ORDER BY timestamp DESC LIMIT 5")
        rows = cursor.fetchall()
        conn.close()
        return "\n\n".join(r["content"] for r in rows) if rows else "No insights found."
    except Exception as e:
        return f"Error reading Gabriel knowledge base: {e}"


@mcp.tool(
    name="add_gabriel_insight",
    description=(
        "Add a new insight to Gabriel's Knowledge Base. "
        "Accepts raw text or structured insights ({problem, cause, solution, tags}). "
        "Automatically indexed via jieba FTS5 and vector embeddings."
    ),
)
def add_gabriel_insight(content: str) -> str:
    """Write an insight to Gabriel's Knowledge Base."""
    if not content or not content.strip():
        return "Error: content cannot be empty."
    try:
        insight_id = save_insight(content.strip())
        return f"已入库 insight #{insight_id}"
    except Exception as e:
        return f"Error saving insight: {e}"


@mcp.tool(
    name="report_agent_stuck",
    description=(
        "Report when an agent is stuck, in a loop, or encountering a blocking issue. "
        "Persists the report context into Gabriel's database and checks for matching historical solutions."
    ),
)
def report_agent_stuck(agent: str, context: str) -> str:
    """Record a stuck status report from an external agent."""
    try:
        conn = sqlite3.connect(DB_PATH)
        init_schema(conn)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO stuck_reports (agent, context, ts) VALUES (?, ?, ?)",
            (agent or "unknown", context or "", time.time()),
        )
        conn.commit()
        conn.close()

        kb_hit = check_active_kb(context or "")
        if kb_hit and kb_hit.get("content"):
            return f"Reported stuck status for agent '{agent}'.\n📌 历史方案: {kb_hit['content']}"
        return f"Reported stuck status for agent '{agent}'."
    except Exception as e:
        return f"Error reporting stuck status: {e}"


@mcp.tool(
    name="get_session_summary",
    description=(
        "Get telemetry summary and recent status for an active or recent agent session. "
        "Provide agent_path to target a specific session, or omit for the latest session."
    ),
)
def get_session_summary(agent_path: str = "") -> str:
    """Get session summary telemetry (turns, chars, est_cost, tokens, waiting state)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        init_schema(conn)
        cursor = conn.cursor()
        if agent_path and agent_path.strip():
            cursor.execute(
                "SELECT * FROM session_meta WHERE path = ? ORDER BY ts DESC LIMIT 1",
                (agent_path.strip(),),
            )
        else:
            cursor.execute("SELECT * FROM session_meta ORDER BY ts DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if not row:
            return "No session telemetry records found."

        res = dict(row)
        summary = (
            f"Agent: {res.get('agent_name', 'unknown')}\n"
            f"Path: {res.get('path', '')}\n"
            f"Turns: {res.get('turns', 0)}\n"
            f"Chars: {res.get('chars', 0)}\n"
            f"Est Cost: ${res.get('est_cost', 0.0):.6f}\n"
            f"Input Tokens: {res.get('input_tokens', 0)}\n"
            f"Output Tokens: {res.get('output_tokens', 0)}\n"
            f"Cache Read Tokens: {res.get('cache_read_tokens', 0)}\n"
            f"Cache Creation Tokens: {res.get('cache_creation_tokens', 0)}"
        )
        return summary
    except Exception as e:
        return f"Error getting session summary: {e}"


def main():
    parser = argparse.ArgumentParser(description="Gabriel MCP server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run with Streamable HTTP transport (default: stdio)",
    )
    args = parser.parse_args()
    if args.http:
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
