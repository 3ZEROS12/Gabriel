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
            safe_content = html.escape(str(content))
            
            if step_type == "USER_INPUT":
                return f'<div style="margin-bottom:8px;"><span style="color:#60a5fa; font-weight:bold;">👤 [USER]:</span> <span style="color:#e2e8f0;">{safe_content[:200]}...</span></div>'
            elif step_type == "PLANNER_RESPONSE":
                return f'<div style="margin-bottom:8px;"><span style="color:#d4af37; font-weight:bold;">🤖 [AGENT]:</span> <span style="color:#cbd5e1;">{safe_content[:200]}...</span></div>'
            elif step_type == "TOOL_RESPONSE":
                if len(safe_content) > 300:
                    safe_content = safe_content[:300] + "... (truncated)"
                return f'<div style="margin-bottom:8px;"><span style="color:#10b981; font-weight:bold;">🛠️ [TOOL OUTPUT]:</span><br><span style="color:#94a3b8; font-size:0.8em;">{safe_content}</span></div>'
        except:
            pass
        return None

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
        except json.JSONDecodeError:
            safe_content = html.escape(line[:200])
            return f'<div style="margin-bottom:8px;"><span style="color:#a855f7; font-weight:bold;">🟣 [Claude Code]:</span> <span style="color:#cbd5e1;">{safe_content}...</span></div>'
        
        msg_type = data.get("type") or data.get("role") or data.get("message_type") or "unknown"
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
        except json.JSONDecodeError:
            safe_content = html.escape(line[:200])
            if line.startswith("User:"):
                return f'<div style="margin-bottom:8px;"><span style="color:#60a5fa; font-weight:bold;">👤 [USER]:</span> <span style="color:#e2e8f0;">{safe_content[5:200]}...</span></div>'
            elif line.startswith("Cursor:"):
                return f'<div style="margin-bottom:8px;"><span style="color:#3b82f6; font-weight:bold;">🔵 [Cursor]:</span> <span style="color:#cbd5e1;">{safe_content[7:200]}...</span></div>'
            return f'<div style="margin-bottom:4px; font-family:monospace; color:#94a3b8; font-size:0.8em;">{safe_content}</div>'
            
        role = data.get("role") or data.get("type") or "unknown"
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



