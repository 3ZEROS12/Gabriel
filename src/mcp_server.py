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

from mcp.server import MCPServer

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge.db")

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
        "Returns up to 5 most relevant entries, or the 5 latest if no query is given. "
        "Use this to recall previously solved problems and their fixes."
    ),
)
def read_gabriel_kb(query: str = "") -> str:
    """Read the latest or query-matched insights from Gabriel's Knowledge Base (FTS5)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            if query and query.strip():
                # Wrap in double quotes to neutralize FTS5 special characters.
                safe_query = f'"{query.strip().replace(chr(34), chr(34) * 2)}"'
                cursor.execute(
                    "SELECT content FROM insights_fts WHERE insights_fts MATCH ? "
                    "ORDER BY rank LIMIT 5",
                    (safe_query,),
                )
            else:
                cursor.execute(
                    "SELECT content FROM insights_fts ORDER BY timestamp DESC LIMIT 5"
                )
        except sqlite3.OperationalError:
            # FTS syntax still failed (e.g. CJK tokenization): fall back to latest.
            cursor.execute(
                "SELECT content FROM insights_fts ORDER BY timestamp DESC LIMIT 5"
            )
        rows = cursor.fetchall()
        conn.close()
        return "\n\n".join(r["content"] for r in rows) if rows else "No insights found."
    except Exception as e:  # pragma: no cover - defensive for DB unavailability
        return f"Error reading Gabriel knowledge base: {e}"


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
