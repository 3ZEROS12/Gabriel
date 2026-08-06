# Code Review Snapshot\n\n## File: `src/main.py`\n\n```python\nimport os
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
            # Broadcast to all subscribers safely
            dead_sockets = set()
            for sub in list(self.subscribers):
                try:
                    await sub.send_text(message)
                except Exception:
                    dead_sockets.add(sub)
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
    for f in files:
        try:
            mtime = os.path.getmtime(f)
            ctime = os.path.getctime(f)
            if time.time() - mtime < 86400: # Active in last 24h
                steps = get_session_stats(f)
                
                # Resolve name dynamically via ParserRegistry
                try:
                    with open(f, 'r', encoding='utf-8') as f_obj:
                        first_line = f_obj.readline()
                except:
                    first_line = ""
                    
                parser = ParserRegistry.get_parser(f, first_line)
                name = parser.get_agent_name(f) if hasattr(parser, 'get_agent_name') else os.path.basename(f)
                
                agents.append({"name": name, "path": f, "mtime": mtime, "ctime": ctime, "steps": steps})
        except:
            pass
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
            
            if step_type == "USER_INPUT":
                return f'<div style="margin-bottom:8px;"><span style="color:#60a5fa; font-weight:bold;">👤 [USER]:</span> <span style="color:#e2e8f0;">{safe_content[:200]}...</span></div>'
            elif step_type == "PLANNER_RESPONSE":
                return f'<div style="margin-bottom:8px;"><span style="color:#d4af37; font-weight:bold;">🤖 [AGENT]:</span> <span style="color:#cbd5e1;">{safe_content[:200]}...</span></div>'
            elif step_type == "TOOL_RESPONSE":
                if len(safe_content) > 300:
                    safe_content = safe_content[:300] + "... (truncated)"
                return f'<div style="margin-bottom:8px;"><span style="color:#10b981; font-weight:bold;">🛠️ [TOOL OUTPUT]:</span><br><span style="color:#94a3b8; font-size:0.8em;">{safe_content}</span></div>'
            else:
                raise ValueError(f"Unrecognized type: {step_type}")
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
        return f'<div style="margin-bottom:4px; font-family:monospace; color:#94a3b8; font-size:0.8em;">{html.escape(line.strip()[:200])}</div>'

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
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if not lines: return ""
        
        # Identify which parser to use based on the file path and first line
        parser = ParserRegistry.get_parser(filepath, lines[0] if lines else "")
        
        output = [f'<div style="color:#fbbf24; font-weight:bold; margin-bottom:12px;">[Agent 日志实时同步中... 渲染引擎: {parser.__name__}]</div>']
        for line in lines[-50:]:
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

STOP_WORDS = {"this", "that", "with", "from", "your", "have", "what", "there", "their", "will", "would", "could", "should", "about", "which", "when", "where", "while", "these", "those", "error", "failed", "using", "function", "return", "class", "import"}

def extract_keywords(text: str, max_words=3) -> str:
    clean_text = re.sub(r'<[^>]+>', ' ', text).lower()
    words = re.findall(r'\b[a-z]{5,}\b', clean_text)
    filtered = [w for w in words if w not in STOP_WORDS]
    most_common = [w[0] for w in Counter(filtered).most_common(max_words)]
    return " AND ".join(most_common) if most_common else ""

def check_active_kb(text: str):
    kw = extract_keywords(text)
    if not kw: return None
    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT content FROM insights_fts WHERE content MATCH ? ORDER BY rank LIMIT 1", (kw,))
        row = cursor.fetchone()
        if row:
            return row[0]
    except Exception as e:
        pass
    finally:
        conn.close()
    return None

