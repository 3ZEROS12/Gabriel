import os
import uvicorn
import asyncio
import glob
import time
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, status, Security, Depends
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

app = FastAPI(title="Gabriel Control Center")
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # [Point 20] Edge Caching: Add Cache-Control for static assets
    if request.url.path.startswith("/static/"):
        # Cache static files for 1 year (Standard CDN practice)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        
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
    "model": "gemini-3.5-flash",
    "merge_mode": "manual",
    "target_agent": "auto" # "auto" or absolute path
}

import copy
import shutil
import tempfile
import logging

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
            except:
                pass
    return current_config

def save_config(cfg):
    dir_name = os.path.dirname(CONFIG_FILE)
    fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        os.replace(temp_path, CONFIG_FILE)
    except Exception as e:
        os.remove(temp_path)
        raise e

config = load_config()

# OpenAI Client singleton
def get_ai_client():
    return AsyncOpenAI(
        base_url=config.get("base_url") or "https://api.openai.com/v1",
        api_key=config.get("api_key") or "dummy"
    )

current_contexts = {}
last_file = None

class ConfigModel(BaseModel):
    base_url: str
    api_key: str
    model: str
    merge_mode: str
    target_agent: str

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

@app.on_event("startup")
async def startup_event():
    await broker.start()
    logger.info("EventBroker started.")

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

@api_router.get("/ping")
async def ping():
    return {"status": "ok"}

@api_router.get("/config")
async def get_config():
    return JSONResponse(load_config())

@api_router.post("/config")
async def update_config(cfg: ConfigModel):
    global config
    try:
        if hasattr(cfg, "model_dump"):
            config.update(cfg.model_dump())
        else:
            config.update(cfg.dict())
        save_config(config)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@api_router.get("/knowledge")
async def get_knowledge():
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

def get_session_stats(filepath):
    steps = 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for _ in f:
                steps += 1
    except:
        pass
    return steps

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
                    steps = get_session_stats(f)
                    try:
                        with open(f, 'r', encoding='utf-8') as f_obj:
                            first_line = f_obj.readline()
                    except:
                        first_line = ""
                    _agent_scan_cache[f] = {'mtime': mtime, 'steps': steps, 'first_line': first_line}
                    
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

