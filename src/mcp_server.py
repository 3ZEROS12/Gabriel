import json
import sys
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge.db")

def handle_request(request):
    try:
        if request.get("method") == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "gabriel-kb", "version": "1.0.0"}
                }
            }
            
        elif request.get("method") == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": [{
                        "name": "read_gabriel_kb",
                        "description": "Reads the latest insights from Gabriel's Knowledge Base (FTS5).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Optional search term"}
                            }
                        }
                    }]
                }
            }
            
        elif request.get("method") == "tools/call":
            params = request.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            
            if name == "read_gabriel_kb":
                query = args.get("query", "")
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if query:
                    # Sanitize for FTS5 by escaping double quotes and wrapping in quotes
                    # This prevents syntax errors from special characters like -, *, OR
                    safe_query = f'"{query.replace("\"", "\"\"")}"'
                    try:
                        cursor.execute("SELECT content FROM insights_fts WHERE content MATCH ? ORDER BY timestamp DESC LIMIT 5", (safe_query,))
                    except sqlite3.OperationalError:
                        # Fallback to simple query if FTS syntax still fails
                        cursor.execute("SELECT content FROM insights_fts ORDER BY timestamp DESC LIMIT 5")
                else:
                    cursor.execute("SELECT content FROM insights_fts ORDER BY timestamp DESC LIMIT 1")
                    
                rows = cursor.fetchall()
                conn.close()
                
                content = "\n\n".join([r["content"] for r in rows]) if rows else "No insights found."
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [{"type": "text", "text": content}],
                        "isError": False
                    }
                }
                
        # Unknown method
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32601, "message": "Method not found"}
        }
            
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32603, "message": str(e)}
        }

def main():
    """
    Gabriel MCP (Model Context Protocol) Server.
    Runs via STDIO to integrate seamlessly with Claude Code, Cursor, or Antigravity.
    """
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            pass

if __name__ == "__main__":
    main()