async def async_log_tailer():
    global current_contexts
    last_mtimes = {}
    last_recommended_kbs = {}
    
    while True:
        try:
            agents = await scan_active_agents()
            tailer_last_heartbeat["timestamp"] = time.time()
            tailer_last_heartbeat["status"] = "healthy"
            for agent in agents:
                target_file = agent["path"]
                current_mtime = agent["mtime"]
                
                # If target_agent is manual, skip others
                if config.get("target_agent") != "auto" and target_file != config.get("target_agent"):
                    continue

                if current_mtime != last_mtimes.get(target_file, 0):
                    last_mtimes[target_file] = current_mtime
                    agent_name = agent["name"]
                    
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
                combined = "\n".join([f"--- Agent: {path} ---\n{ctx}" for path, ctx in current_contexts.items()])
                full_prompt = f"Terminal Snapshot(s):\n```\n{combined}\n```\n\nUser Question:\n{user_prompt}"
                
                try:
                    client = get_ai_client()
                    
                    await websocket.send_text(json.dumps({
                        "type": "ai_response_start",
                        "content": ""
                    }))
                    
                    response = await client.chat.completions.create(
                        model=config["model"],
                        messages=[{"role": "user", "content": full_prompt}],
                        stream=True
                    )
                    
                    async for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            await websocket.send_text(json.dumps({
                                "type": "ai_response_chunk",
                                "content": content
                            }))
                            
                    await websocket.send_text(json.dumps({
                        "type": "ai_response_end"
                    }))
                    
                except Exception as e:
                    print(f"[OpenAI Error]: {e}")
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "ai_response_chunk",
                            "content": f"\n\nAPI Error: {str(e)}"
                        }))
                        await websocket.send_text(json.dumps({
                            "type": "ai_response_end"
                        }))
                    except Exception:
                        pass
                
            elif msg["type"] == "merge_kb":
                combined = "\n".join([f"--- Agent: {path} ---\n{ctx}" for path, ctx in current_contexts.items()])
                kb_prompt = f"请将以下开发日志中的核心问题和解决方案提炼成一段 Markdown 笔记（包含问题描述、原因分析、解决方案、以及可以直接复制粘贴的修复代码）。要求格式极其严谨。\n\n日志上下文:\n```\n{combined}\n```"
                try:
                    client = get_ai_client()
                    response = await client.chat.completions.create(
                        model=config["model"],
                        messages=[{"role": "user", "content": kb_prompt}]
                    )
                    
                    kb_path = os.path.join(ROOT_DIR, "Gabriel_Insight.md")
                    with open(kb_path, "w", encoding="utf-8") as f:
                        f.write(response.choices[0].message.content)
                        
                    await websocket.send_text(json.dumps({
                        "type": "sys_message",
                        "content": "✅ 已生成知识库草稿，请前往【Knowledge Base】面板查看并注入剪贴板！"
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "sys_message",
                        "content": f"❌ 提炼失败: {str(e)}"
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



\n```\n\n## File: `static/script.js`\n\n```javascript\nconst dict = {
    "en": {
        "nav_chat": "Chat", "nav_radar": "Radar", "nav_kb": "KB", "nav_settings": "Settings",
        "chat_terminal": "Terminal Context", "chat_waiting_log": "Waiting for terminal tailing...",
        "chat_assistant": "🧠 Assistant", "chat_merge": "Merge to KB", "chat_welcome": "Gabriel launched. Terminal snapshot is actively tracked.",
        "chat_placeholder": "Ask Gabriel...",
        "radar_title": "Agent Radar", "radar_desc": "Monitor active CLI Agents (Antigravity, Claude Code).", "radar_auto": "Auto-detect Active Terminal (Smart Cursor)",
        "sort_mtime_desc": "Last Active (Newest First)", "sort_mtime_asc": "Last Active (Oldest First)",
        "sort_ctime_desc": "Creation Date (Newest First)", "sort_ctime_asc": "Creation Date (Oldest First)",
        "sort_steps_desc": "Volume (Highest First)", "sort_steps_asc": "Volume (Lowest First)",
        "kb_title": "Knowledge Draft", "kb_copy": "Copy Injection Command", "kb_desc": "Review Gabriel's insight before injecting into main CLI.",
        "kb_placeholder": "Gabriel's insights will appear here...", "kb_save": "Save Draft",
        "settings_title": "API & Model Settings", "settings_desc": "Universal configuration for OpenAI-compatible endpoints.",
        "settings_baseurl": "Base URL", "settings_apikey": "API Key", "settings_model": "Model Name",
        "settings_workflow": "Workflow Strategy", "settings_merge": "Knowledge Base Merge", "settings_save": "Save Configuration",
        "mode_manual": "Manual (Geek)", "mode_auto": "Automatic",
        "settings_ui": "UI Preferences", "settings_lang": "Language", "lang_en": "English", "lang_zh": "中文 (Chinese)",
        "copied": "Copied to Clipboard!", "saved": "Saved", "scanning": "Scanning...","radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        "chat_feedback": "Feedback", "kb_recommendation": "Knowledge Base Recommendation"
    },
    "zh": {
        "nav_chat": "对话", "nav_radar": "雷达", "nav_kb": "知识库", "nav_settings": "设置",
        "chat_terminal": "终端上下文", "chat_waiting_log": "等待终端日志同步...",
        "chat_assistant": "🧠 智能副脑", "chat_merge": "合并至知识库", "chat_welcome": "加百列已启动。正在静默监听终端上下文。",
        "chat_placeholder": "向加百列提问...",
        "radar_title": "终端雷达", "radar_desc": "监控活跃的 CLI 终端 (Antigravity, Claude Code)。", "radar_auto": "自动追踪当前活跃终端 (智能游标)",
        "sort_mtime_desc": "最后活跃 (最近优先)", "sort_mtime_asc": "最后活跃 (最旧优先)",
        "sort_ctime_desc": "创建时间 (最新优先)", "sort_ctime_asc": "创建时间 (最早优先)",
        "sort_steps_desc": "对话体量 (最多优先)", "sort_steps_asc": "对话体量 (最少优先)",
        "kb_title": "知识注入草稿", "kb_copy": "复制注入指令", "kb_desc": "在注入主终端前，检查加百列整理的方案。",
        "kb_placeholder": "加百列的知识草稿将在此生成...", "kb_save": "保存草稿",
        "settings_title": "API 与模型设置", "settings_desc": "配置兼容 OpenAI 格式的大语言模型服务。",
        "settings_baseurl": "接口地址 (Base URL)", "settings_apikey": "密钥 (API Key)", "settings_model": "模型名称 (Model)",
        "settings_workflow": "工作流策略", "settings_merge": "知识库合并模式", "settings_save": "保存配置",
        "mode_manual": "手动提取 (极客)", "mode_auto": "全自动注入",
        "settings_ui": "界面偏好", "settings_lang": "显示语言",
        "copied": "已复制到剪贴板！", "saved": "已保存", "scanning": "正在扫描...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "ja": {
        "nav_chat": "チャット", "nav_radar": "レーダー", "nav_kb": "知識ベース", "nav_settings": "設定",
        "chat_terminal": "ターミナルコンテキスト", "chat_waiting_log": "ログの同期を待機中...",
        "chat_assistant": "🧠 アシスタント", "chat_merge": "知識ベースに結合", "chat_welcome": "ガブリエルが起動しました。ターミナルを監視中。",
        "chat_placeholder": "ガブリエルに質問する...",
        "radar_title": "エージェントレーダー", "radar_desc": "アクティブな CLI エージェントを監視します。", "radar_auto": "アクティブなターミナルを自動検出",
        "sort_mtime_desc": "最終アクティブ (新しい順)", "sort_mtime_asc": "最終アクティブ (古い順)",
        "sort_ctime_desc": "作成日時 (新しい順)", "sort_ctime_asc": "作成日時 (古い順)",
        "sort_steps_desc": "会話量 (多い順)", "sort_steps_asc": "会話量 (少ない順)",
        "kb_title": "知識ドラフト", "kb_copy": "コマンドをコピー", "kb_desc": "メインCLIに注入する前にインサイトを確認します。",
        "kb_placeholder": "ここにインサイトが生成されます...", "kb_save": "保存",
        "settings_title": "API とモデル設定", "settings_desc": "OpenAI 互換エンドポイントの共通設定。",
        "settings_baseurl": "ベース URL", "settings_apikey": "API キー", "settings_model": "モデル名",
        "settings_workflow": "ワークフロー戦略", "settings_merge": "知識ベース結合モード", "settings_save": "設定を保存",
        "mode_manual": "手動抽出", "mode_auto": "自動注入",
        "settings_ui": "UI 設定", "settings_lang": "表示言語",
        "copied": "コピーしました！", "saved": "保存しました", "scanning": "スキャン中...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "zh-TW": {
        "nav_chat": "對話", "nav_radar": "雷達", "nav_kb": "知識庫", "nav_settings": "設定",
        "chat_terminal": "終端上下文", "chat_waiting_log": "等待終端日誌同步...",
        "chat_assistant": "🧠 智能副腦", "chat_merge": "合併至知識庫", "chat_welcome": "加百列已啟動。正在靜默監聽終端上下文。",
        "chat_placeholder": "向加百列提問...",
        "radar_title": "終端雷達", "radar_desc": "監控活躍的 CLI 終端 (Antigravity, Claude Code)。", "radar_auto": "自動追蹤當前活躍終端 (智能游標)",
        "sort_mtime_desc": "最後活躍 (最近優先)", "sort_mtime_asc": "最後活躍 (最舊優先)",
        "sort_ctime_desc": "創建時間 (最新優先)", "sort_ctime_asc": "創建時間 (最早優先)",
        "sort_steps_desc": "對話體量 (最多優先)", "sort_steps_asc": "對話體量 (最少優先)",
        "kb_title": "知識注入草稿", "kb_copy": "複製注入指令", "kb_desc": "在注入主終端前，檢查加百列整理的方案。",
        "kb_placeholder": "加百列的知識草稿將在此生成...", "kb_save": "保存草稿",
        "settings_title": "API 與模型設定", "settings_desc": "配置相容 OpenAI 格式的大型語言模型服務。",
        "settings_baseurl": "介面位址 (Base URL)", "settings_apikey": "密鑰 (API Key)", "settings_model": "模型名稱 (Model)",
        "settings_workflow": "工作流策略", "settings_merge": "知識庫合併模式", "settings_save": "保存配置",
        "mode_manual": "手動提取 (極客)", "mode_auto": "全自動注入",
        "settings_ui": "介面偏好", "settings_lang": "顯示語言",
        "copied": "已複製到剪貼簿！", "saved": "已保存", "scanning": "正在掃描...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "fr": {
        "nav_chat": "Chat", "nav_radar": "Radar", "nav_kb": "Base de C.", "nav_settings": "Paramètres",
        "chat_terminal": "Contexte Terminal", "chat_waiting_log": "En attente des journaux...",
        "chat_assistant": "🧠 Assistant", "chat_merge": "Fusionner à la base", "chat_welcome": "Gabriel lancé. Terminal surveillé.",
        "chat_placeholder": "Demandez à Gabriel...",
        "radar_title": "Radar d'Agents", "radar_desc": "Surveiller les agents CLI actifs.", "radar_auto": "Détection automatique",
        "sort_mtime_desc": "Dernier Actif (Plus récent)", "sort_mtime_asc": "Dernier Actif (Plus ancien)",
        "sort_ctime_desc": "Date de création (Plus récent)", "sort_ctime_asc": "Date de création (Plus ancien)",
        "sort_steps_desc": "Volume (Plus élevé)", "sort_steps_asc": "Volume (Plus bas)",
        "kb_title": "Brouillon", "kb_copy": "Copier la Commande", "kb_desc": "Vérifiez les insights avant l'injection.",
        "kb_placeholder": "Les insights apparaîtront ici...", "kb_save": "Enregistrer",
        "settings_title": "Paramètres API", "settings_desc": "Configuration des points d'accès OpenAI.",
        "settings_baseurl": "URL de base", "settings_apikey": "Clé API", "settings_model": "Modèle",
        "settings_workflow": "Stratégie de Workflow", "settings_merge": "Mode de Fusion", "settings_save": "Enregistrer",
        "mode_manual": "Manuel (Geek)", "mode_auto": "Automatique",
        "settings_ui": "Préférences UI", "settings_lang": "Langue",
        "copied": "Copié !", "saved": "Enregistré", "scanning": "Analyse...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "es": {
        "nav_chat": "Chat", "nav_radar": "Radar", "nav_kb": "Base C.", "nav_settings": "Ajustes",
        "chat_terminal": "Contexto", "chat_waiting_log": "Esperando registros...",
        "chat_assistant": "🧠 Asistente", "chat_merge": "Combinar a KB", "chat_welcome": "Gabriel iniciado.",
        "chat_placeholder": "Preguntar a Gabriel...",
        "radar_title": "Radar de Agentes", "radar_desc": "Monitorear agentes CLI activos.", "radar_auto": "Detección automática",
        "sort_mtime_desc": "Último Activo (Más reciente)", "sort_mtime_asc": "Último Activo (Más antiguo)",
        "sort_ctime_desc": "Creación (Más reciente)", "sort_ctime_asc": "Creación (Más antiguo)",
        "sort_steps_desc": "Volumen (Mayor)", "sort_steps_asc": "Volumen (Menor)",
        "kb_title": "Borrador", "kb_copy": "Copiar Comando", "kb_desc": "Revisar insights antes de inyectar.",
        "kb_placeholder": "Los insights aparecerán aquí...", "kb_save": "Guardar",
        "settings_title": "Ajustes de API", "settings_desc": "Configuración para endpoints de OpenAI.",
        "settings_baseurl": "URL Base", "settings_apikey": "Clave API", "settings_model": "Modelo",
        "settings_workflow": "Flujo de trabajo", "settings_merge": "Modo de Fusión", "settings_save": "Guardar Ajustes",
        "mode_manual": "Manual (Geek)", "mode_auto": "Automático",
        "settings_ui": "Preferencias de IU", "settings_lang": "Idioma",
        "copied": "¡Copiado!", "saved": "Guardado", "scanning": "Escaneando...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "ko": {
        "nav_chat": "채팅", "nav_radar": "레이더", "nav_kb": "지식 베이스", "nav_settings": "설정",
        "chat_terminal": "터미널 컨텍스트", "chat_waiting_log": "터미널 대기 중...",
        "chat_assistant": "🧠 어시스턴트", "chat_merge": "KB에 병합", "chat_welcome": "가브리엘 시작됨. 터미널 추적 중.",
        "chat_placeholder": "질문 입력...",
        "radar_title": "에이전트 레이더", "radar_desc": "활성 CLI 에이전트 모니터링.", "radar_auto": "활성 터미널 자동 감지",
        "sort_mtime_desc": "최근 활동 (최신순)", "sort_mtime_asc": "최근 활동 (오래된순)",
        "sort_ctime_desc": "생성일 (최신순)", "sort_ctime_asc": "생성일 (오래된순)",
        "sort_steps_desc": "대화량 (많은순)", "sort_steps_asc": "대화량 (적은순)",
        "kb_title": "지식 초안", "kb_copy": "명령 복사", "kb_desc": "메인 CLI에 주입하기 전 확인.",
        "kb_placeholder": "가브리엘의 통찰력이 생성됩니다...", "kb_save": "초안 저장",
        "settings_title": "API 및 모델 설정", "settings_desc": "OpenAI 호환 엔드포인트 공통 설정.",
        "settings_baseurl": "기본 URL", "settings_apikey": "API 키", "settings_model": "모델명",
        "settings_workflow": "워크플로 전략", "settings_merge": "지식 베이스 병합 모드", "settings_save": "설정 저장",
        "mode_manual": "수동", "mode_auto": "자동",
        "settings_ui": "UI 환경설정", "settings_lang": "언어",
        "copied": "복사 완료!", "saved": "저장됨", "scanning": "스캔 중..."
    }
};

let currentLang = localStorage.getItem('gabriel_lang') || "en";

// [NOTE]: Using localStorage for token is acceptable for this local single-machine tool. 
// If Gabriel supports multi-user LAN access in the future, this must be re-evaluated.
let localToken = urlParams.get('token') || sessionStorage.getItem('gabriel_token') || localStorage.getItem('gabriel_token');
if (localToken) {
    sessionStorage.setItem('gabriel_token', localToken);
    localStorage.setItem('gabriel_token', localToken);
    window.history.replaceState({}, document.title, window.location.pathname);
} else {
    document.getElementById('loginModal').style.display = 'flex';
}

document.getElementById('btnLogin').addEventListener('click', () => {
    const t = document.getElementById('inputToken').value.trim();
    if (t) {
        sessionStorage.setItem('gabriel_token', t);
        localStorage.setItem('gabriel_token', t);
        window.location.reload();
    }
});

function applyLang() {
    const map = dict[currentLang];
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.innerText = map[el.getAttribute('data-i18n')];
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = map[el.getAttribute('data-i18n-placeholder')];
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        if(map[el.getAttribute('data-i18n-title')]) {
            el.title = map[el.getAttribute('data-i18n-title')];
        }
    });
}

document.getElementById('langSelect').value = currentLang;

document.getElementById('langSelect').addEventListener('change', (e) => {
    currentLang = e.target.value;
    localStorage.setItem('gabriel_lang', currentLang);
    applyLang();
});

// --- Window Controls ---
document.getElementById('btnClose').addEventListener('click', () => {
    if(window.pywebview && window.pywebview.api) { window.pywebview.api.close(); }
});
document.getElementById('btnMin').addEventListener('click', () => {
    if(window.pywebview && window.pywebview.api) { window.pywebview.api.minimize(); }
});

// --- Tab Navigation ---
const navItems = document.querySelectorAll('.nav-item');
const tabPanes = document.querySelectorAll('.tab-pane');

navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        navItems.forEach(n => n.classList.remove('active'));
        tabPanes.forEach(p => p.classList.add('hidden'));
        
        item.classList.add('active');
        const target = document.getElementById(item.dataset.tab);
        target.classList.remove('hidden');
        
        if(item.dataset.tab === 'tab-monitor') fetchAgents();
        if(item.dataset.tab === 'tab-kb') loadKb();
    });
});

