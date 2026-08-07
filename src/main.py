import os
import uvicorn
import asyncio
import glob
import time
import sqlite3
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, status, Security, Depends
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import json
import logging
import secrets
from openai import AsyncOpenAI
import re
from collections import Counter

import traceback
from logging.handlers import RotatingFileHandler

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("gabriel")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    "logs/gabriel.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()
    logger.info("EventBroker started.")
    asyncio.create_task(async_log_tailer())
    yield

app = FastAPI(title="Gabriel Control Center", lifespan=lifespan)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # [Point 20] Edge Caching: Add Cache-Control for static assets
    if request.url.path.startswith("/static"):
        if "v" in request.query_params or "hash" in request.query_params:
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        else:
            response.headers["Cache-Control"] = "public, max-age=3600"
        
    logger.info(f"{request.method} {request.url.path} - Completed in {process_time:.4f}s")
    return response

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(ROOT_DIR, "static")), name="static")

CONFIG_FILE = os.path.join(ROOT_DIR, "config.json")
DEFAULT_CONFIG = {
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "api_key": "",
    "model": "gpt-4o-mini",
    "target_agent": "auto",
    "price_input_per_m": 1.0,
    "price_output_per_m": 3.0
}

import copy
import shutil
import tempfile
import logging

def init_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS insights (id INTEGER PRIMARY KEY, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    try:
        cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS insights_fts USING fts5(content, timestamp)")
    except Exception:
        pass
    cursor.execute("CREATE TABLE IF NOT EXISTS kb_feedback (id INTEGER PRIMARY KEY, insight_id INTEGER, action TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS session_meta (id INTEGER PRIMARY KEY, agent_name TEXT, path TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP, turns INTEGER DEFAULT 0, chars INTEGER DEFAULT 0, est_cost REAL DEFAULT 0.0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY, agent_path TEXT, role TEXT, content TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
    
    for col_def in ["turns INTEGER DEFAULT 0", "chars INTEGER DEFAULT 0", "est_cost REAL DEFAULT 0.0"]:
        try:
            cursor.execute(f"ALTER TABLE session_meta ADD COLUMN {col_def}")
        except Exception:
            pass
            
    conn.commit()

def init_db():
    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    conn = sqlite3.connect(db_path)
    init_schema(conn)
    conn.close()

init_db()

def load_config():
    current_config = copy.deepcopy(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                if isinstance(cfg, dict):
                    current_config.update(cfg)
        except Exception as e:
            logging.error(f"Failed to load config: {e}. Falling back to default.")
            try:
                shutil.copy(CONFIG_FILE, CONFIG_FILE + ".corrupt.bak")
            except: pass
    return current_config

def save_config(cfg):
    temp_fd, temp_path = tempfile.mkstemp(dir=ROOT_DIR, prefix="cfg_tmp_")
    safe_cfg = copy.deepcopy(cfg)
    safe_cfg.pop("api_key", None)
        
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            json.dump(safe_cfg, f, indent=4, ensure_ascii=False)
        shutil.move(temp_path, CONFIG_FILE)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

config = load_config()

# System prompt shared by all chat sessions (single source of truth)
SYSTEM_PROMPT = (
    "You are Gabriel, an elite, non-intrusive AI side-screen companion and engineering supervisor. "
    "Your core directive is to observe the main AI agent's execution logs (Terminal Snapshot) and answer "
    "the human user's queries WITHOUT interrupting the main agent's context. \n\nPERSONA & CAPABILITIES:\n"
    "1. Parallel Querying: Answer user questions (definitions, code explanations, logic checks) based on the "
    "logs without polluting the main context.\n2. Real-time Debugging: If the user asks about an error or "
    "stall, diagnose the stack trace deeply and provide actionable fixes.\n3. Process Auditing: Act as a "
    "QA/Supervisor. Evaluate if the agent's current strategy is correct.\n4. Strict Conciseness: You are a "
    "side-screen. Responses must be sharp, highly formatted (use markdown, bolding, code blocks), and free "
    "of filler words. Jump straight to the insight."
)

# OpenAI Client singleton
from dotenv import load_dotenv
load_dotenv()

def get_ai_client():
    if not hasattr(get_ai_client, "_client"):
        get_ai_client._client = AsyncOpenAI(
            base_url=config.get("base_url") or "https://api.openai.com/v1",
            api_key=os.environ.get("OPENAI_API_KEY") or config.get("api_key") or "dummy"
        )
    return get_ai_client._client

current_contexts = {}
last_file = None

class ConfigModel(BaseModel):
    base_url: str
    api_key: str
    model: str
    target_agent: str
    price_input_per_m: float = 1.0
    price_output_per_m: float = 3.0

# --- Security ---
# Read from env if present (for persistent setups), otherwise generate randomly for session
API_KEY = os.environ.get("GABRIEL_TOKEN", secrets.token_hex(16))
print(f"\n=======================================================")
print(f"👼 Gabriel is starting up!")
print(f"🔐 Security Token Generated. Please use this token to login:")
print(f"Token: {API_KEY}")
print(f"Access the Control Center at: http://127.0.0.1:8080")
print(f"=======================================================\n")

from fastapi import Header
async def verify_token(x_gabriel_token: str = Header(None)):
    if not x_gabriel_token or not secrets.compare_digest(x_gabriel_token, API_KEY):
        logger.warning(f"Unauthorized API access attempt or missing token.")
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_gabriel_token

# --- Message Broker (Pub/Sub) ---
class EventBroker:
    def __init__(self):
        self.subscribers = set()
        self.queue = asyncio.Queue()
        self._task = None

    async def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._process_queue())

    async def subscribe(self, websocket: WebSocket):
        self.subscribers.add(websocket)

    async def unsubscribe(self, websocket: WebSocket):
        if websocket in self.subscribers:
            self.subscribers.remove(websocket)

    async def publish(self, message: str):
        await self.queue.put(message)

    async def _process_queue(self):
        while True:
            message = await self.queue.get()
            subs = list(self.subscribers)
            if subs:
                tasks = [sub.send_text(message) for sub in subs]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                dead_sockets = {sub for sub, res in zip(subs, results) if isinstance(res, Exception)}
                for dead in dead_sockets:
                    await self.unsubscribe(dead)
            self.queue.task_done()

broker = EventBroker()

from fastapi import APIRouter
api_router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])

tailer_last_heartbeat = {"timestamp": None, "status": "starting"}

@api_router.get("/health")
async def health_check():
    if tailer_last_heartbeat["timestamp"] is None:
        return JSONResponse({"status": "starting"}, status_code=503)
    stale = time.time() - tailer_last_heartbeat["timestamp"] > 30
    return JSONResponse({
        "status": "stale" if stale else "healthy",
        "last_heartbeat": tailer_last_heartbeat["timestamp"]
    }, status_code=503 if stale else 200)