import sqlite3
# --- Database (FTS5 Knowledge Base) ---
def init_db():
    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    # Upgrade to FTS5 for lightning-fast semantic/text retrieval
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS insights_fts USING fts5(
            content,
            timestamp UNINDEXED
        )
    """)
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

def get_db():
    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@api_router.get("/kb")
async def get_kb(db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
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
    return JSONResponse({"content": ""})

@api_router.post("/kb")
async def update_kb(data: KBModel, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        # Insert into legacy table for backup
        cursor.execute("CREATE TABLE IF NOT EXISTS insights (id INTEGER PRIMARY KEY, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("INSERT INTO insights (content) VALUES (?)", (data.content,))
        # Insert into FTS5 high-performance index
        cursor.execute("INSERT INTO insights_fts (content, timestamp) VALUES (?, CURRENT_TIMESTAMP)", (data.content,))
        db.commit()
        
        # Keep a markdown mirror for backward compatibility and easy human reading
        kb_path = os.path.join(ROOT_DIR, "Gabriel_Insight.md")
        with open(kb_path, "w", encoding="utf-8") as f:
            f.write(data.content)
            
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"KB Post Error: {e}")
        raise HTTPException(status_code=500, detail="Database write failed")

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
        return [os.path.join(os.path.expanduser(r"~/.gemini/antigravity-cli/brain"), "*", ".system_generated", "logs", "transcript.jsonl")]

    @staticmethod
    def get_agent_name(filepath: str) -> str:
        uuid_str = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(filepath))))[:8]
        return f"agy session ({uuid_str})"

    @staticmethod
    def identify(filepath: str, line: str) -> bool:
        return ".system_generated" in filepath or "transcript.jsonl" in filepath
        
    @staticmethod
    def parse(line: str) -> str:
        try:
            data = json.loads(line)
            step_type = data.get("type", "")
            content = data.get("content", "")
            if not step_type:
                raise ValueError("Missing 'type' field")
            
            safe_content = html.escape(str(content))
            
            # Extract tool calls if present
            tool_html = ""
            if "tool_calls" in data and isinstance(data["tool_calls"], list):
                for tc in data["tool_calls"]:
                    t_name = html.escape(tc.get("name", "unknown_tool"))
                    t_args = html.escape(json.dumps(tc.get("arguments", {}))[:100])
                    tool_html += f'<div style="margin-top:4px; padding:4px 8px; background:rgba(16, 185, 129, 0.1); border-left:2px solid #10b981; font-size:0.8em; color:#10b981;">⚡ Call: {t_name}({t_args}...)</div>'
            
            if step_type == "USER_INPUT":
                return f'<div style="margin-bottom:8px;"><span style="color:#60a5fa; font-weight:bold;">👤 [USER]:</span> <span style="color:#e2e8f0;">{safe_content[:200]}...</span></div>'
            elif step_type == "PLANNER_RESPONSE":
                return f'<div style="margin-bottom:8px;"><span style="color:#d4af37; font-weight:bold;">🤖 [AGENT]:</span> <span style="color:#cbd5e1;">{safe_content[:200]}...</span>{tool_html}</div>'
            elif step_type == "TOOL_RESPONSE":
                if len(safe_content) > 300:
                    safe_content = safe_content[:300] + "... (truncated)"
                return f'<div style="margin-bottom:8px;"><span style="color:#10b981; font-weight:bold;">🛠️ [TOOL OUTPUT]:</span><br><span style="color:#94a3b8; font-size:0.8em;">{safe_content}</span></div>'
            else:
                return f'<div style="margin-bottom:8px;"><span style="color:#94a3b8; font-weight:bold;">[{step_type}]:</span> <span style="color:#cbd5e1;">{safe_content[:150]}...</span>{tool_html}</div>'
        except Exception as e:
            logger.warning(f"AntigravityParser parse warning: {e}. Degrading to plain text.")
            return PlainTextFallbackParser.parse(line)

class ClaudeCodeParser(BaseParser):
    @staticmethod
    def get_scan_patterns() -> list:
        return [os.path.expanduser(r"~/.claude_code/logs/*.json"), os.path.expanduser(r"~/.claude_code/logs/*.jsonl")]

    @staticmethod
    def get_agent_name(filepath: str) -> str:
        return f"claude ({os.path.basename(filepath)})"

    @staticmethod
    def identify(filepath: str, line: str) -> bool:
        return "claude_code" in filepath.lower() or "claude.json" in filepath.lower()
        
    @staticmethod
    def parse(line: str) -> str:
        line = line.strip()
        if not line: return None
        try:
            data = json.loads(line)
            if not isinstance(data, dict):
                raise ValueError("JSON root is not an object")
            msg_type = data.get("type") or data.get("role") or data.get("message_type")
            if not msg_type:
                raise ValueError("Missing role/type field")
        except Exception as e:
            logger.warning(f"ClaudeCodeParser parse warning: {e}. Degrading to plain text.")
            return PlainTextFallbackParser.parse(line)
            
        content = data.get("content") or data.get("message") or data.get("text") or ""
        
        if isinstance(content, (dict, list)):
            content = json.dumps(content, ensure_ascii=False)
            
        content = str(content)
        safe_content = html.escape(content)
        
        if msg_type in ("user", "USER_INPUT"):
            return f'<div style="margin-bottom:8px;"><span style="color:#60a5fa; font-weight:bold;">👤 [USER]:</span> <span style="color:#e2e8f0;">{safe_content[:200]}...</span></div>'
        elif msg_type in ("assistant", "agent", "PLANNER_RESPONSE", "model"):
            return f'<div style="margin-bottom:8px;"><span style="color:#a855f7; font-weight:bold;">🟣 [Claude]:</span> <span style="color:#cbd5e1;">{safe_content[:200]}...</span></div>'
        elif msg_type in ("tool", "system", "TOOL_RESPONSE", "tool_call"):
            if len(safe_content) > 300:
                safe_content = safe_content[:300] + "... (truncated)"
            return f'<div style="margin-bottom:8px;"><span style="color:#10b981; font-weight:bold;">🛠️ [TOOL]:</span><br><span style="color:#94a3b8; font-size:0.8em;">{safe_content}</span></div>'
        else:
            return f'<div style="margin-bottom:8px;"><span style="color:#a855f7; font-weight:bold;">🟣 [Claude Code]:</span> <span style="color:#cbd5e1;">{safe_content[:200]}...</span></div>'

class CursorParser(BaseParser):
    @staticmethod
    def get_scan_patterns() -> list:
        return [os.path.join(os.getcwd(), ".cursor", "logs", "*.log"), os.path.join(os.getcwd(), ".cursor", "logs", "*.jsonl")]

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
                return f'<div style="margin-bottom:8px;"><span style="color:#60a5fa; font-weight:bold;">👤 [USER]:</span> <span style="color:#e2e8f0;">{safe_content[5:200]}...</span></div>'
            elif line.startswith("Cursor:"):
                return f'<div style="margin-bottom:8px;"><span style="color:#3b82f6; font-weight:bold;">🔵 [Cursor]:</span> <span style="color:#cbd5e1;">{safe_content[7:200]}...</span></div>'
            return PlainTextFallbackParser.parse(line)
            
        content = data.get("content") or data.get("message") or data.get("text") or ""
        
        if isinstance(content, (dict, list)):
            content = json.dumps(content, ensure_ascii=False)
        content = str(content)
        safe_content = html.escape(content)
        
        if role in ("user", "USER_INPUT"):
            return f'<div style="margin-bottom:8px;"><span style="color:#60a5fa; font-weight:bold;">👤 [USER]:</span> <span style="color:#e2e8f0;">{safe_content[:200]}...</span></div>'
        elif role in ("assistant", "agent", "model"):
            return f'<div style="margin-bottom:8px;"><span style="color:#3b82f6; font-weight:bold;">🔵 [Cursor]:</span> <span style="color:#cbd5e1;">{safe_content[:200]}...</span></div>'
        elif role in ("tool", "system", "tool_call"):
            if len(safe_content) > 300:
                safe_content = safe_content[:300] + "... (truncated)"
            return f'<div style="margin-bottom:8px;"><span style="color:#10b981; font-weight:bold;">🛠️ [TOOL]:</span><br><span style="color:#94a3b8; font-size:0.8em;">{safe_content}</span></div>'
        else:
            return f'<div style="margin-bottom:8px;"><span style="color:#3b82f6; font-weight:bold;">🔵 [Cursor]:</span> <span style="color:#cbd5e1;">{safe_content[:200]}...</span></div>'

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

def _format_transcript_sync(filepath):
    try:
        from collections import deque
        first_line = ""
        last_lines = deque(maxlen=200)
        
        with open(filepath, "r", encoding="utf-8") as f:
            first_line = f.readline()
            if not first_line:
                return ""
            last_lines.append(first_line)
            for line in f:
                last_lines.append(line)
        
        # Identify which parser to use based on the file path and first line
        parser = ParserRegistry.get_parser(filepath, first_line)
        
        output = [f'<div style="color:#fbbf24; font-weight:bold; margin-bottom:12px;">[Agent 日志实时同步中... 渲染引擎: {parser.__name__}]</div>']
        for line in last_lines:
            try:
                parsed = parser.parse(line)
                if parsed:
                    output.append(parsed)
            except:
                pass
        return "".join(output)
    except Exception as e:
        return f"Error reading log: {e}"

async def format_transcript(filepath):
    return await asyncio.to_thread(_format_transcript_sync, filepath)

STOP_WORDS = {"this", "that", "with", "from", "your", "have", "what", "there", "their", "will", "would", "could", "should", "about", "which", "when", "where", "while", "these", "those", "using", "function", "return", "class", "import", "system", "message", "content", "role", "user", "agent", "tool", "response", "planner"}

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
    all_terms = [w.lower() for w in (files + identifiers + errors)]
    filtered = [w for w in all_terms if w not in STOP_WORDS and len(w) > 3]
    
    most_common = [w[0] for w in Counter(filtered).most_common(max_words)]
    
    # Use FTS5 OR syntax to increase recall
    return " OR ".join(most_common) if most_common else ""

def check_active_kb(text: str):
    kw = extract_keywords(text)
    if not kw: return None
    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # FTS5 matches using the constructed OR query
        cursor.execute("SELECT content FROM insights_fts WHERE content MATCH ? ORDER BY rank LIMIT 1", (kw,))
        row = cursor.fetchone()
        if row:
            return row[0]
    except Exception as e:
        logger.error(f"FTS5 Match Error for query '{kw}': {e}")
    finally:
        conn.close()
    return None

async def async_log_tailer():
    global current_contexts
    last_mtimes = {}
    last_recommended_kbs = {}
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

                if current_mtime != last_mtimes.get(target_file, 0):
                    last_mtimes[target_file] = current_mtime
                    
                    new_context = await format_transcript(target_file)
                    current_contexts[target_file] = new_context
                    
                    payload = json.dumps({
                        "type": "context_update", 
                        "content": new_context, 
                        "agent": agent_name,
                        "path": target_file
                    })
                    await broker.publish(payload)
                    
                    kb_match = await asyncio.to_thread(check_active_kb, new_context[-1500:])
                    last_kb = last_recommended_kbs.get(target_file, "")
                    if kb_match and kb_match != last_kb:
                        last_recommended_kbs[target_file] = kb_match
                        await broker.publish(json.dumps({
                            "type": "kb_recommendation", 
                            "content": kb_match,
                            "agent": agent_name,
                            "path": target_file
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

@app.on_event("startup")
async def startup_event_tailer():
    asyncio.create_task(async_log_tailer())

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
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    if token != API_KEY:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning("Rejected unauthorized WebSocket connection.")
        return
        
    global current_contexts, config
    await websocket.accept()
    await broker.subscribe(websocket)
    try:
        combined = "\n".join([f"--- Agent: {path} ---\n{ctx}" for path, ctx in current_contexts.items()])
        await websocket.send_text(json.dumps({"type": "context_update", "content": combined, "agent": "Loading...", "path": "all"}))
        last_request_time = 0
        
        chat_history = [
            {"role": "system", "content": "You are Gabriel, an elite, non-intrusive AI side-screen companion and engineering supervisor. Your core directive is to observe the main AI agent's execution logs (Terminal Snapshot) and answer the human user's queries WITHOUT interrupting the main agent's context. \n\nPERSONA & CAPABILITIES:\n1. Parallel Querying: Answer user questions (definitions, code explanations, logic checks) based on the logs without polluting the main context.\n2. Real-time Debugging: If the user asks about an error or stall, diagnose the stack trace deeply and provide actionable fixes.\n3. Process Auditing: Act as a QA/Supervisor. Evaluate if the agent's current strategy is correct.\n4. Strict Conciseness: You are a side-screen. Responses must be sharp, highly formatted (use markdown, bolding, code blocks), and free of filler words. Jump straight to the insight."}
        ]
        
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg["type"] == "chat":
                current_time = time.time()
                if current_time - last_request_time < 1.0:
                    await websocket.send_text(json.dumps({"type": "ai_response_chunk", "content": "\n\n[System] Rate limited. Please wait..."}))
                    await websocket.send_text(json.dumps({"type": "ai_response_end"}))
                    continue
                last_request_time = current_time
                
                user_prompt = msg["content"]
                
                # Store ONLY the user's question in the persistent chat history
                chat_history.append({"role": "user", "content": user_prompt})
                
                # Keep history bounded (System prompt + last 10 messages)
                if len(chat_history) > 11:
                    chat_history = [chat_history[0]] + chat_history[-10:]
                
                # Build temporary messages array for API call to prevent context pollution
                combined = "\n".join([f"--- Agent: {path} ---\n{ctx}" for path, ctx in current_contexts.items()])
                prompt_content = f"Terminal Snapshot(s):\n```\n{combined}\n```\n\nUser Question:\n{user_prompt}"
                
                api_messages = list(chat_history)
                api_messages[-1] = {"role": "user", "content": prompt_content}
                
                try:
                    client = get_ai_client()
                    
                    await websocket.send_text(json.dumps({
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
                            await websocket.send_text(json.dumps({
                                "type": "ai_response_chunk",
                                "content": content
                            }))
                            
                    await websocket.send_text(json.dumps({
                        "type": "ai_response_end"
                    }))
                    
                    chat_history.append({"role": "assistant", "content": full_response})
                    
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
                        await websocket.send_text(json.dumps({
                            "type": "ai_response_chunk",
                            "content": friendly_error
                        }))
                        await websocket.send_text(json.dumps({
                            "type": "ai_response_end"
                        }))
                        # Remove the failed user prompt so it doesn't corrupt history
                        if chat_history and chat_history[-1]["role"] == "user":
                            chat_history.pop()
                    except Exception:
                        pass
                
            elif msg["type"] == "clear_history":
                chat_history = [
                    {"role": "system", "content": "You are Gabriel, an elite, non-intrusive AI side-screen companion and engineering supervisor. Your core directive is to observe the main AI agent's execution logs (Terminal Snapshot) and answer the human user's queries WITHOUT interrupting the main agent's context. \n\nPERSONA & CAPABILITIES:\n1. Parallel Querying: Answer user questions (definitions, code explanations, logic checks) based on the logs without polluting the main context.\n2. Real-time Debugging: If the user asks about an error or stall, diagnose the stack trace deeply and provide actionable fixes.\n3. Process Auditing: Act as a QA/Supervisor. Evaluate if the agent's current strategy is correct.\n4. Strict Conciseness: You are a side-screen. Responses must be sharp, highly formatted (use markdown, bolding, code blocks), and free of filler words. Jump straight to the insight."}
                ]
                
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
                        f.write("\n\n" + insight_content)
                        
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
                        
                    await websocket.send_text(json.dumps({
                        "type": "kb_toast",
                        "content": insight_content
                    }))
                    
                    await websocket.send_text(json.dumps({
                        "type": "sys_message",
                        "content": "✅ 已生成知识库并存入大脑（FTS5索引完成）！"
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "sys_message",
                        "content": f"❌ 提炼失败: {str(e)}"
                    }))
            elif msg["type"] == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif msg["type"] == "request_full_sync":
                for target_file, ctx in current_contexts.items():
                    await websocket.send_text(json.dumps({
                        "type": "context_update",
                        "content": ctx,
                        "agent": os.path.basename(target_file),
                        "path": target_file
                    }))
                    
    except WebSocketDisconnect:
        await broker.unsubscribe(websocket)
        logger.info("Client disconnected from WebSocket.")
            
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gabriel Control Center")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    uvicorn.run(app, host="127.0.0.1", port=args.port)

if __name__ == "__main__":
    main()