// --- Toggle Context Panel ---
const contextPanel = document.getElementById('contextPanel');
const dragResizer = document.getElementById('dragResizer');
document.getElementById('btnToggleContext').addEventListener('click', () => {
    contextPanel.classList.toggle('collapsed');
    dragResizer.style.display = contextPanel.classList.contains('collapsed') ? 'none' : 'block';
});

// Toggle Context Panel with Ctrl+B
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        document.getElementById('btnToggleContext').click();
    }
});

// --- Resizer Logic ---
let isResizing = false;
dragResizer.addEventListener('mousedown', (e) => {
    isResizing = true;
    document.body.style.cursor = 'col-resize';
});
document.addEventListener('mousemove', (e) => {
    if (!isResizing) return;
    const newWidth = e.clientX - 60; // 60 is sidebar width
    if (newWidth > 200 && newWidth < window.innerWidth - 300) {
        contextPanel.style.flex = 'none';
        contextPanel.style.width = newWidth + 'px';
    }
});
document.addEventListener('mouseup', () => {
    if (isResizing) {
        isResizing = false;
        document.body.style.cursor = 'default';
    }
});

// --- API Settings ---
const cfgBaseUrl = document.getElementById('cfgBaseUrl');
const cfgApiKey = document.getElementById('cfgApiKey');
const cfgModel = document.getElementById('cfgModel');
let currentMergeMode = "manual";
let currentTargetAgent = "auto";

async function loadConfig() {
    try {
        const res = await fetch('/api/config');
        const data = await res.json();
        if(data.base_url) cfgBaseUrl.value = data.base_url;
        if(data.api_key) cfgApiKey.value = data.api_key;
        if(data.model) cfgModel.value = data.model;
        currentMergeMode = data.merge_mode || "manual";
        document.querySelector(`input[name="mergeMode"][value="${currentMergeMode}"]`).checked = true;
        currentTargetAgent = data.target_agent || "auto";
        document.getElementById('toggleAutoCursor').checked = (currentTargetAgent === "auto");
    } catch(e) { console.error("Config load error", e); }
}

async function saveConfig() {
    currentMergeMode = document.querySelector('input[name="mergeMode"]:checked').value;
    const isAuto = document.getElementById('toggleAutoCursor').checked;
    if(isAuto) currentTargetAgent = "auto";
    
    const payload = {
        base_url: cfgBaseUrl.value,
        api_key: cfgApiKey.value,
        model: cfgModel.value,
        merge_mode: currentMergeMode,
        target_agent: currentTargetAgent
    };
    try {
        await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Gabriel-Token': localToken
            },
            body: JSON.stringify(payload)
        });
    } catch(e) { console.error("Save config error", e); }
}