active_tickets = {}

@api_router.post("/auth/ticket")
async def create_auth_ticket():
    now = time.time()
    for t, exp in list(active_tickets.items()):
        if now > exp:
            active_tickets.pop(t, None)
    ticket = secrets.token_hex(16)
    active_tickets[ticket] = now + 300
    return {"ticket": ticket}

@api_router.get("/ping")
async def ping():
    return {"status": "ok"}

@api_router.get("/config")
async def get_config():
    cfg = load_config()
    api_key = cfg.get("api_key", "")
    if api_key and len(api_key) > 8:
        cfg["api_key"] = api_key[:3] + "****" + api_key[-3:]
    return JSONResponse(cfg)

@api_router.post("/config")
async def update_config(cfg: ConfigModel):
    global config
    try:
        new_cfg = cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict()
        if new_cfg.get("api_key") == "" or "****" in new_cfg.get("api_key", ""):
            new_cfg["api_key"] = config.get("api_key", "")
        config.update(new_cfg)
        save_config(config)
        
        # Reset cached client if config changed
        if hasattr(get_ai_client, "_client"):
            delattr(get_ai_client, "_client")
            
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@api_router.get("/knowledge")
def get_knowledge():
    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    if not os.path.exists(db_path):
        return {"status": "success", "data": []}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Ensure table exists first just in case
        cursor.execute("CREATE TABLE IF NOT EXISTS insights (id INTEGER PRIMARY KEY, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("SELECT content, strftime('%s', timestamp) FROM insights ORDER BY timestamp DESC LIMIT 50")
        rows = cursor.fetchall()
        
        data = [{"content": row[0], "timestamp": float(row[1])} for row in rows]
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error fetching knowledge: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if 'conn' in locals():
            conn.close()

_agent_scan_cache = {}

def _scan_active_agents_sync():
    patterns = ParserRegistry.get_all_scan_patterns()
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    
    agents = []
    current_time = time.time()
    for f in files:
        try:
            mtime = os.path.getmtime(f)
            ctime = os.path.getctime(f)
            if current_time - mtime < 86400: # Active in last 24h
                cache_entry = _agent_scan_cache.get(f)
                if cache_entry and cache_entry['mtime'] == mtime:
                    steps = cache_entry['steps']
                    first_line = cache_entry['first_line']
                else:
                    last_pos = cache_entry['pos'] if cache_entry else 0
                    current_steps = cache_entry['steps'] if cache_entry else 0
                    try:
                        with open(f, 'r', encoding='utf-8') as f_obj:
                            size = os.fstat(f_obj.fileno()).st_size
                            pos = last_pos if last_pos <= size else 0
                            base_steps = current_steps if pos == last_pos else 0
                            f_obj.seek(pos)
                            new_steps = sum(1 for _ in f_obj)
                            steps = base_steps + new_steps
                            new_pos = f_obj.tell()
                            if not cache_entry or not cache_entry['first_line']:
                                f_obj.seek(0)
                                first_line = f_obj.readline()
                            else:
                                first_line = cache_entry['first_line']
                    except:
                        steps = current_steps
                        new_pos = last_pos
                        first_line = ""

                    _agent_scan_cache[f] = {'mtime': mtime, 'steps': steps, 'pos': new_pos, 'first_line': first_line}
                    
                parser = ParserRegistry.get_parser(f, first_line)
                name = parser.get_agent_name(f) if hasattr(parser, 'get_agent_name') else os.path.basename(f)
                
                agents.append({"name": name, "path": f, "mtime": mtime, "ctime": ctime, "steps": steps})
        except:
            pass
            
    # Cleanup old entries
    active_paths = set(files)
    keys_to_remove = [k for k in _agent_scan_cache if k not in active_paths]
    for k in keys_to_remove:
        del _agent_scan_cache[k]
        
    return agents

async def scan_active_agents():
    return await asyncio.to_thread(_scan_active_agents_sync)

@api_router.get("/agents")
async def get_agents():
    return JSONResponse(await scan_active_agents())

class FeedbackModel(BaseModel):
    issue: str
    context: str

def redact_secrets(text: str) -> str:
    # Mask common secrets
    text = re.sub(r'sk-[a-zA-Z0-9]{20,}', 'sk-[REDACTED]', text)
    text = re.sub(r'Bearer\s+[a-zA-Z0-9\-\._~\+]+', 'Bearer [REDACTED]', text)
    return text

@api_router.post("/feedback")
async def submit_feedback(data: FeedbackModel):
    feedback_file = os.path.join(ROOT_DIR, "user_feedback.jsonl")
    try:
        sanitized_context = redact_secrets(data.context)
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": time.time(), "issue": data.issue, "context": sanitized_context}) + "\n")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return {"status": "error"}

class KBModel(BaseModel):
    content: str

def get_db():
    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    try:
        yield conn
    finally:
        conn.close()

@api_router.get("/kb")
def get_kb(filter: str = None, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        if filter == "favorite":
            cursor.execute("""
                SELECT DISTINCT i.id, i.content, i.timestamp
                FROM insights i
                JOIN kb_feedback f ON i.id = f.insight_id
                WHERE f.action = 'favorite'
                AND i.id NOT IN (
                    SELECT insight_id FROM kb_feedback WHERE action = 'unfavorite'
                )
                ORDER BY i.timestamp DESC
            """)
            rows = cursor.fetchall()
            items = [{"id": row["id"], "content": row["content"], "timestamp": str(row["timestamp"])} for row in rows]
            return JSONResponse({"favorites": items})

        # Fallback to normal table if FTS is empty for backward compatibility
        cursor.execute("SELECT content FROM insights_fts ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            cursor.execute("SELECT content FROM insights ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
        if row:
            return JSONResponse({"content": row["content"]})
    except Exception as e:
        logger.error(f"KB Get Error: {e}")
    return JSONResponse({"content": "", "favorites": []})

@api_router.post("/kb")
def update_kb(data: KBModel, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO insights (content) VALUES (?)", (data.content,))
        # Insert into FTS5 high-performance index
        cursor.execute("INSERT INTO insights_fts (content, timestamp) VALUES (?, CURRENT_TIMESTAMP)", (data.content,))
        db.commit()
        
        # Keep a markdown mirror for backward compatibility and easy human reading
        kb_path = os.path.join(ROOT_DIR, "Gabriel_Insight.md")
        with open(kb_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n## Insight ({time.strftime('%Y-%m-%d %H:%M:%S')})\n{data.content}")
            
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"KB Post Error: {e}")
        return {"status": "error", "message": str(e)}

class KBFeedbackModel(BaseModel):
    insight_id: int
    action: str

@api_router.post("/kb/feedback")
def submit_kb_feedback(data: KBFeedbackModel, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO kb_feedback (insight_id, action) VALUES (?, ?)", (data.insight_id, data.action))
        db.commit()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@api_router.get("/stats")
def get_stats(db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, agent_name, path, ts, turns, chars, est_cost FROM session_meta ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        
        total_turns = sum(r["turns"] or 0 for r in rows)
        total_chars = sum(r["chars"] or 0 for r in rows)
        total_cost = sum(r["est_cost"] or 0.0 for r in rows)
        
        total_errors = 0
        total_tools = 0
        for cache in _transcript_cache.values():
            if not cache: continue
            full_text = "".join(list(cache.get('last_200_lines', [])))
            total_errors += len(re.findall(r'(?i)(error|exception|fail)', full_text))
            total_tools += len(re.findall(r'(?i)(tool_call|call|run_command|tool)', full_text))
            
        if not rows and _transcript_cache:
            for cache in _transcript_cache.values():
                if not cache: continue
                full_text = "".join(list(cache.get('last_200_lines', [])))
                total_chars += len(full_text)
                total_turns += len(re.findall(r'(?i)(assistant|agent|planner_response|claude)', full_text))
            price_in = config.get("price_input_per_m", 1.0)
            total_cost = (total_chars / 4) * price_in / 1e6
            
        return JSONResponse({
            "turns": total_turns,
            "errors": total_errors,
            "tools": total_tools,
            "cost": round(total_cost, 4),
            "sessions": [{
                "id": r["id"],
                "agent": r["agent_name"],
                "path": r["path"],
                "ts": str(r["ts"]),
                "turns": r["turns"] or 0,
                "chars": r["chars"] or 0,
                "est_cost": round(r["est_cost"] or 0.0, 4)
            } for r in rows]
        })
    except Exception as e:
        logger.error(f"Get Stats Error: {e}")
        return JSONResponse({"turns": 0, "errors": 0, "tools": 0, "cost": 0.0, "sessions": []})

@api_router.get("/sessions")
def get_sessions(db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, agent_name, path, ts, turns, chars, est_cost FROM session_meta ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        res = []
        for r in rows:
            path = r["path"]
            exists = os.path.exists(path)
            mtime = os.path.getmtime(path) if exists else 0
            res.append({
                "id": r["id"],
                "agent": r["agent_name"],
                "path": path,
                "ts": str(r["ts"]),
                "turns": r["turns"] or 0,
                "chars": r["chars"] or 0,
                "est_cost": r["est_cost"] or 0.0,
                "exists": exists,
                "mtime": mtime
            })
        return JSONResponse(res)
    except Exception as e:
        logger.error(f"Get Sessions Error: {e}")
        return JSONResponse([])

@api_router.get("/sessions/{session_id}/transcript")
def get_session_transcript(session_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT path, agent_name, ts FROM session_meta WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"status": "error", "message": "Session not found"}, status_code=404)
            
        path = row["path"]
        if not os.path.exists(path):
            return JSONResponse({"status": "error", "message": f"Log file at {path} no longer exists"}, status_code=404)
            
        rendered_html, raw_lines = _format_transcript_sync(path, is_initial=True)
        return JSONResponse({
            "status": "success",
            "id": session_id,
            "agent": row["agent_name"],
            "path": path,
            "ts": str(row["ts"]),
            "html": rendered_html,
            "total_lines": len(raw_lines)
        })
    except Exception as e:
        logger.error(f"Get Session Transcript Error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_target_transcript_file():
    if config["target_agent"] != "auto" and os.path.exists(config["target_agent"]):
        return config["target_agent"]
    
    agents = await scan_active_agents()
    if agents:
        agents.sort(key=lambda x: x["mtime"], reverse=True)
        return agents[0]["path"]
    return None

import html

class BaseParser:
    @staticmethod
    def get_scan_patterns() -> list:
        return []
        
    @staticmethod
    def get_agent_name(filepath: str) -> str:
        return os.path.basename(filepath)

    @staticmethod
    def identify(filepath: str, line: str) -> bool:
        return False
        
    @staticmethod
    def parse(line: str) -> str:
        return ""

class AntigravityParser(BaseParser):
    @staticmethod
    def get_scan_patterns() -> list:
        return [
            os.path.expanduser(r"~/.gemini/antigravity-cli/brain/*/logs/*.jsonl"),
            os.path.expanduser(r"~/.gemini/antigravity-cli/brain/*/.system_generated/logs/*.jsonl"),
            os.path.join(os.getcwd(), ".system_generated", "logs", "*.jsonl")
        ]

    @staticmethod
    def get_agent_name(filepath: str) -> str:
        parts = filepath.replace("\\", "/").split("/")
        for i, part in enumerate(parts):
            if part in ("brain", "logs") and i + 1 < len(parts):
                return f"antigravity ({parts[i+1][:8]})"
        return f"antigravity ({os.path.basename(filepath)})"

    @staticmethod
    def identify(filepath: str, line: str) -> bool:
        fp = filepath.lower()
        return "antigravity" in fp or ".system_generated" in fp or "transcript" in fp

    @staticmethod
    def parse(line: str) -> str:
        line = line.strip()
        if not line: return None
        try:
            data = json.loads(line)
            if not isinstance(data, dict):
                raise ValueError("JSON root is not an object")
                
            step_type = data.get("type")
            content = data.get("content", "")
            
            if isinstance(content, (dict, list)):
                content = json.dumps(content, ensure_ascii=False)
                
            content = str(content)
            safe_content = html.escape(content)
            
            tool_html = ""
            if data.get("tool_calls"):
                for tc in data["tool_calls"]:
                    t_name = html.escape(tc.get("name", "unknown_tool"))
                    t_args = html.escape(json.dumps(tc.get("arguments", {}))[:100])
                    tool_html += f'<div class="log-tool-call">⚡ Call: {t_name}({t_args}...)</div>'
            
            if step_type == "USER_INPUT":
                return f'<div class="log-entry"><span class="log-user">👤 [USER]:</span> <span class="log-text">{safe_content[:200]}...</span></div>'
            elif step_type == "PLANNER_RESPONSE":
                return f'<div class="log-entry"><span class="log-agent">🤖 [AGENT]:</span> <span class="log-text">{safe_content[:200]}...</span>{tool_html}</div>'
            elif step_type == "TOOL_RESPONSE":
                if len(safe_content) > 300:
                    safe_content = safe_content[:300] + "... (truncated)"
                return f'<div class="log-entry"><span class="log-tool">🛠️ [TOOL OUTPUT]:</span><br><span class="log-subtext">{safe_content}</span></div>'
            else:
                return f'<div class="log-entry"><span class="log-subtext">[{step_type}]:</span> <span class="log-text">{safe_content[:150]}...</span>{tool_html}</div>'
        except Exception as e:
            logger.warning(f"AntigravityParser parse warning: {e}. Degrading to plain text.")
            return PlainTextFallbackParser.parse(line)

class ClaudeCodeParser(BaseParser):
    @staticmethod
    def get_scan_patterns() -> list:
        return [
            os.path.expanduser(r"~/.claude/projects/*/*.jsonl"),
            os.path.expanduser(r"~/.claude/logs/*.jsonl"),
            os.path.expanduser(r"~/.claude_code/logs/*.jsonl"),
            os.path.join(os.getcwd(), ".claude", "logs", "*.jsonl"),
            os.path.join(os.getcwd(), ".claude", "logs", "*.log")
        ]

    @staticmethod
    def get_agent_name(filepath: str) -> str:
        return f"claude-code ({os.path.basename(filepath)})"

    @staticmethod
    def identify(filepath: str, line: str) -> bool:
        return ".claude" in filepath.lower() or "claude" in line.lower()
        
    @staticmethod
    def parse(line: str) -> str:
        line = line.strip()
        if not line: return None
        try:
            data = json.loads(line)
            if not isinstance(data, dict):
                raise ValueError("JSON root is not an object")
            msg_type = data.get("type") or data.get("role")
            if not msg_type:
                raise ValueError("Missing type/role field")
        except Exception as e:
            logger.warning(f"ClaudeCodeParser parse warning: {e}. Degrading to plain text.")
            return PlainTextFallbackParser.parse(line)
            
        content = data.get("content") or data.get("message") or data.get("text") or ""
        
        if isinstance(content, (dict, list)):
            content = json.dumps(content, ensure_ascii=False)
            
        content = str(content)
        safe_content = html.escape(content)
        
        if msg_type in ("user", "USER_INPUT"):
            return f'<div class="log-entry"><span class="log-user">👤 [USER]:</span> <span class="log-text">{safe_content[:200]}...</span></div>'
        elif msg_type in ("assistant", "agent", "PLANNER_RESPONSE", "model"):
            return f'<div class="log-entry"><span class="log-claude">🟣 [Claude]:</span> <span class="log-text">{safe_content[:200]}...</span></div>'
        elif msg_type in ("tool", "system", "TOOL_RESPONSE", "tool_call"):
            if len(safe_content) > 300:
                safe_content = safe_content[:300] + "... (truncated)"
            return f'<div class="log-entry"><span class="log-tool">🛠️ [TOOL]:</span><br><span class="log-subtext">{safe_content}</span></div>'
        else:
            return f'<div class="log-entry"><span class="log-claude">🟣 [Claude Code]:</span> <span class="log-text">{safe_content[:200]}...</span></div>'

class CursorParser(BaseParser):
    @staticmethod
    def get_scan_patterns() -> list:
        return [
            os.path.expanduser(r"~/.cursor/logs/*.log"),
            os.path.expanduser(r"~/.config/Cursor/logs/*.log"),
            os.path.join(os.getcwd(), ".cursor", "logs", "*.log"),
            os.path.join(os.getcwd(), ".cursor", "logs", "*.jsonl")
        ]

    @staticmethod
    def get_agent_name(filepath: str) -> str:
        return f"cursor ({os.path.basename(filepath)})"

    @staticmethod
    def identify(filepath: str, line: str) -> bool:
        return ".cursor" in filepath.lower()
        
    @staticmethod
    def parse(line: str) -> str:
        line = line.strip()
        if not line: return None
        try:
            data = json.loads(line)
            if not isinstance(data, dict):
                raise ValueError("JSON root is not an object")
            role = data.get("role") or data.get("type")
            if not role:
                raise ValueError("Missing role/type field")
        except Exception as e:
            logger.warning(f"CursorParser parse warning: {e}. Degrading to plain text.")
            safe_content = html.escape(line[:200])
            if line.startswith("User:"):
                return f'<div class="log-entry"><span class="log-user">👤 [USER]:</span> <span class="log-text">{safe_content[5:200]}...</span></div>'
            elif line.startswith("Cursor:"):
                return f'<div class="log-entry"><span class="log-cursor">🔵 [Cursor]:</span> <span class="log-text">{safe_content[7:200]}...</span></div>'
            return PlainTextFallbackParser.parse(line)
            
        content = data.get("content") or data.get("message") or data.get("text") or ""
        
        if isinstance(content, (dict, list)):
            content = json.dumps(content, ensure_ascii=False)
        content = str(content)
        safe_content = html.escape(content)
        
        if role in ("user", "USER_INPUT"):
            return f'<div class="log-entry"><span class="log-user">👤 [USER]:</span> <span class="log-text">{safe_content[:200]}...</span></div>'
        elif role in ("assistant", "agent", "model"):
            return f'<div class="log-entry"><span class="log-cursor">🔵 [Cursor]:</span> <span class="log-text">{safe_content[:200]}...</span></div>'
        elif role in ("tool", "system", "tool_call"):
            if len(safe_content) > 300:
                safe_content = safe_content[:300] + "... (truncated)"
            return f'<div class="log-entry"><span class="log-tool">🛠️ [TOOL]:</span><br><span class="log-subtext">{safe_content}</span></div>'
        else:
            return f'<div class="log-entry"><span class="log-cursor">🔵 [Cursor]:</span> <span class="log-text">{safe_content[:200]}...</span></div>'

class PlainTextFallbackParser(BaseParser):
    @staticmethod
    def identify(filepath: str, line: str) -> bool:
        return True # Catch-all
        
    @staticmethod
    def parse(line: str) -> str:
        if not line.strip(): return None
        # Strip ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_line = ansi_escape.sub('', line.rstrip('\r\n'))
        
        is_error = bool(re.search(r'(Error|Exception):', clean_line, re.IGNORECASE))
        style = "margin-bottom:4px; font-family:monospace; font-size:0.8em; white-space:pre-wrap; word-break:break-word;"
        if is_error:
            style += " color:#ef4444; background:rgba(239, 68, 68, 0.1); padding:2px 4px; border-radius:4px;"
        else:
            style += " color:#94a3b8;"
            
        display_line = clean_line[:4000] + ("..." if len(clean_line) > 4000 else "")
        return f'<div style="{style}">{html.escape(display_line)}</div>'

class ParserRegistry:
    parsers = [AntigravityParser, ClaudeCodeParser, CursorParser, PlainTextFallbackParser]
    
    @classmethod
    def get_all_scan_patterns(cls) -> list:
        patterns = []
        for p in cls.parsers:
            patterns.extend(p.get_scan_patterns())
        return patterns

    @classmethod
    def get_parser(cls, filepath: str, sample_line: str):
        for p in cls.parsers:
            if p.identify(filepath, sample_line):
                return p
        return PlainTextFallbackParser

_transcript_cache = {}

def _format_transcript_sync(filepath, is_initial=False):
    try:
        from collections import deque
        
        if filepath not in _transcript_cache or is_initial:
            _transcript_cache[filepath] = {
                'pos': 0,
                'first_line': "",
                'last_200_lines': deque(maxlen=200)
            }
            
        cache = _transcript_cache[filepath]
        
        with open(filepath, "r", encoding="utf-8") as f:
            size = os.fstat(f.fileno()).st_size
            if cache['pos'] > size:
                # File was truncated/rotated: restart tailing from the beginning.
                cache['pos'] = 0
                cache['first_line'] = ""
                cache['last_200_lines'].clear()
            f.seek(cache['pos'])
            new_lines = f.readlines()
            cache['pos'] = f.tell()
            
            if not cache['first_line'] and new_lines:
                cache['first_line'] = new_lines[0]
                
            for line in new_lines:
                cache['last_200_lines'].append(line)
                
        if not cache['first_line']:
            return "", []
        
        parser = ParserRegistry.get_parser(filepath, cache['first_line'])
        
        if is_initial:
            output = [f'<div class="log-header">[Agent 日志实时同步中... 渲染引擎: {parser.__name__}]</div>']
            lines_to_render = cache['last_200_lines']
        else:
            output = []
            lines_to_render = new_lines
            
        for line in lines_to_render:
            try:
                parsed = parser.parse(line)
                if parsed:
                    output.append(parsed)
            except:
                pass
        return "".join(output), cache['last_200_lines']
    except Exception as e:
        return f"Error reading log: {e}", []

async def format_transcript(filepath, is_initial=False):
    return await asyncio.to_thread(_format_transcript_sync, filepath, is_initial)

STOP_WORDS = {"this", "that", "with", "from", "your", "have", "what", "there", "their", "will", "would", "could", "should", "about", "which", "when", "where", "while", "these", "those", "using", "system", "message", "content", "response", "planner"}

def extract_touched_files(text: str) -> list:
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    files = re.findall(r'\b[\w-]+\.(?:py|js|ts|jsx|tsx|css|html|md|json)\b', clean_text, re.IGNORECASE)
    return list(set(files))

def extract_keywords(text: str, max_words=4) -> str:
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    
    # 1. Extract file names (e.g., main.py, script.js)
    files = re.findall(r'\b[\w-]+\.(?:py|js|ts|jsx|tsx|css|html|md|json)\b', clean_text, re.IGNORECASE)
    
    # 2. Extract CamelCase, PascalCase, or snake_case identifiers
    identifiers = re.findall(r'\b(?:[a-z]+_[a-z0-9_]+|[A-Z][a-z0-9]+[A-Z][a-z0-9a-zA-Z]*|[a-z]+[A-Z][a-z0-9a-zA-Z]*)\b', clean_text)
    
    # 3. Extract common error keywords
    errors = re.findall(r'\b(?:error|exception|traceback|fail(?:ed|ure)?|fatal|warn(?:ing)?)\b', clean_text, re.IGNORECASE)
    
    # Combine and normalize
    all_terms = [re.sub(r'[^\w\.\_\-]', '', w.lower()) for w in (files + identifiers + errors)]
    filtered = [w for w in all_terms if w not in STOP_WORDS and len(w) > 3]
    
    most_common = [w[0] for w in Counter(filtered).most_common(max_words)]
    
    # Escape quotes and wrap in quotes for robust FTS5 MATCH
    return " OR ".join(f'"{w}"' for w in most_common if w) if most_common else ""

def _compress_lines(lines: list, max_events: int = 40) -> list:
    if not lines:
        return []
    
    compressed = []
    prev_clean = None
    count = 0
    
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        truncated = stripped[:200]
        if truncated == prev_clean:
            count += 1
        else:
            if prev_clean is not None:
                if count > 1:
                    compressed.append(f"{prev_clean} (×{count})")
                else:
                    compressed.append(prev_clean)
            prev_clean = truncated
            count = 1
            
    if prev_clean is not None:
        if count > 1:
            compressed.append(f"{prev_clean} (×{count})")
        else:
            compressed.append(prev_clean)
            
    return compressed[-max_events:]

def build_snapshot(path: str, user_prompt: str) -> str:
    entry = _transcript_cache.get(path)
    if not entry:
        return f"--- Agent: {path} ---\nNo logs available."
    
    lines = list(entry.get('last_200_lines', []))
    if not lines:
        return f"--- Agent: {path} ---\nEmpty log."
        
    full_text = "".join(lines)
    
    # Extract metrics
    files = re.findall(r'\b[\w-]+\.(?:py|js|ts|jsx|tsx|css|html|md|json)\b', full_text, re.IGNORECASE)
    top_files = [f"{k}({v})" for k, v in Counter(files).most_common(5)]
    
    err_count = sum(1 for line in lines if re.search(r'(?i)(error|exception|fail)', line))
    
    tool_matches = re.findall(r'(?i)(?:tool_call|call|run_command|tool)[\s:\"\']+(\w+)', full_text)
    recent_tool = tool_matches[-1] if tool_matches else "None"
    
    # Determine scene status
    if check_waiting_status(lines):
        status_str = "等待输入"
    elif err_count >= 5:
        status_str = "疑似卡点"
    else:
        status_str = "运行中"
        
    # Output structure
    snapshot = f"--- Agent: {path} ---\n"
    snapshot += f"[现场] 状态: {status_str} | 最近工具: {recent_tool} | 改动文件Top5: {', '.join(top_files) if top_files else 'None'} | Error行: {err_count}\n"
    
    # Active KB hit if any
    try:
        kb_hit = check_active_kb(full_text)
        if kb_hit and isinstance(kb_hit, dict) and kb_hit.get("content"):
            snapshot += f"[命中历史] {kb_hit['content']}\n"
    except Exception:
        pass
        
    # Timeline (compressed)
    compressed_timeline = _compress_lines(lines, max_events=40)
    snapshot += f"[时间线] (最近 {len(compressed_timeline)} 事件):\n"
    for ev in compressed_timeline:
        snapshot += f"  • {ev}\n"
        
    is_full = "全文" in user_prompt or "full context" in user_prompt.lower()
    keep_lines = lines[-60:]
    if is_full:
        snapshot += f"[原始尾部] (最近 {len(keep_lines)} 行):\n"
        snapshot += "".join(keep_lines)
        
    logger.info(f"[SNAPSHOT] path={path} chars={len(snapshot)} lines={len(keep_lines)}")
    return snapshot

# Length guards for "full context" mode (snapshot mode stays cheap by design).
FULL_CONTEXT_PER_FILE_LIMIT = 200_000  # chars per agent
FULL_CONTEXT_TOTAL_LIMIT = 300_000     # chars total across all agents

def build_prompt_content(mode: dict, contexts: dict, user_prompt: str) -> str:
    """Build the context injected into the side-brain prompt.

    mode.context == "full"     -> feed the raw terminal context (length-capped)
    mode.context == "snapshot" -> (default) feed the compressed build_snapshot()

    The default keeps the current behavior: cheap, focused, non-polluting.
    Full mode is an opt-in escape hatch for deep diagnosis / whole-session audit.
    """
    use_full = (mode or {}).get("context") == "full"

    if use_full:
        parts = []
        for path, ctx in contexts.items():
            tail = ctx[-FULL_CONTEXT_PER_FILE_LIMIT:] if ctx else ""
            parts.append(f"--- Agent: {path} ---\n{tail}")
        combined = "\n".join(parts)
        if len(combined) > FULL_CONTEXT_TOTAL_LIMIT:
            combined = combined[-FULL_CONTEXT_TOTAL_LIMIT:]
        return f"Terminal Context(s):\n```\n{combined}\n```\n\nUser Question:\n{user_prompt}"

    snapshots = [build_snapshot(path, user_prompt) for path in contexts.keys()]
    combined = "\n\n".join(snapshots)
    return f"Terminal Snapshot(s):\n```\n{combined}\n```\n\nUser Question:\n{user_prompt}"


def check_active_kb(text: str):
    kw = extract_keywords(text)
    if not kw: return None
    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Get top 5 matches
        cursor.execute("SELECT rowid, content FROM insights_fts WHERE insights_fts MATCH ? ORDER BY rank LIMIT 5", (kw,))
        rows = cursor.fetchall()
        if not rows: return None
        
        # Ensure feedback table exists
        cursor.execute("CREATE TABLE IF NOT EXISTS kb_feedback (id INTEGER PRIMARY KEY, insight_id INTEGER, action TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
        
        best_row = None
        best_score = -9999
        
        for rowid, content in rows:
            cursor.execute("SELECT action FROM kb_feedback WHERE insight_id = ?", (rowid,))
            feedbacks = cursor.fetchall()
            
            useful_count = sum(1 for (a,) in feedbacks if a == "useful")
            useless_count = sum(1 for (a,) in feedbacks if a == "useless")
            favorite_count = sum(1 for (a,) in feedbacks if a == "favorite")
            unfavorite_count = sum(1 for (a,) in feedbacks if a == "unfavorite")
            
            effective_favorite = max(0, favorite_count - unfavorite_count)
            total_votes = useful_count + useless_count + effective_favorite
            
            if useless_count >= 2:
                score = -10.0
            else:
                base = 0.3
                delta = (useful_count - 0.8 * useless_count + 1.5 * effective_favorite) / max(1, total_votes) if total_votes > 0 else 0
                score = base + delta
            
            if score > best_score and score > -5.0:
                best_score = score
                best_row = (rowid, content)
                
        if best_row:
            return {"id": best_row[0], "content": best_row[1]}
    except Exception as e:
        logger.error(f"FTS Search error: {e}")
    finally:
        conn.close()
    return None

def check_waiting_status(lines: list) -> bool:
    if not lines:
        return False
    # Check the last 5 lines for awaiting keywords
    for line in reversed(lines[-5:]):
        try:
            data = json.loads(line)
            # Claude Code format
            if data.get("awaiting_reason") or data.get("type") == "permission":
                return True
            # Antigravity format (waiting_for_input step status or type)
            if data.get("status") == "waiting_for_input" or data.get("type") == "WAITING_FOR_INPUT" or data.get("state") == "waiting_for_input":
                return True
        except Exception:
            # plain text fallback
            line_str = line.lower()
            if "awaiting_reason" in line_str or "waiting for user" in line_str or "permission" in line_str or "waiting_for_input" in line_str:
                return True
    return False

async def async_log_tailer():
    global current_contexts
    last_mtimes = {}
    last_recommended_kbs = {}
    last_error_warnings = {}
    last_wait_state = {}
    last_wait_notified = {}
    active_tracking = set()
    
    while True:
        try:
            agents = await scan_active_agents()
            tailer_last_heartbeat["timestamp"] = time.time()
            tailer_last_heartbeat["status"] = "healthy"
            
            main_agent_path = await get_target_transcript_file()
            current_active = set()
            
            for agent in agents:
                target_file = agent["path"]
                current_mtime = agent["mtime"]
                agent_name = agent["name"]
                
                # If target_agent is auto, track ONLY the main agent. 
                # If target_agent is manual, track ONLY the manual target.
                if config.get("target_agent") == "auto":
                    if target_file != main_agent_path:
                        continue
                else:
                    if target_file != config.get("target_agent"):
                        continue
                        
                current_active.add(target_file)
                
                if target_file not in active_tracking:
                    active_tracking.add(target_file)
                    await broker.publish(json.dumps({"type": "agent_spawn", "agent": agent_name, "path": target_file}))
                    def insert_session():
                        try:
                            with sqlite3.connect(os.path.join(ROOT_DIR, "knowledge.db")) as conn:
                                conn.execute("INSERT INTO session_meta (agent_name, path) VALUES (?, ?)", (agent_name, target_file))
                                conn.commit()
                        except: pass
                    await asyncio.to_thread(insert_session)

                if current_mtime != last_mtimes.get(target_file, 0):
                    last_mtimes[target_file] = current_mtime
                    
                    is_initial = target_file not in current_contexts
                    new_html, last_lines = await format_transcript(target_file, is_initial)
                    kb_match = None
                    
                    if is_initial:
                        current_contexts[target_file] = new_html
                    else:
                        current_contexts[target_file] += new_html
                        if len(current_contexts[target_file]) > 500000:
                            current_contexts[target_file] = current_contexts[target_file][-500000:]

                    if last_lines:
                        file_chars = os.path.getsize(target_file) if os.path.exists(target_file) else len("".join(last_lines))
                        file_turns = sum(1 for line in last_lines if re.search(r'(?i)(assistant|agent|planner_response|user)', line))
                        price_in = config.get("price_input_per_m", 1.0)
                        file_cost = (file_chars / 4) * price_in / 1e6
                        
                        def update_session_stats():
                            try:
                                with sqlite3.connect(os.path.join(ROOT_DIR, "knowledge.db")) as conn:
                                    conn.execute("UPDATE session_meta SET turns = ?, chars = ?, est_cost = ? WHERE path = ?", (file_turns, file_chars, file_cost, target_file))
                                    conn.commit()
                            except: pass
                        await asyncio.to_thread(update_session_stats)
                    
                    if new_html:
                        try:
                            file_size = os.path.getsize(target_file)
                            context_percent = min(100.0, (file_size / 512000.0) * 100.0)
                        except:
                            context_percent = 0.0
                            
                        payload = json.dumps({
                            "type": "context_append" if not is_initial else "context_update", 
                            "content": new_html, 
                            "agent": agent_name,
                            "path": target_file,
                            "touched_files": extract_touched_files("".join(last_lines)[-2000:]),
                            "context_percent": context_percent
                        })
                        await broker.publish(payload)
                        
                        kb_match = await asyncio.to_thread(check_active_kb, "".join(last_lines)[-1500:])
                    last_kb = last_recommended_kbs.get(target_file, "")
                    if kb_match and kb_match["content"] != last_kb:
                        last_recommended_kbs[target_file] = kb_match["content"]
                        await broker.publish(json.dumps({
                            "type": "kb_recommendation", 
                            "insight_id": kb_match["id"],
                            "content": kb_match["content"],
                            "agent": agent_name,
                            "path": target_file
                        }))
                        
                    if last_lines:
                        is_waiting = check_waiting_status(list(last_lines))
                        prev_waiting = last_wait_state.get(target_file)
                        
                        if is_waiting != prev_waiting:
                            last_wait_state[target_file] = is_waiting
                            if is_waiting:
                                now = time.time()
                                if now - last_wait_notified.get(target_file, 0) > 180:
                                    last_wait_notified[target_file] = now
                                    await broker.publish(json.dumps({
                                        "type": "agent_waiting",
                                        "agent": agent_name,
                                        "path": target_file
                                    }))
                            else:
                                await broker.publish(json.dumps({
                                    "type": "agent_unblocked",
                                    "agent": agent_name,
                                    "path": target_file
                                }))
                            
                        recent_20 = list(last_lines)[-20:]
                        err_lines = [l for l in recent_20 if re.search(r'(?i)(error|exception|timeout)', l)]
                        if len(err_lines) >= 5:
                            if time.time() - last_error_warnings.get(target_file, 0) > 60:
                                last_error_warnings[target_file] = time.time()
                                await broker.publish(json.dumps({
                                    "type": "error_warning",
                                    "agent": agent_name,
                                    "path": target_file,
                                    "content": "检测到连续异常，可能是卡点，是否需要我诊断？"
                                }))
                        
            frozen = active_tracking - current_active
            for f in frozen:
                await broker.publish(json.dumps({"type": "agent_frozen", "path": f}))
                active_tracking.remove(f)
                if f in current_contexts:
                    del current_contexts[f]
                if f in last_mtimes:
                    del last_mtimes[f]
                    
        except Exception:
            logger.error("async_log_tailer 轮询异常: %s", traceback.format_exc())
        await asyncio.sleep(1)

app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    index_path = os.path.join(ROOT_DIR, "static", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/splash", response_class=HTMLResponse)
async def get_splash():
    splash_path = os.path.join(ROOT_DIR, "static", "splash.html")
    with open(splash_path, "r", encoding="utf-8") as f:
        return f.read()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None, ticket: str = None):
    valid = False
    if ticket and ticket in active_tickets:
        if time.time() < active_tickets[ticket]:
            valid = True
        active_tickets.pop(ticket, None)
    elif token and secrets.compare_digest(token, API_KEY):
        valid = True
        
    if not valid:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning("Rejected unauthorized WebSocket connection.")
        return
        
    global current_contexts, config
    await websocket.accept()
    
    class WSWrapper:
        def __init__(self, ws: WebSocket):
            self.ws = ws
            self.queue = asyncio.Queue(maxsize=200)
            self.task = asyncio.create_task(self.writer())
            
        async def writer(self):
            try:
                while True:
                    msg = await self.queue.get()
                    await self.ws.send_text(msg)
                    self.queue.task_done()
            except Exception:
                pass
                
        async def send_text(self, text: str):
            try:
                self.queue.put_nowait(text)
            except asyncio.QueueFull:
                pass
            
        def cancel(self):
            self.task.cancel()
            
    wrapper = WSWrapper(websocket)
    await broker.subscribe(wrapper)
    
    try:
        combined = "\n".join([f"--- Agent: {path} ---\n{ctx}" for path, ctx in current_contexts.items()])
        await wrapper.send_text(json.dumps({"type": "context_update", "content": combined, "agent": "Loading...", "path": "all"}))
        last_request_time = 0
        
        def load_persisted_chat(agent_path=""):
            try:
                with sqlite3.connect(os.path.join(ROOT_DIR, "knowledge.db")) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT role, content FROM chat_history WHERE agent_path = ? ORDER BY id DESC LIMIT 20", (agent_path,))
                    rows = cursor.fetchall()
                    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
            except:
                return []

        sys_prompt = {"role": "system", "content": SYSTEM_PROMPT}
        chat_history = [sys_prompt] + load_persisted_chat("")
        
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("type") == "adopt_session":
                target_path = msg.get("path")
                if target_path and os.path.exists(target_path):
                    rendered_html, last_lines = _format_transcript_sync(target_path, is_initial=True)
                    current_contexts[target_path] = rendered_html
                    combined = "\n".join([f"--- Agent: {p} ---\n{ctx}" for p, ctx in current_contexts.items()])
                    await wrapper.send_text(json.dumps({
                        "type": "context_update",
                        "content": combined,
                        "agent": os.path.basename(target_path),
                        "path": target_path
                    }))
                    await wrapper.send_text(json.dumps({
                        "type": "sys_message",
                        "content": f"⚡ Context resumed for session: {os.path.basename(target_path)}"
                    }))
                continue
                
            if msg["type"] == "chat":
                current_time = time.time()
                if current_time - last_request_time < 1.0:
                    await wrapper.send_text(json.dumps({"type": "ai_response_chunk", "content": "\n\n[System] Rate limited. Please wait..."}))
                    await wrapper.send_text(json.dumps({"type": "ai_response_end"}))
                    continue
                last_request_time = current_time
                
                user_prompt = msg["content"]

                # Optional per-message mode: {"context": "snapshot"|"full", "save": true|false}
                # Defaults keep the original behavior (snapshot + save).
                mode = msg.get("mode") or {}
                should_save = mode.get("save", True)

                # Store ONLY the user's question in the persistent chat history
                chat_history.append({"role": "user", "content": user_prompt})

                # Keep history bounded (System prompt + last 10 messages)
                if len(chat_history) > 11:
                    chat_history = [chat_history[0]] + chat_history[-10:]

                # Build temporary messages array for API call to prevent context pollution
                prompt_content = build_prompt_content(mode, current_contexts, user_prompt)
                
                api_messages = list(chat_history)
                api_messages[-1] = {"role": "user", "content": prompt_content}
                
                try:
                    client = get_ai_client()
                    
                    await wrapper.send_text(json.dumps({
                        "type": "ai_response_start",
                        "content": ""
                    }))
                    
                    response = await client.chat.completions.create(
                        model=config["model"],
                        messages=api_messages,
                        stream=True
                    )
                    
                    full_response = ""
                    async for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            await wrapper.send_text(json.dumps({
                                "type": "ai_response_chunk",
                                "content": content
                            }))
                            
                    await wrapper.send_text(json.dumps({
                        "type": "ai_response_end"
                    }))
                    
                    chat_history.append({"role": "assistant", "content": full_response})
                    
                    def save_chat_round(u_text, a_text):
                        try:
                            with sqlite3.connect(os.path.join(ROOT_DIR, "knowledge.db")) as conn:
                                conn.execute("INSERT INTO chat_history (agent_path, role, content) VALUES ('', 'user', ?)", (u_text,))
                                conn.execute("INSERT INTO chat_history (agent_path, role, content) VALUES ('', 'assistant', ?)", (a_text,))
                                conn.execute("DELETE FROM chat_history WHERE id NOT IN (SELECT id FROM chat_history WHERE agent_path = '' ORDER BY id DESC LIMIT 40)")
                                conn.commit()
                        except: pass
                    if should_save:
                        await asyncio.to_thread(save_chat_round, user_prompt, full_response)
                    
                except Exception as e:
                    logger.error(f"[AI Model Error]: {e}")
                    error_msg = str(e)
                    friendly_error = (
                        f"\n\n<div style='background:rgba(239, 68, 68, 0.1); border:1px solid rgba(239, 68, 68, 0.4); "
                        f"padding:12px; border-radius:8px; color:#fca5a5; margin-top:8px; font-size:0.9rem;'>"
                        f"<strong>⚠️ AI Request Failed</strong><br>"
                        f"I couldn't process that request. The backend encountered an error: <br><code>{error_msg}</code><br>"
                        f"<em>Tip: Check your API key or network connection.</em></div>"
                    )
                    try:
                        await wrapper.send_text(json.dumps({
                            "type": "ai_response_chunk",
                            "content": friendly_error
                        }))
                        await wrapper.send_text(json.dumps({
                            "type": "ai_response_end"
                        }))
                        # Remove the failed user prompt so it doesn't corrupt history
                        if chat_history and chat_history[-1]["role"] == "user":
                            chat_history.pop()
                    except Exception:
                        pass
                
            elif msg["type"] == "clear_history":
                chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
                
            elif msg["type"] == "merge_kb":
                combined = "\n".join([f"--- Agent: {path} ---\n{ctx}" for path, ctx in current_contexts.items()])
                kb_prompt = f"请将以下开发日志中的核心问题和解决方案提炼成一段 Markdown 笔记（包含问题描述、原因分析、解决方案、以及可以直接复制粘贴的修复代码）。要求格式极其严谨。\n\n日志上下文:\n```\n{combined}\n```"
                try:
                    client = get_ai_client()
                    response = await client.chat.completions.create(
                        model=config["model"],
                        messages=[{"role": "user", "content": kb_prompt}]
                    )
                    
                    insight_content = response.choices[0].message.content
                    
                    # Also write to file for legacy/UI reasons
                    kb_path = os.path.join(ROOT_DIR, "Gabriel_Insight.md")
                    with open(kb_path, "a", encoding="utf-8") as f:
                        f.write(f"\n\n---\n## Insight ({time.strftime('%Y-%m-%d %H:%M:%S')})\n{insight_content}")
                        
                    # Save to DB for FTS5 indexing
                    db_path = os.path.join(ROOT_DIR, "knowledge.db")
                    conn = sqlite3.connect(db_path)
                    try:
                        cursor = conn.cursor()
                        cursor.execute("CREATE TABLE IF NOT EXISTS insights (id INTEGER PRIMARY KEY, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
                        cursor.execute("INSERT INTO insights (content) VALUES (?)", (insight_content,))
                        cursor.execute("INSERT INTO insights_fts (content, timestamp) VALUES (?, CURRENT_TIMESTAMP)", (insight_content,))
                        conn.commit()
                    except Exception as db_err:
                        logger.error(f"Failed to insert into FTS5: {db_err}")
                    finally:
                        conn.close()
                        
                    await wrapper.send_text(json.dumps({
                        "type": "kb_toast",
                        "content": insight_content
                    }))
                    
                    await wrapper.send_text(json.dumps({
                        "type": "sys_message",
                        "content": "✅ 已生成知识库并存入大脑（FTS5索引完成）！"
                    }))
                except Exception as e:
                    await wrapper.send_text(json.dumps({
                        "type": "sys_message",
                        "content": f"❌ 提炼失败: {str(e)}"
                    }))
            elif msg["type"] == "inject_insight":
                insight_content = msg.get("content", "")
                db_path = os.path.join(ROOT_DIR, "knowledge.db")
                conn = sqlite3.connect(db_path)
                try:
                    cursor = conn.cursor()
                    cursor.execute("CREATE TABLE IF NOT EXISTS insights (id INTEGER PRIMARY KEY, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
                    cursor.execute("INSERT INTO insights (content) VALUES (?)", (insight_content,))
                    cursor.execute("INSERT INTO insights_fts (content, timestamp) VALUES (?, CURRENT_TIMESTAMP)", (insight_content,))
                    conn.commit()
                except Exception as db_err:
                    logger.error(f"Failed to insert into FTS5: {db_err}")
                finally:
                    conn.close()
                    
                kb_path = os.path.join(ROOT_DIR, "Gabriel_Insight.md")
                with open(kb_path, "a", encoding="utf-8") as f:
                    f.write(f"\n\n---\n## Insight ({time.strftime('%Y-%m-%d %H:%M:%S')})\n{insight_content}")
                await wrapper.send_text(json.dumps({
                    "type": "sys_message",
                    "content": "✅ 已注入知识库草稿！(Injected into KB)"
                }))
            elif msg["type"] == "ping":
                await wrapper.send_text(json.dumps({"type": "pong"}))
            elif msg["type"] == "request_full_sync":
                for target_file, ctx in current_contexts.items():
                    await wrapper.send_text(json.dumps({
                        "type": "context_update",
                        "content": ctx,
                        "agent": os.path.basename(target_file),
                        "path": target_file
                    }))
                    
    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket.")
    except Exception:
        logger.warning("WebSocket session ended unexpectedly: %s", traceback.format_exc())
    finally:
        await broker.unsubscribe(wrapper)
        wrapper.cancel()
            
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gabriel Control Center")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="critical")

if __name__ == "__main__":
    main()