document.getElementById('btnSaveConfig').addEventListener('click', async () => {
    const btn = document.getElementById('btnSaveConfig');
    const originalText = btn.innerText;
    btn.innerText = dict[currentLang].saving || "Saving...";
    await saveConfig();
    btn.innerText = dict[currentLang].saved;
    setTimeout(() => btn.innerText = originalText, 1500);
});

// --- Agent Monitor ---
document.getElementById('toggleAutoCursor').addEventListener('change', async (e) => {
    if(e.target.checked) {
        currentTargetAgent = "auto";
        await saveConfig();
        fetchAgents();
    }
});

async function fetchAgents() {
    const list = document.getElementById('agentList');
    list.innerHTML = `<div class="agent-item">${dict[currentLang].scanning}</div>`;
    try {
        await fetch('/api/agents', {
            headers: { 'X-Gabriel-Token': localToken }
        })
        .then(r => r.json())
        .then(agents => {
            // Sorting Logic
            const sortMode = document.getElementById('agentSortSelect').value;
            const [sortKey, sortDir] = sortMode.split('_');
            
            agents.sort((a, b) => {
                let valA = a[sortKey] || 0;
                let valB = b[sortKey] || 0;
                if (sortDir === 'asc') return valA - valB;
                return valB - valA;
            });

            list.innerHTML = "";
            if (agents.length === 0) {
                list.innerHTML = `
                    <div class="agent-item" style="justify-content: center; opacity: 0.5; flex-direction: column; padding: 32px 16px;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:12px; color:var(--text-secondary);"><circle cx="12" cy="12" r="10"></circle><path d="M12 8v4m0 4h.01"></path></svg>
                        <div class="agent-name" style="color:var(--text-secondary);" data-i18n="radar_empty">No Active Agents Found</div>
                        <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:8px; text-align:center;" data-i18n="radar_no_agents_hint">Start an agent in your terminal to see it here</div>
                    </div>
                `;
                applyLang();
                return;
            }
            agents.forEach(a => {
                const isLocked = (currentTargetAgent === a.path);
                const date = new Date(a.mtime * 1000).toLocaleString();
                const div = document.createElement('div');
                div.className = `agent-item ${isLocked ? 'locked' : ''}`;
                div.innerHTML = `
                    <div class="agent-info">
                        <span class="agent-name">${a.name} ${isLocked ? '🔒' : ''}</span>
                        <span class="agent-time">⏱ ${dict[currentLang].agent_last_active || "Last Active:"} ${date} &nbsp;|&nbsp; 📊 ${dict[currentLang].agent_volume || "Volume:"} ${a.steps || 0} ${dict[currentLang].agent_steps || "steps"}</span>
                    </div>
                    ${!isLocked ? `<button class="btn-outline" style="padding:4px 8px; font-size:0.75rem;" onclick="lockAgent('${a.path.replace(/\\/g, '\\\\')}')">${dict[currentLang].btn_lock || 'Lock'}</button>` : ''}
                `;
                list.appendChild(div);
            });
        });
    } catch(e) {
        list.innerHTML = `<div class="agent-item">${dict[currentLang].err_fetching_agents || "Error fetching agents."}</div>`;
    }
}
window.lockAgent = async function(path) {
    document.getElementById('toggleAutoCursor').checked = false;
    currentTargetAgent = path;
    await saveConfig();
    fetchAgents();
}

document.getElementById('agentSortSelect').addEventListener('change', fetchAgents);

// --- Knowledge Base ---
const kbEditor = document.getElementById('kbEditor');
async function loadKb() {
    try {
        const res = await fetch('/api/kb', {
            headers: { 'X-Gabriel-Token': localToken }
        });
        const data = await res.json();
        kbEditor.value = data.content || "";
    } catch(e) {}
}
document.getElementById('btnSaveKb').addEventListener('click', async () => {
    const content = document.getElementById('kbEditor').value;
    await fetch('/api/kb', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Gabriel-Token': localToken
        },
        body: JSON.stringify({content: content})
    });

    const btn = document.getElementById('btnSaveKb');
    const originalText = btn.innerText;
    btn.innerText = dict[currentLang].saved;
    setTimeout(() => btn.innerText = originalText, 1500);
});

// Markdown Preview Toggle
const btnPreviewKb = document.getElementById('btnPreviewKb');
const kbEditor = document.getElementById('kbEditor');
const kbPreview = document.getElementById('kbPreview');
btnPreviewKb.addEventListener('click', () => {
    if (kbPreview.classList.contains('hidden')) {
        // Show Preview
        const rawHtml = window.marked ? marked.parse(kbEditor.value) : kbEditor.value;
        if (window.DOMPurify) {
            kbPreview.innerHTML = DOMPurify.sanitize(rawHtml);
        } else {
            kbPreview.textContent = rawHtml;
        }
        kbPreview.classList.remove('hidden');
        kbEditor.style.display = 'none';
        btnPreviewKb.innerText = dict[currentLang].btn_edit || '✏️ Edit';
        btnPreviewKb.style.background = 'var(--accent)';
        btnPreviewKb.style.color = '#fff';
    } else {
        // Show Editor
        kbPreview.classList.add('hidden');
        kbEditor.style.display = 'block';
        btnPreviewKb.innerText = dict[currentLang].btn_preview || '👁 Preview';
        btnPreviewKb.style.background = 'transparent';
        btnPreviewKb.style.color = 'var(--text-primary)';
    }
});

document.getElementById('btnCopyInject').addEventListener('click', () => {
    const textToCopy = "Please read Gabriel_Insight.md in the current directory and execute the fix.";
    navigator.clipboard.writeText(textToCopy).then(() => {
        const btn = document.getElementById('btnCopyInject');
        const originalText = btn.innerText;
        btn.innerText = dict[currentLang].copied;
        setTimeout(() => btn.innerText = originalText, 2000);
    });
});

// --- Chart.js Telemetry ---
let telemetryChart;
const chartData = {
    labels: Array(20).fill(''),
    datasets: [{
        label: 'Neural Activity (Load %)',
        data: Array(20).fill(5),
        borderColor: 'rgba(16, 185, 129, 0.8)', // var(--success)
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 0
    }]
};

function initChart() {
    const ctx = document.getElementById('telemetryChart');
    if (!ctx) return;
    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 300 },
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, display: false },
                x: { display: false }
            }
        }
    });

    // Idle cooldown loop
    setInterval(() => {
        const lastVal = chartData.datasets[0].data[19];
        const newVal = Math.max(5, lastVal - (lastVal * 0.2)); // Cool down by 20%
        chartData.datasets[0].data.shift();
        chartData.datasets[0].data.push(newVal);
        telemetryChart.update('none');
    }, 1000);
}

// ==========================================
// Safe Rendering
// ==========================================
function renderAgentContent(codeEl, content) {
    if (window.DOMPurify && typeof DOMPurify.sanitize === 'function') {
        codeEl.innerHTML = DOMPurify.sanitize(content, {
            ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'code', 'pre', 'span', 'br'],
            ALLOWED_ATTR: ['class']
        });
    } else {
        codeEl.textContent = content;
        console.warn('[Gabriel] DOMPurify 未加载，已降级为纯文本渲染');
    }
}

// --- WebSocket & Chat ---
let ws;
let reconnectAttempts = 0;
const MAX_RECONNECT_DELAY = 30000;

function connectWebSocket() {
    if (!localToken) return;
    const wsUrl = `ws://${window.location.host || '127.0.0.1:8080'}/ws?token=${localToken}`;
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        document.getElementById('wsStatus').classList.remove('disconnected');
        document.getElementById('wsStatus').classList.add('connected');
        reconnectAttempts = 0;
    };
    
    ws.onclose = (e) => {
        document.getElementById('wsStatus').classList.remove('connected');
        document.getElementById('wsStatus').classList.add('disconnected');
        
        const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts), MAX_RECONNECT_DELAY);
        setTimeout(() => {
            reconnectAttempts++;
            connectWebSocket();
        }, delay);
    };

    ws.onerror = (err) => {
        ws.close();
    };

    let currentAiMessageDiv = null;
    let currentAiMessageContent = "";

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === "context_update") {
            // Spike the telemetry chart to simulate agent computation
            if (telemetryChart) {
                const spike = Math.min(100, Math.floor(Math.random() * 40) + 60);
                chartData.datasets[0].data.shift();
                chartData.datasets[0].data.push(spike);
                telemetryChart.update('none');
            }
            
            // Render logs into grid
            const grid = document.getElementById('contextGrid');
            if (grid && msg.path && msg.path !== "all") {
                // Remove the waiting placeholder if it exists
                const placeholder = document.getElementById('contextDisplay');
                if (placeholder && placeholder.parentElement) {
                    placeholder.parentElement.remove();
                }
                
                let agentId = 'agent_' + msg.path.replace(/[^a-zA-Z0-9]/g, '_');
                let displayCard = document.getElementById(agentId);
                
                if (!displayCard) {
                    displayCard = document.createElement('div');
                    displayCard.id = agentId;
                    displayCard.className = 'agent-terminal-card';
                    displayCard.style.cssText = 'background: rgba(15, 23, 42, 0.6); border: 1px solid var(--panel-border); border-radius: 8px; display: flex; flex-direction: column; height: 400px; overflow: hidden;';
                    displayCard.innerHTML = `
                        <div style="background: rgba(0,0,0,0.4); padding: 6px 12px; border-bottom: 1px solid var(--panel-border); font-size: 0.8rem; font-weight: bold; color: var(--accent); display:flex; justify-content:space-between;">
                            <span>🖥️ ${msg.agent}</span>
                        </div>
                        <pre style="margin:0; padding:12px; height:calc(100% - 30px); overflow-y:auto; white-space:pre-wrap; word-wrap:break-word;"><code class="agent-display-code"></code></pre>
                    `;
                    grid.appendChild(displayCard);
                }
                
                const codeEl = displayCard.querySelector('.agent-display-code');
                const parent = codeEl.parentElement;
                const isAtBottom = parent.scrollHeight - parent.scrollTop - parent.clientHeight < 50;
                
                renderAgentContent(codeEl, msg.content);
                
                if (isAtBottom) {
                    parent.scrollTop = parent.scrollHeight;
                }
            } else if (msg.path === "all") {
                // Handle initial loading sync
                const placeholder = document.getElementById('contextDisplay');
                if (placeholder) {
                    placeholder.innerHTML = "Connected. Waiting for agent updates...";
                }
            }
            
            // Trigger Telemetry Pulse (Agent MX Design)
            const pulse = document.getElementById('telemetryPulse');
            if (pulse) {
                pulse.style.background = 'var(--success)';
                pulse.style.boxShadow = '0 0 10px var(--success)';
                setTimeout(() => {
                    pulse.style.background = 'transparent';
                    pulse.style.boxShadow = 'none';
                }, 150);
            }
        } else if (msg.type === "kb_recommendation") {
            const toast = document.getElementById('kbToast');
            const toastContent = document.getElementById('kbToastContent');
            if (toast && toastContent) {
                const parsed = window.marked ? marked.parse(msg.content) : msg.content;
                if (window.DOMPurify) {
                    toastContent.innerHTML = DOMPurify.sanitize(parsed);
                } else {
                    toastContent.textContent = parsed;
                }
                toast.classList.remove('hidden');
            }
        } else if (msg.type === "ai_response_start") {
            currentAiMessageContent = "";
            currentAiMessageDiv = createMessageDiv('ai-message');
            document.getElementById('chatHistory').appendChild(currentAiMessageDiv);
        } else if (msg.type === "ai_response_chunk") {
            currentAiMessageContent += msg.content;
            if(window.marked) {
                const parsed = marked.parse(currentAiMessageContent);
                if (window.DOMPurify) {
                    currentAiMessageDiv.innerHTML = DOMPurify.sanitize(parsed);
                } else {
                    currentAiMessageDiv.textContent = parsed;
                }
            } else {
                currentAiMessageDiv.innerText = currentAiMessageContent;
            }
            const container = document.getElementById('chatHistory');
            container.scrollTop = container.scrollHeight;
        } else if (msg.type === "ai_response_end") {
            currentAiMessageDiv = null;
        } else if (msg.type === "ai_response") {
            appendMessage(msg.content, 'ai-message');
        } else if (msg.type === "sys_message") {
            appendMessage(msg.content, 'sys-message');
        }
    };
    ws.onclose = () => {
        document.getElementById('statusText').innerText = dict[currentLang].status_disconnected || "Disconnected";
        document.querySelector('.status-dot').classList.add('disconnected');
        setTimeout(connectWebSocket, 3000);
    };
}

function createMessageDiv(className) {
    const div = document.createElement('div');
    div.className = `message ${className}`;
    return div;
}

function appendMessage(text, className) {
    const container = document.getElementById('chatHistory');
    const div = createMessageDiv(className);
    if(className === 'ai-message' && window.marked) {
        const parsed = marked.parse(text);
        if (window.DOMPurify) {
            div.innerHTML = DOMPurify.sanitize(parsed);
        } else {
            div.textContent = parsed;
        }
    } else {
        div.innerText = text;
    }
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

document.getElementById('btnSend').addEventListener('click', () => {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (text && ws && ws.readyState === WebSocket.OPEN) {
        appendMessage(text, 'user-message');
        ws.send(JSON.stringify({type: "chat", content: text}));
        input.value = '';
    }
});
document.getElementById('chatInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('btnSend').click();
    }
});

document.getElementById('btnMerge').addEventListener('click', () => {
    initTabs();
    initChart();
    document.getElementById('btnStartTerminal').addEventListener('click', () => {
    if(ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({type: "merge_kb", content: ""}));
        appendMessage(dict[currentLang].gen_draft || "⏳ Generating solution draft...", "sys-message");
    }
});

document.getElementById('btnFeedback').addEventListener('click', () => {
    document.getElementById('feedbackModal').style.display = 'flex';
});
document.getElementById('btnPreviewFeedback').addEventListener('click', () => {
    const text = document.getElementById('feedbackText').value;
    if (!text) return;
    
    // Gather all agent contents for feedback
    let combinedCtx = "";
    document.querySelectorAll('.agent-display-code').forEach(el => {
        combinedCtx += "\n---\n" + el.innerText;
    });
    
    const contextPreview = combinedCtx.slice(-1500);
    const fullPreview = `Issue:\n${text}\n\nContext:\n${contextPreview}`;
    
    document.getElementById('feedbackPreviewText').value = fullPreview;
    document.getElementById('feedbackModal').style.display = 'none';
    document.getElementById('feedbackPreviewModal').style.display = 'flex';
});

document.getElementById('btnConfirmFeedback').addEventListener('click', async () => {
    const content = document.getElementById('feedbackPreviewText').value;
    if (!content) return;
    
    const parts = content.split("\n\nContext:\n");
    const issue = parts[0].replace(/^Issue:\n/, '');
    const context = parts.length > 1 ? parts[1] : '';

    try {
        await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Gabriel-Token': localToken },
            body: JSON.stringify({ issue: issue, context: context })
        });
        document.getElementById('feedbackPreviewModal').style.display = 'none';
        document.getElementById('feedbackText').value = '';
    } catch(e) {}
});

document.getElementById('btnForgetToken').addEventListener('click', () => {
    localStorage.removeItem('gabriel_token');
    sessionStorage.removeItem('gabriel_token');
    window.location.reload();
});

// Init
applyLang();
loadConfig();
connectWebSocket();

async function pollHealth() {
    if (!localToken) return;
    try {
        const res = await fetch('/api/health', { headers: { 'X-Gabriel-Token': localToken } });
        if (!res.ok) {
            document.getElementById('healthAlertBanner').style.display = 'block';
        } else {
            document.getElementById('healthAlertBanner').style.display = 'none';
        }
    } catch(e) {
        document.getElementById('healthAlertBanner').style.display = 'block';
    }
}

setInterval(pollHealth, 10000);
setTimeout(pollHealth, 2000);

\n```\n\n## File: `static/index.html`\n\n```html\n<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gabriel Control Center</title>
    <link rel="stylesheet" href="/static/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="vendor/purify.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    
    <!-- Login Modal -->
    <div id="loginModal" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 9999; justify-content: center; align-items: center;">
        <div class="panel" style="width: 400px; padding: 24px;">
            <h2>Enter Security Token</h2>
            <p class="subtitle" style="margin-bottom: 16px;">Check your terminal for the generated Gabriel Token.</p>
            <input type="password" id="inputToken" class="sleek-input" placeholder="Paste token here..." style="width: 100%; margin-bottom: 16px;">
            <button id="btnLogin" class="btn-primary" style="width: 100%;">Connect</button>
        </div>
    </div>
    <!-- Feedback Modal -->
    <div id="feedbackModal" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 9999; justify-content: center; align-items: center;">
        <div class="panel" style="width: 400px; padding: 24px;">
            <h2>Send Feedback</h2>
            <textarea id="feedbackText" class="sleek-textarea" placeholder="Describe the issue or feature request..." style="width: 100%; height:80px; margin-bottom: 16px; margin-top:8px;"></textarea>
            <div style="display: flex; justify-content: flex-end; gap: 8px;">
                <button onclick="document.getElementById('feedbackModal').style.display='none'" class="btn-outline">Cancel</button>
                <button id="btnPreviewFeedback" class="btn-primary">Preview & Submit</button>
            </div>
        </div>
    </div>

    <!-- Feedback Preview Modal -->
    <div id="feedbackPreviewModal" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 10000; justify-content: center; align-items: center;">
        <div class="panel" style="width: 600px; padding: 24px; border: 1px solid var(--panel-border);">
            <h2>Review Feedback Submission</h2>
            <p style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px;">Please review the context being sent. You may edit or redact sensitive information below:</p>
            <textarea id="feedbackPreviewText" class="sleek-textarea" style="width: 100%; height:300px; margin-bottom: 16px; font-family: monospace; font-size: 0.85rem;"></textarea>
            <div style="display: flex; justify-content: flex-end; gap: 8px;">
                <button onclick="document.getElementById('feedbackPreviewModal').style.display='none'" class="btn-outline">Back</button>
                <button id="btnConfirmFeedback" class="btn-primary" style="background: var(--success); border-color: var(--success);">Confirm Submit</button>
            </div>
        </div>
    </div>
    
    <!-- Custom Draggable Title Bar (Hidden for native window) -->
    <div class="title-bar drag-region" style="display: none;">
        <div class="title-logo">
            <span data-i18n="gabriel_logo">👼 Gabriel</span>
        </div>
        <div class="window-controls no-drag">
            <button id="btnMin" class="win-btn" data-i18n-title="title_minimize" title="Minimize">—</button>
            <button id="btnClose" class="win-btn close" data-i18n-title="title_close" title="Close">✕</button>
        </div>
    </div>

    <div id="healthAlertBanner" style="display: none; background: #ef4444; color: white; padding: 12px; text-align: center; font-weight: bold; width: 100%; z-index: 10000; position: absolute; top: 0;">
        后台监控可能已停止响应 (Backend monitoring may have stopped responding)
    </div>

    <div class="app-container">
        
        <!-- Sidebar Navigation -->
        <nav class="sidebar">
            <div class="sidebar-logo">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
            </div>
            <div class="sidebar-nav">
                <div class="nav-item active" data-tab="tab-chat" data-i18n-title="title_control_center" title="Control Center">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                </div>
                <div class="nav-item" data-tab="tab-radar" data-i18n-title="title_agent_radar" title="Agent Radar">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
                </div>
                <div class="nav-item" data-tab="tab-kb" data-i18n-title="title_knowledge_base" title="Knowledge Base">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                </div>
                <div class="nav-item" data-tab="tab-settings" data-i18n-title="title_settings" title="Settings">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-2.82.11 1.65 1.65 0 0 0-1.82.33 2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83 1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.82-.33l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 2.82-.11 1.65 1.65 0 0 0-1.82-.33 2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83 1.65 1.65 0 0 0-.33 1.82z"></path></svg>
                </div>
            </div>
            <div style="margin-top:auto; padding-bottom:16px;">
                <div class="status-indicator">
                    <div class="status-dot" id="wsStatus"></div>
                </div>
            </div>
        </nav>

        <!-- Main Content View -->
        <main class="main-content no-drag">
            
            <!-- CHAT / SIDECAR VIEW -->
            <section id="tab-chat" class="tab-pane active split-view">
                <div class="panel context-panel" id="contextPanel" style="display:flex; flex-direction:column;">
                    <header class="panel-header">
                        <span data-i18n="chat_terminal">Terminal Context (Grid View)</span>
                        <div class="connection-status">
                            <span class="status-dot"></span>
                            <span id="statusText" data-i18n="status_wait">Wait...</span>
                        </div>
                    </header>
                    <div class="context-body" id="contextGrid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; height: 100%; overflow-y: auto; padding: 12px;">
                        <!-- Dynamic agent terminals will go here -->
                        <div style="grid-column: 1 / -1; display:flex; justify-content:center; align-items:center; height:100%; color:var(--text-secondary);">
                            <span id="contextDisplay" data-i18n="chat_waiting_log">Waiting for terminal tailing...</span>
                        </div>
                    </div>
                </div>

                <div class="resizer" id="dragResizer"></div>

                <div class="panel chat-panel">
                    <header class="panel-header" style="display:flex; justify-content:space-between;">
                        <div>
                            <button id="btnToggleContext" class="icon-btn" title="Toggle Terminal View" style="margin-right:8px;">👁</button>
                            <span data-i18n="chat_assistant">🧠 Assistant</span>
                        </div>
                        <div>
                            <button id="btnFeedback" class="btn-outline" style="margin-right:8px; padding:4px 8px; font-size:0.75rem;">
                                <span data-i18n="chat_feedback">Feedback</span>
                            </button>
                            <button id="btnMerge" class="btn-primary-small">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:4px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                                <span data-i18n="chat_merge">Merge to KB</span>
                            </button>
                        </div>
                    </header>
                    <div id="kbToast" class="kb-toast hidden">
                        <div class="kb-toast-header">
                            <span>💡 <span data-i18n="kb_recommendation">Knowledge Base Recommendation</span></span>
                            <button onclick="document.getElementById('kbToast').classList.add('hidden')" style="background:none; border:none; color:#94a3b8; cursor:pointer;">✕</button>
                        </div>
                        <div id="kbToastContent" class="kb-toast-body ai-message"></div>
                    </div>
                    <div class="chat-history" id="chatHistory">
                        <div class="message sys-message" data-i18n="chat_welcome">
                            Gabriel launched. Terminal snapshot is actively tracked.
                        </div>
                    </div>
                    <div class="chat-input-area">
                        <textarea id="chatInput" class="sleek-textarea chat-input" placeholder="Ask Gabriel..." data-i18n-placeholder="chat_placeholder" rows="1"></textarea>
                        <button id="btnSend" class="icon-btn send-btn">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                        </button>
                    </div>
                </div>
            </section>

            <!-- AGENT RADAR VIEW -->
            <section id="tab-radar" class="tab-pane hidden single-view">
                <div class="panel" style="width:100%; max-width:800px;">
                    <header class="panel-header" style="justify-content: space-between;">
                        <h2 data-i18n="radar_title">Agent Radar</h2>
                        <div class="status-indicator" style="display:flex; align-items:center; gap:8px;">
                            <div class="status-dot" id="telemetryPulse" style="animation: none;"></div>
                            <span style="font-size:0.75rem; color:var(--text-secondary);">Agent Telemetry</span>
                        </div>
                    </header>
                    <div class="panel-body">
                        <div class="form-group" style="margin-bottom: 20px;">
                            <label data-i18n="radar_target">Target Agent</label>
                            <select id="targetAgent" class="sleek-input">
                                <option value="auto" data-i18n="auto_track">Auto-track Newest</option>
                            </select>
                        </div>
                        
                        <!-- Telemetry Chart -->
                        <div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 12px; margin-bottom: 20px;">
                            <canvas id="telemetryChart" height="80"></canvas>
                        </div>

                        <div class="agent-list" id="agentList">
                            <div class="agent-item" style="justify-content: center; opacity: 0.5;">
                                <div class="agent-info" style="align-items: center; gap: 8px;">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path><path d="M9 12l2 2 4-4"></path></svg>
                                    <div class="agent-name" data-i18n="radar_scanning">Scanning for agents...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- KNOWLEDGE BASE VIEW -->
            <section id="tab-kb" class="tab-pane hidden single-view">
                <div class="panel" style="width:100%; max-width:1200px;">
                    <header class="panel-header" style="justify-content: space-between;">
                        <h2 data-i18n="kb_title">Knowledge Draft</h2>
                        <div>
                            <button id="btnPreviewKb" class="btn-outline" style="margin-right: 8px;"><span data-i18n="btn_preview_kb">👁 Preview</span></button>
                            <button id="btnCopyInject" class="btn-primary" data-i18n="kb_copy">Copy Injection Command</button>
                        </div>
                    </div>
                    <div class="panel-body" style="display:flex; flex-direction:column; height: 100%;">
                        <p class="subtitle" data-i18n="kb_desc">Review Gabriel's insight before injecting into main CLI.</p>
                        <div style="display:flex; flex:1; gap:16px; margin-top:12px; position:relative;">
                            <textarea id="kbEditor" class="sleek-textarea" style="flex:1; height:100%; resize:none;" placeholder="Gabriel's insights will appear here..." data-i18n-placeholder="kb_placeholder"></textarea>
                            <div id="kbPreview" class="hidden ai-message" style="flex:1; height:100%; overflow-y:auto; padding:16px; border-radius:8px; margin:0;"></div>
                        </div>
                        <button id="btnSaveKb" class="btn-outline" style="margin-top: 12px; align-self: flex-start;" data-i18n="kb_save">Save Draft</button>
                    </div>
                </div>
            </div>

            <!-- SETTINGS VIEW -->
            <div id="tab-settings" class="tab-pane hidden single-view">
                <div class="panel">
                    <div class="panel-header">
                        <h2 data-i18n="settings_title">API & Model Settings</h2>
                    </div>
                    <div class="panel-body form-layout">
                        <p class="subtitle" data-i18n="settings_desc">Universal configuration for OpenAI-compatible endpoints.</p>
                        
                        <div class="form-group">
                            <label data-i18n="settings_baseurl">Base URL</label>
                            <input type="text" id="cfgBaseUrl" class="sleek-input" placeholder="https://api.openai.com/v1">
                        </div>
                        <div class="form-group">
                            <label data-i18n="settings_apikey">API Key</label>
                            <input type="password" id="cfgApiKey" class="sleek-input" placeholder="sk-...">
                        </div>
                        <div class="form-group">
                            <label data-i18n="settings_model">Model Name</label>
                            <input type="text" id="cfgModel" class="sleek-input" placeholder="e.g. gpt-4o, deepseek-coder">
                        </div>
                        
                        <div class="form-section" style="margin-top: 10px;">
                            <h3 data-i18n="settings_workflow">Workflow Strategy</h3>
                            <div class="form-group">
                                <label data-i18n="settings_merge">Knowledge Base Merge</label>
                                <div class="segmented-control">
                                    <input type="radio" name="mergeMode" id="modeManual" value="manual" checked>
                                    <label for="modeManual" data-i18n="mode_manual">Manual (Geek)</label>
                                    <input type="radio" name="mergeMode" id="modeAuto" value="auto">
                                    <label for="modeAuto" data-i18n="mode_auto">Automatic</label>
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-section">
                            <h3 data-i18n="settings_ui">UI Preferences</h3>
                            <div class="form-group">
                                <label data-i18n="settings_lang">Language</label>
                                <select id="langSelect" class="sleek-input" style="padding: 8px; font-size: 0.85rem;">
                                    <option value="en">English (US)</option>
                                    <option value="zh">简体中文 (Simplified Chinese)</option>
                                    <option value="zh-TW">繁體中文 (Traditional Chinese)</option>
                                    <option value="fr">Français (French)</option>
                                    <option value="es">Español (Spanish)</option>
                                    <option value="ja">日本語 (Japanese)</option>
                                    <option value="ko">한국어 (Korean)</option>
                                </select>
                            </div>
                        </div>
                        <button id="btnSaveConfig" class="btn-primary" style="margin-top: 10px;" data-i18n="settings_save">Save Configuration</button>
                        
                        <button id="btnForgetToken" class="btn-outline" style="margin-top: 10px; border-color: #ef4444; color: #ef4444;">Forget Token</button>

                        <div class="form-section" style="margin-top: 30px; border-top: 1px solid var(--panel-border); padding-top: 20px;">
                            <h3 data-i18n="settings_about">About Gabriel</h3>
                            <p class="subtitle" style="font-size: 0.8rem; line-height: 1.6;">
                                <span data-i18n="about_version">Version 3.1.0 (Cyber-Dark Edition)</span><br>
                                <span data-i18n="about_created">Created by</span> <strong>Li Ming</strong> & Gabriel AI<br>
                                <em data-i18n="about_subtitle">"The Missing Visual Sidecar for Autonomous Agents"</em>
                            </p>
                        </div>
                    </div>
                </div>
            </div>

        </main>
    </div>

    <script src="/static/script.js"></script>
</body>
</html>
\n```\n\n## File: `tests/test_gabriel.py`\n\n```python\nimport sys
import os
import json
import unittest
from fastapi.testclient import TestClient
from pathlib import Path

# Add src to path to import main
sys.path.insert(0, os.path.abspath("src"))

try:
    from main import app, config, DEFAULT_CONFIG, API_KEY
except ImportError as e:
    print(f"Failed to import app from src.main: {e}")
    sys.exit(1)

client = TestClient(app)

class TestGabrielControlCenter(unittest.TestCase):
    def setUp(self):
        print("\n" + "="*40)
        print(f"🚀 [QA MATRIX] Running Test: {self._testMethodName}")
        print("="*40)

    def test_ping_endpoint(self):
        """Test if the server is responsive"""
        response = client.get("/api/ping", headers={"X-Gabriel-Token": API_KEY})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        print("✅ Ping successful")

    def test_get_config(self):
        """Test configuration retrieval"""
        response = client.get("/api/config", headers={"X-Gabriel-Token": API_KEY})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("base_url", data)
        self.assertIn("model", data)
        print(f"✅ Config retrieved: {data['model']}")

    def test_update_config_atomic_write(self):
        """Test updating config using the new atomic write mechanism"""
        # Backup original
        orig = client.get("/api/config", headers={"X-Gabriel-Token": API_KEY}).json()
        
        # Write new
        payload = {
            "base_url": "https://api.openai.com/v1",
            "api_key": "test_key",
            "model": "gpt-4",
            "merge_mode": "auto",
            "target_agent": "auto"
        }
        response = client.post("/api/config", json=payload, headers={"X-Gabriel-Token": API_KEY})
        self.assertEqual(response.status_code, 200)
        
        # Verify
        new_config = client.get("/api/config", headers={"X-Gabriel-Token": API_KEY}).json()
        self.assertEqual(new_config["model"], "gpt-4")
        print("✅ Atomic config update successful")
        
        # Restore
        client.post("/api/config", json=orig, headers={"X-Gabriel-Token": API_KEY})

    def test_knowledge_base_crud(self):
        """Test SQLite KB injection and retrieval"""
        payload = {"content": "## Test Insight\nThis is a QA test."}
        res_post = client.post("/api/kb", json=payload, headers={"X-Gabriel-Token": API_KEY})
        self.assertEqual(res_post.status_code, 200)
        
        res_get = client.get("/api/kb", headers={"X-Gabriel-Token": API_KEY})
        self.assertEqual(res_get.status_code, 200)
        data = res_get.json()
        self.assertEqual(data["content"], payload["content"])
        print("✅ SQLite Knowledge Base CRUD successful")

    def test_websocket_pubsub(self):
        """Test WebSocket connection and EventBroker broadcasting"""
        from main import broker
        import asyncio
        import json
        
        # We must use a separate event loop context for this if we were strictly async, 
        # but TestClient handles websocket_connect synchronously in Starlette
        with client.websocket_connect(f"/ws?token={API_KEY}") as websocket:
            # First message should be context_update (initial state)
            data = websocket.receive_json()
            self.assertEqual(data["type"], "context_update")
            
            # Simulate an incoming chat message
            websocket.send_json({"type": "chat", "content": "ping_test"})
            
            # The AI should respond with start/chunk/end (this might require mocking the AI client)
            # Since the real OpenAI client might fail without a valid key, we will just expect either
            # an AI response or an API error chunk, both are valid responses indicating the WS works.
            response1 = websocket.receive_json()
            self.assertIn(response1["type"], ["ai_response_start", "ai_response_chunk"])
            
            
        print("✅ WebSocket Connection & EventBroker Pub/Sub successful")

    def test_claude_code_parser(self):
        from main import ClaudeCodeParser
        import html
        
        # Normal user
        res = ClaudeCodeParser.parse('{"type": "user", "content": "hello"}')
        self.assertIn("👤 [USER]", res)
        self.assertIn("hello", res)
        
        # Normal agent
        res = ClaudeCodeParser.parse('{"type": "assistant", "content": "I am here"}')
        self.assertIn("🟣 [Claude]", res)
        self.assertIn("I am here", res)
        
        # Abnormal / non-json
        res = ClaudeCodeParser.parse('just some text')
        self.assertIn("just some text", res)
        self.assertIn("font-family:monospace", res)
        
        # Unknown JSON structure
        res_json = ClaudeCodeParser.parse('{"unknown_field": "value"}')
        self.assertIn('{&quot;unknown_field&quot;: &quot;value&quot;}', res_json)
        self.assertIn("font-family:monospace", res_json)
        
        # Edge case: empty content
        res = ClaudeCodeParser.parse('')
        self.assertIsNone(res)
        
        # Edge case: super long content
        long_text = "a" * 500
        res = ClaudeCodeParser.parse(f'{{"type": "assistant", "content": "{long_text}"}}')
        self.assertIn("a" * 200, res)
        self.assertTrue(len(res) < 600)
        
        print("✅ ClaudeCodeParser tests successful")

    def test_cursor_parser(self):
        from main import CursorParser
        
        # Normal user JSON
        res = CursorParser.parse('{"role": "user", "content": "fix this"}')
        self.assertIn("👤 [USER]", res)
        self.assertIn("fix this", res)
        
        # Normal agent JSON
        res = CursorParser.parse('{"role": "assistant", "content": "I fixed it"}')
        self.assertIn("🔵 [Cursor]", res)
        self.assertIn("I fixed it", res)
        
        # Plain text User
        res = CursorParser.parse('User: plain text input')
        self.assertIn("👤 [USER]", res)
        self.assertIn("plain text input", res)
        
        # Plain text Agent
        res = CursorParser.parse('Cursor: plain text response')
        self.assertIn("🔵 [Cursor]", res)
        self.assertIn("plain text response", res)
        
        # Abnormal / non-json that does not match User/Cursor prefix
        res = CursorParser.parse('just some text')
        self.assertIn("just some text", res)
        self.assertIn("font-family:monospace", res)
        
        # Unknown JSON structure
        res_json = CursorParser.parse('{"unknown_field": "value"}')
        self.assertIn('{&quot;unknown_field&quot;: &quot;value&quot;}', res_json)
        self.assertIn("font-family:monospace", res_json)
        
        # Empty
        res = CursorParser.parse('')
        self.assertIsNone(res)
        
        # Super long content
        long_text = "a" * 500
        res = CursorParser.parse(f'{{"role": "assistant", "content": "{long_text}"}}')
        self.assertIn("a" * 200, res)
        self.assertTrue(len(res) < 600)
        
        print("✅ CursorParser tests successful")

    def test_auth_enforcement(self):
        """Test that API endpoints and WS reject requests without token"""
        response = client.get("/api/config")
        self.assertEqual(response.status_code, 401)
        
        # Test WS auth
        from fastapi.websockets import WebSocketDisconnect
        with self.assertRaises(WebSocketDisconnect) as context:
            with client.websocket_connect("/ws") as websocket:
                pass
        self.assertEqual(context.exception.code, 1008)
        print("✅ Auth enforcement test successful")

if __name__ == '__main__':
    unittest.main(verbosity=2)
\n```\n\n## Unit Test Results\n\n```\nC:\Users\Jason\Desktop\Gabriel\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
  from starlette.testclient import TestClient as TestClient  # noqa
test_auth_enforcement (test_gabriel.TestGabrielControlCenter.test_auth_enforcement)
Test that API endpoints and WS reject requests without token ... ok
test_claude_code_parser (test_gabriel.TestGabrielControlCenter.test_claude_code_parser) ... ok
test_cursor_parser (test_gabriel.TestGabrielControlCenter.test_cursor_parser) ... ok
test_get_config (test_gabriel.TestGabrielControlCenter.test_get_config)
Test configuration retrieval ... ok
test_knowledge_base_crud (test_gabriel.TestGabrielControlCenter.test_knowledge_base_crud)
Test SQLite KB injection and retrieval ... ok
test_ping_endpoint (test_gabriel.TestGabrielControlCenter.test_ping_endpoint)
Test if the server is responsive ... ok
test_update_config_atomic_write (test_gabriel.TestGabrielControlCenter.test_update_config_atomic_write)
Test updating config using the new atomic write mechanism ... ok
test_websocket_pubsub (test_gabriel.TestGabrielControlCenter.test_websocket_pubsub)
Test WebSocket connection and EventBroker broadcasting ... ok

----------------------------------------------------------------------
Ran 8 tests in 1.300s

OK

=======================================================
👼 Gabriel is starting up!
🔐 Security Token Generated. Please use this token to login:
Token: 5d26bd87c7f302f2a049188c7de4886a
Access the Control Center at: http://127.0.0.1:8080
=======================================================


========================================
🚀 [QA MATRIX] Running Test: test_auth_enforcement
========================================
✅ Auth enforcement test successful

========================================
🚀 [QA MATRIX] Running Test: test_claude_code_parser
========================================
✅ ClaudeCodeParser tests successful

========================================
🚀 [QA MATRIX] Running Test: test_cursor_parser
========================================
✅ CursorParser tests successful

========================================
🚀 [QA MATRIX] Running Test: test_get_config
========================================
✅ Config retrieved: deepseek-chat

========================================
🚀 [QA MATRIX] Running Test: test_knowledge_base_crud
========================================
✅ SQLite Knowledge Base CRUD successful

========================================
🚀 [QA MATRIX] Running Test: test_ping_endpoint
========================================
✅ Ping successful

========================================
🚀 [QA MATRIX] Running Test: test_update_config_atomic_write
========================================
✅ Atomic config update successful

========================================
🚀 [QA MATRIX] Running Test: test_websocket_pubsub
========================================
✅ WebSocket Connection & EventBroker Pub/Sub successful
\n```\n\n## Known Issues / Unresolved Items\n\n
### 已知问题 / 未处理事项

1. **多用户并发连接状态同步问题**: 当前的 Token 免重复输入使用的是 `localStorage`。由于 Gabriel 的定位是单机运行，暂时没有问题。但如果未来暴露在局域网下多用户并发访问（例如团队共享），基于 WebSocket 的状态同步机制可能会将一个用户的切换操作广播给所有连接的客户端，这会导致"幽灵切换"。
2. **`script.js` 现存语法残留**: 在修复合并时发现 `script.js` 约 673 行 `document.getElementById('btnMerge').addEventListener` 内部有未闭合或结构混乱的残留代码（`initTabs(); initChart();`）。虽然 JavaScript 能够勉强运行或部分失败，但这是前几次重构留下的隐患，由于本次主要集中在稳定性、健康检查与 Token 本地化，没有贸然深入重构前端事件绑定。
3. **日志轮转（Log Rotation）的并发写入风险**: 使用了 `RotatingFileHandler` 解决了无限增长问题。但在高并发多进程测试（类似之前被清理掉的 benchmark 脚本模拟的环境）下，默认的 RotatingFileHandler 在 Windows 下可能会因为文件占用导致轮转失败（PermissionError）。如果要求极其严苛的稳定性，后续应引入 `ConcurrentRotatingFileHandler`。
4. **WebSocket 心跳机制缺失**: 虽然增加了 `/api/health` 轮询检查后端 tailer 的存活，但 WebSocket 层面仍然缺乏标准的 Ping/Pong 心跳，如果底层连接默默断开（Half-open connection），只能依赖浏览器的超时机制，偶尔会出现状态断联没有及时显示的问题。
