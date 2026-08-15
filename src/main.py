import os
import sys
import uvicorn
import asyncio
import glob
import time

# Windows consoles default to cp1252 and choke on the emoji startup banner /
# test output. Keep stdout/stderr UTF-8 when the runtime supports reconfiguring.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import sqlite3
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from typing import Optional
from pydantic import BaseModel
import json
import logging
import secrets
import openai
from openai import AsyncOpenAI
import re
from collections import Counter, deque
import jieba
import jieba.analyse
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import sqlite_vec

RETRYABLE_EXCEPTIONS = (openai.APIConnectionError, openai.APITimeoutError, openai.RateLimitError)
retry_llm = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=8),
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
    reraise=True
)

_embedder_instance = None
_embedder_failed = False

def get_embedder():
    """Lazy singleton for fastembed TextEmbedding (BAAI/bge-small-zh-v1.5).
    If initialization or model loading fails, log warning and set to None.
    """
    global _embedder_instance, _embedder_failed
    if _embedder_failed:
        return None
    if _embedder_instance is None:
        try:
            from fastembed import TextEmbedding
            cache_dir = os.path.join(ROOT_DIR, ".model_cache")
            os.makedirs(cache_dir, exist_ok=True)
            _embedder_instance = TextEmbedding(model_name="BAAI/bge-small-zh-v1.5", cache_dir=cache_dir)
            logger.info("Fastembed model BAAI/bge-small-zh-v1.5 initialized successfully.")
        except Exception as e:
            logger.warning(f"Fastembed model initialization failed ({e}). Falling back to pure FTS5.")
            _embedder_failed = True
            _embedder_instance = None
    return _embedder_instance

def rrf_fuse(fts_rows: list, vec_rows: list, k: int = 60) -> list:
    """RRF Reciprocal Rank Fusion:
    fts_rows: list of (insight_id, content) from FTS5
    vec_rows: list of (insight_id, content) from sqlite-vec
    returns sorted list of (insight_id, content, score)
    """
    scores = {}
    content_map = {}

    for rank, item in enumerate(fts_rows or []):
        iid = item[0]
        content_map[iid] = item[1]
        scores[iid] = scores.get(iid, 0.0) + (1.0 / (k + rank + 1))

    for rank, item in enumerate(vec_rows or []):
        iid = item[0]
        content_map[iid] = item[1]
        scores[iid] = scores.get(iid, 0.0) + (1.0 / (k + rank + 1))

    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return [(iid, content_map[iid], scores[iid]) for iid in sorted_ids]

def search_kb(text: str, limit: int = 5) -> list:
    """统一检索管道：FTS5(分词) + sqlite-vec + RRF 融合 + 反馈加权重排。
    返回 [(insight_id, content, score)]，按 score 降序；无反馈时与纯 RRF 输出一致。
    复用：extract_keywords / tokenize_for_fts / get_embedder / store_insight_vector 同源工具。"""
    if not text or not text.strip():
        return []

    kw = extract_keywords(text)
    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    conn = sqlite3.connect(db_path)
    load_sqlite_vec(conn)
    cursor = conn.cursor()

    fts_rows = []
    if kw:
        try:
            cursor.execute(
                "SELECT rowid, content FROM insights_fts WHERE insights_fts MATCH ? ORDER BY rank LIMIT 5",
                (kw,)
            )
            fts_rows = cursor.fetchall()
        except Exception as e:
            logger.warning(f"FTS Search error: {e}")

    vec_rows = []
    embedder = get_embedder()
    if embedder and text:
        try:
            embeddings = list(embedder.embed([text]))
            if embeddings:
                query_blob = sqlite_vec.serialize_float32(embeddings[0])
                cursor.execute(
                    "SELECT v.insight_id, i.content FROM insights_vec v JOIN insights i ON v.insight_id = i.id WHERE v.embedding MATCH ? AND k = 5",
                    (query_blob,)
                )
                vec_rows = cursor.fetchall()
        except Exception as e:
            logger.warning(f"Vector search error: {e}")

    candidates = rrf_fuse(fts_rows, vec_rows)
    if not candidates:
        conn.close()
        return []

    try:
        cursor.execute("SELECT insight_id, action, COUNT(*) as cnt FROM kb_feedback GROUP BY insight_id, action")
        feedback_rows = cursor.fetchall()
        
        fb_map = {}
        for r in feedback_rows:
            iid = r[0] if isinstance(r, (tuple, list)) else r["insight_id"]
            action = r[1] if isinstance(r, (tuple, list)) else r["action"]
            cnt = r[2] if isinstance(r, (tuple, list)) else r["cnt"]
            fb_map.setdefault(iid, {})[action] = cnt

        res = []
        for rowid, content, rrf_score in candidates:
            fb = fb_map.get(rowid, {})
            useful_count = fb.get("useful", 0)
            useless_count = fb.get("useless", 0)
            favorite_count = fb.get("favorite", 0)
            unfavorite_count = fb.get("unfavorite", 0)

            effective_favorite = max(0, favorite_count - unfavorite_count)
            total_votes = useful_count + useless_count + effective_favorite

            if useless_count >= 2:
                score = -10.0
            else:
                base = rrf_score
                delta = (useful_count - 0.8 * useless_count + 1.5 * effective_favorite) / max(1, total_votes) if total_votes > 0 else 0.0
                score = base + delta

            if score > -5.0:
                res.append((rowid, content, score))

        res.sort(key=lambda x: x[2], reverse=True)
        return res[:limit]
    except Exception as e:
        logger.error(f"search_kb error: {e}")
        return [(c[0], c[1], c[2]) for c in candidates[:limit]]
    finally:
        conn.close()

def load_sqlite_vec(conn: sqlite3.Connection):
    try:
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
    except Exception as e:
        logger.warning(f"Could not load sqlite-vec extension: {e}")

def store_insight_vector(insight_id: int, content: str):
    embedder = get_embedder()
    if not embedder or not content or not insight_id:
        return
    try:
        embeddings = list(embedder.embed([content]))
        if embeddings:
            vec_blob = sqlite_vec.serialize_float32(embeddings[0])
            db_path = os.path.join(ROOT_DIR, "knowledge.db")
            conn = sqlite3.connect(db_path)
            try:
                init_schema(conn)
                conn.execute("INSERT OR REPLACE INTO insights_vec (insight_id, embedding) VALUES (?, ?)", (insight_id, vec_blob))
                conn.commit()
            finally:
                conn.close()
    except Exception as e:
        logger.warning(f"Failed to store vector for insight {insight_id}: {e}")

def tokenize_for_fts(text: str) -> str:
    """jieba 分词后空格拼接；英文与非词字符原样保留。供 FTS5 入库前调用。"""
    if not text:
        return ""
    return " ".join(jieba.cut(text))

def parse_structured_insight(raw: str) -> dict:
    """从 LLM 输出提取 {problem, cause, solution, tags}。
    依次尝试：```json 代码块 → 直接 json.loads → 正则抓取 JSON 对象。
    全部失败返回空 dict（调用方降级为整段 content）。"""
    if not raw:
        return {}
    m = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw, re.IGNORECASE)
    if m:
        try:
            data = json.loads(m.group(1))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    try:
        data = json.loads(raw.strip())
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    m_obj = re.search(r'\{[\s\S]*\}', raw)
    if m_obj:
        try:
            data = json.loads(m_obj.group(0))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}

def save_insight(
    content: str,
    problem: str = "",
    cause: str = "",
    solution: str = "",
    tags: str = "",
    agent_path: str = "",
    db: sqlite3.Connection | None = None
) -> int:
    """单一 KB 写入入口：insights + insights_fts(分词) + insights_vec(向量)。
    返回新 insight id；任何单步失败不得影响主流程（向量失败仅 warning）。"""
    parsed = parse_structured_insight(content)
    prob = problem or parsed.get("problem", "")
    cs = cause or parsed.get("cause", "")
    sol = solution or parsed.get("solution", "")

    if tags:
        tags_str = json.dumps(tags, ensure_ascii=False) if isinstance(tags, (list, dict)) else str(tags)
    else:
        tags_raw = parsed.get("tags", [])
        tags_str = json.dumps(tags_raw, ensure_ascii=False) if isinstance(tags_raw, (list, dict)) else str(tags_raw)

    close_db = False
    if db is None:
        db_path = os.path.join(ROOT_DIR, "knowledge.db")
        db = sqlite3.connect(db_path)
        close_db = True

    try:
        cursor = db.cursor()
        init_schema(db)
        cursor.execute(
            "INSERT INTO insights (content, problem, cause, solution, tags) VALUES (?, ?, ?, ?, ?)",
            (content, prob, cs, sol, tags_str)
        )
        insight_id = cursor.lastrowid
        tok_content = tokenize_for_fts(content)
        cursor.execute(
            "INSERT INTO insights_fts (rowid, content, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (insight_id, tok_content)
        )
        db.commit()

        kb_path = os.path.join(ROOT_DIR, "Gabriel_Insight.md")
        try:
            with open(kb_path, "a", encoding="utf-8") as f:
                f.write(f"\n\n---\n## Insight ({time.strftime('%Y-%m-%d %H:%M:%S')})\n{content}")
        except Exception as f_err:
            logger.warning(f"Failed to append to Gabriel_Insight.md: {f_err}")

        store_insight_vector(insight_id, content)

        return insight_id
    except Exception as e:
        logger.error(f"save_insight Error: {e}")
        raise e
    finally:
        if close_db:
            db.close()

import traceback
from logging.handlers import RotatingFileHandler

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

# --- Paths: code vs data separation ---
# 源码模式：代码与数据同在仓库根。
# frozen（PyInstaller）模式：静态资源在打包的只读区（_MEIPASS），
# 而数据库/配置/日志等数据必须落在 exe 旁的持久目录（否则重启即丢）。
if getattr(sys, 'frozen', False):
    DATA_DIR = os.path.dirname(os.path.abspath(sys.executable))  # exe 所在目录（可写）
    CODE_DIR = getattr(sys, '_MEIPASS', DATA_DIR)               # 打包内容（只读）
else:
    DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CODE_DIR = DATA_DIR
ROOT_DIR = DATA_DIR  # 历史引用保持（knowledge.db / config.json / .model_cache / logs）
STATIC_DIR = os.path.join(CODE_DIR, "static")  # 页面模板只读区（frozen 下为打包内容）
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Logging: 数据目录基准（frozen 下为 exe 旁，双击启动时 CWD 不可靠）---
LOG_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger("gabriel")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "gabriel.log"), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)

CONFIG_FILE = os.path.join(ROOT_DIR, "config.json")
DEFAULT_CONFIG = {
    "provider": "custom",
    "base_url": "https://api.openai.com/v1",
    "api_key": "",
    "model": "gpt-4o-mini",
    "target_agent": "auto",
    "price_input_per_m": 1.0,
    "price_output_per_m": 3.0,
    "error_alert_threshold": 5,
    "error_alert_cooldown": 60,
    "loop_detection_window": 8,
    "loop_detection_repeat": 5,
    "loop_detection_cooldown": 60,
    "stuck_retention_max": 200
}

import copy
import shutil
import tempfile
import logging

def init_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS insights (id INTEGER PRIMARY KEY, content TEXT, problem TEXT, cause TEXT, solution TEXT, tags TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    try:
        cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS insights_fts USING fts5(content, timestamp)")
    except Exception:
        pass

    load_sqlite_vec(conn)
    try:
        cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS insights_vec USING vec0(insight_id INTEGER PRIMARY KEY, embedding FLOAT[512])")
    except Exception as e:
        logger.warning(f"Failed to create vec0 table: {e}")

    cursor.execute("CREATE TABLE IF NOT EXISTS stuck_reports (id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, context TEXT, ts REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS kb_feedback (id INTEGER PRIMARY KEY, insight_id INTEGER, action TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS session_meta (id INTEGER PRIMARY KEY, agent_name TEXT, path TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP, turns INTEGER DEFAULT 0, chars INTEGER DEFAULT 0, est_cost REAL DEFAULT 0.0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY, agent_path TEXT, role TEXT, content TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS kb_meta (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS provider_configs (
            provider_id TEXT PRIMARY KEY,
            base_url TEXT,
            api_key TEXT,
            model TEXT,
            price_input REAL DEFAULT 0.0,
            price_output REAL DEFAULT 0.0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    for col_def in ["turns INTEGER DEFAULT 0", "chars INTEGER DEFAULT 0", "est_cost REAL DEFAULT 0.0",
                    "input_tokens INTEGER DEFAULT 0", "output_tokens INTEGER DEFAULT 0",
                    "cache_read_tokens INTEGER DEFAULT 0", "cache_creation_tokens INTEGER DEFAULT 0"]:
        try:
            cursor.execute(f"ALTER TABLE session_meta ADD COLUMN {col_def}")
        except Exception:
            pass
            
    for col_def in ["problem TEXT", "cause TEXT", "solution TEXT", "tags TEXT"]:
        try:
            cursor.execute(f"ALTER TABLE insights ADD COLUMN {col_def}")
        except Exception:
            pass

    # Migration to schema_version 2 (jieba fts tokenization)
    try:
        cursor.execute("SELECT value FROM kb_meta WHERE key = 'schema_version'")
        row = cursor.fetchone()
        ver = int(row[0]) if row and row[0].isdigit() else 0
    except Exception:
        ver = 0

    if ver < 2:
        try:
            cursor.execute("DROP TABLE IF EXISTS insights_fts")
            cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS insights_fts USING fts5(content, timestamp)")
            cursor.execute("SELECT id, content, timestamp FROM insights")
            rows = cursor.fetchall()
            for r_id, r_content, r_ts in rows:
                tok = tokenize_for_fts(r_content or "")
                cursor.execute("INSERT INTO insights_fts (rowid, content, timestamp) VALUES (?, ?, ?)", (r_id, tok, r_ts))
            cursor.execute("INSERT OR REPLACE INTO kb_meta (key, value) VALUES ('schema_version', '2')")
            ver = 2
        except Exception as e:
            logger.error(f"FTS5 migration failed: {e}")

    # Migration to schema_version 3 (vector embeddings backfill)
    if ver < 3:
        embedder = get_embedder()
        if embedder:
            try:
                cursor.execute("SELECT id, content FROM insights")
                rows = cursor.fetchall()
                for r_id, r_content in rows:
                    if r_content:
                        embeddings = list(embedder.embed([r_content]))
                        if embeddings:
                            vec_blob = sqlite_vec.serialize_float32(embeddings[0])
                            cursor.execute("INSERT OR REPLACE INTO insights_vec (insight_id, embedding) VALUES (?, ?)", (r_id, vec_blob))
                cursor.execute("INSERT OR REPLACE INTO kb_meta (key, value) VALUES ('schema_version', '3')")
            except Exception as e:
                logger.warning(f"Vector backfill failed: {e}")

    conn.commit()

def init_db():
    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    conn = sqlite3.connect(db_path)
    init_schema(conn)
    conn.close()

init_db()

def load_db_api_key():
    try:
        db_path = os.path.join(ROOT_DIR, "knowledge.db")
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM kb_meta WHERE key = 'user_api_key'")
            row = cur.fetchone()
            if row and row[0]:
                return row[0]
    except Exception:
        pass
    return ""

def save_db_api_key(key_str):
    if not key_str or "****" in key_str:
        return
    try:
        db_path = os.path.join(ROOT_DIR, "knowledge.db")
        with sqlite3.connect(db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO kb_meta (key, value) VALUES ('user_api_key', ?)", (key_str.strip(),))
            conn.commit()
    except Exception as e:
        logger.warning(f"Failed to persist API key to db: {e}")

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

    # If api_key in config is empty, load stored key from local database
    if not current_config.get("api_key"):
        db_key = load_db_api_key()
        if db_key:
            current_config["api_key"] = db_key

    return current_config

def save_config(cfg):
    temp_fd, temp_path = tempfile.mkstemp(dir=ROOT_DIR, prefix="cfg_tmp_")
    safe_cfg = copy.deepcopy(cfg)
    
    # Save API key to local SQLite database for persistent recovery across restarts
    api_key_to_save = safe_cfg.get("api_key", "")
    if api_key_to_save and "****" not in api_key_to_save:
        save_db_api_key(api_key_to_save)

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
        user_key = (config.get("api_key") or "").strip()
        env_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
        api_key = user_key or env_key or "dummy"

        base_url = (config.get("base_url") or "https://api.openai.com/v1").strip()
        if not base_url.endswith("/"):
            base_url += "/"

        get_ai_client._client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )
    return get_ai_client._client

current_contexts = {}
last_file = None

class ConfigModel(BaseModel):
    provider: Optional[str] = "custom"
    base_url: str
    api_key: str
    model: str
    target_agent: str
    price_input_per_m: float = 1.0
    price_output_per_m: float = 3.0
    error_alert_threshold: int = 5
    error_alert_cooldown: int = 60
    loop_detection_window: int = 8
    loop_detection_repeat: int = 5
    loop_detection_cooldown: int = 60
    stuck_retention_max: int = 200

# --- Security ---
# Read from env if present (for persistent setups), otherwise generate randomly for session
API_KEY = os.environ.get("GABRIEL_TOKEN", secrets.token_hex(16))
print(f"\n=======================================================")
print(f"🕊️ Gabriel is starting up!")
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

def load_db_provider_configs():
    providers = {}
    try:
        db_path = os.path.join(ROOT_DIR, "knowledge.db")
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT provider_id, base_url, api_key, model, price_input, price_output FROM provider_configs")
            rows = cur.fetchall()
            for r in rows:
                providers[r["provider_id"]] = {
                    "base_url": r["base_url"] or "",
                    "api_key": r["api_key"] or "",
                    "model": r["model"] or "",
                    "price_input": r["price_input"] or 0.0,
                    "price_output": r["price_output"] or 0.0
                }
    except Exception as e:
        logger.warning(f"Failed to load provider configs from db: {e}")
    return providers

def save_db_provider_config(provider_id, base_url, api_key, model, price_input=0.0, price_output=0.0):
    if not provider_id:
        return
    try:
        db_path = os.path.join(ROOT_DIR, "knowledge.db")
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            if api_key and "****" in api_key:
                cur.execute("SELECT api_key FROM provider_configs WHERE provider_id = ?", (provider_id,))
                row = cur.fetchone()
                if row and row[0]:
                    api_key = row[0]
                else:
                    api_key = ""
            conn.execute("""
                INSERT OR REPLACE INTO provider_configs (provider_id, base_url, api_key, model, price_input, price_output, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (provider_id, (base_url or "").strip(), (api_key or "").strip(), (model or "").strip(), float(price_input or 0.0), float(price_output or 0.0)))
            conn.commit()
    except Exception as e:
        logger.warning(f"Failed to save provider config '{provider_id}' to db: {e}")

@api_router.get("/config")
async def get_config():
    cfg = load_config()
    db_providers = load_db_provider_configs()
    api_key = cfg.get("api_key", "")
    if api_key:
        if len(api_key) > 8:
            cfg["api_key"] = api_key[:3] + "****" + api_key[-3:]
        else:
            cfg["api_key"] = "****"
            
    masked_providers = {}
    for pid, pdata in db_providers.items():
        k = pdata.get("api_key", "")
        m_k = (k[:3] + "****" + k[-3:]) if len(k) > 6 else ("****" if k else "")
        masked_providers[pid] = {
            "base_url": pdata.get("base_url", ""),
            "api_key": m_k,
            "model": pdata.get("model", ""),
            "price_input": pdata.get("price_input", 0.0),
            "price_output": pdata.get("price_output", 0.0)
        }
    cfg["providers"] = masked_providers
    return JSONResponse(cfg)

@api_router.post("/config")
async def update_config(cfg: ConfigModel):
    global config
    try:
        new_cfg = cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict()
        input_key = (new_cfg.get("api_key") or "").strip()
        provider_id = (new_cfg.get("provider") or "custom").strip()
        
        db_providers = load_db_provider_configs()
        saved_provider_data = db_providers.get(provider_id, {})
        
        if not input_key or "****" in input_key:
            new_cfg["api_key"] = saved_provider_data.get("api_key") or config.get("api_key", "")
        else:
            new_cfg["api_key"] = input_key
            save_db_api_key(input_key)

        save_db_provider_config(
            provider_id=provider_id,
            base_url=new_cfg.get("base_url", ""),
            api_key=new_cfg.get("api_key", ""),
            model=new_cfg.get("model", ""),
            price_input=new_cfg.get("price_input_per_m", 0.0),
            price_output=new_cfg.get("price_output_per_m", 0.0)
        )

        config.update(new_cfg)
        save_config(config)
        
        # Reset cached client if config changed
        if hasattr(get_ai_client, "_client"):
            delattr(get_ai_client, "_client")
            
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class TestConfigModel(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None

@api_router.post("/config/test")
async def test_config(req: TestConfigModel):
    try:
        test_base_url = (req.base_url or config.get("base_url") or "https://api.openai.com/v1").strip()
        test_api_key = (req.api_key or "").strip()
        test_model = (req.model or config.get("model") or "gpt-4o-mini").strip()
        
        if "****" in test_api_key:
            test_api_key = (config.get("api_key") or "").strip()

        if not test_api_key or test_api_key == "dummy":
            return JSONResponse({
                "status": "error",
                "message": "API Key 为空，请输入有效的 API Key 后再进行连接测试。"
            }, status_code=400)

        if not test_base_url.endswith("/"):
            test_base_url += "/"

        # Provider mismatch heuristic diagnosis
        if test_api_key.startswith("sk-") and "generativelanguage.googleapis.com" in test_base_url:
            return JSONResponse({
                "status": "error",
                "message": "接口 Base URL 冲突：您输入的 Key 为 OpenAI/DeepSeek 格式，但当前 Base URL 为 Google Gemini。请在【服务商预设】下拉菜单中选择对应服务商。"
            }, status_code=400)

        test_client = AsyncOpenAI(
            base_url=test_base_url,
            api_key=test_api_key
        )

        await asyncio.wait_for(
            test_client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=2
            ),
            timeout=10.0
        )

        return JSONResponse({
            "status": "ok",
            "message": f"✅ 连接测试成功！模型 '{test_model}' 响应正常。"
        })
    except asyncio.TimeoutError:
        return JSONResponse({
            "status": "error",
            "message": "❌ 连接超时 (10s)：无法连接到指定 Base URL，请检查网络或 URL 拼写。"
        }, status_code=504)
    except openai.AuthenticationError as e:
        return JSONResponse({
            "status": "error",
            "message": f"❌ 鉴权失败 (401)：API Key 无效或格式错误。详细信息: {e}"
        }, status_code=401)
    except openai.NotFoundError as e:
        return JSONResponse({
            "status": "error",
            "message": f"❌ 端点/模型未找到 (404)：请检查 Model 名称 '{test_model}' 与 Base URL。详细信息: {e}"
        }, status_code=404)
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"❌ API 连接测试失败: {str(e)}"
        }, status_code=400)

@api_router.post("/config/models")
async def fetch_provider_models(req: TestConfigModel):
    try:
        test_base_url = (req.base_url or config.get("base_url") or "https://api.openai.com/v1").strip()
        test_api_key = (req.api_key or "").strip()
        
        if "****" in test_api_key:
            test_api_key = (config.get("api_key") or "").strip()

        if not test_api_key or test_api_key == "dummy":
            return JSONResponse({
                "status": "error",
                "message": "API Key 为空，请输入 API Key 后再获取模型列表。"
            }, status_code=400)

        test_base_url = test_base_url.rstrip("/") + "/"

        test_client = AsyncOpenAI(
            base_url=test_base_url,
            api_key=test_api_key
        )

        res = await asyncio.wait_for(test_client.models.list(), timeout=10.0)
        models_list = [m.id for m in res.data]
        return JSONResponse({
            "status": "ok",
            "models": models_list,
            "message": f"✅ 成功获取 {len(models_list)} 个可用模型！"
        })
    except Exception as e:
        logger.error(f"Fetch models error: {e}")
        return JSONResponse({
            "status": "error",
            "message": f"无法自动拉取远程模型列表 ({str(e)})"
        }, status_code=400)


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
                SELECT DISTINCT i.id, i.content, i.problem, i.cause, i.solution, i.tags, i.timestamp
                FROM insights i
                JOIN kb_feedback f ON i.id = f.insight_id
                WHERE f.action = 'favorite'
                AND i.id NOT IN (
                    SELECT insight_id FROM kb_feedback WHERE action = 'unfavorite'
                )
                ORDER BY i.timestamp DESC
            """)
            rows = cursor.fetchall()
            items = [{
                "id": row["id"],
                "content": row["content"],
                "problem": row["problem"] if "problem" in row.keys() and row["problem"] else "",
                "cause": row["cause"] if "cause" in row.keys() and row["cause"] else "",
                "solution": row["solution"] if "solution" in row.keys() and row["solution"] else "",
                "tags": row["tags"] if "tags" in row.keys() and row["tags"] else "",
                "timestamp": str(row["timestamp"])
            } for row in rows]
            return JSONResponse({"favorites": items})

        if filter == "all":
            cursor.execute("SELECT id, content, problem, cause, solution, tags, timestamp FROM insights ORDER BY id DESC")
            rows = cursor.fetchall()
            items = [{
                "id": row["id"],
                "content": row["content"],
                "problem": row["problem"] if "problem" in row.keys() and row["problem"] else "",
                "cause": row["cause"] if "cause" in row.keys() and row["cause"] else "",
                "solution": row["solution"] if "solution" in row.keys() and row["solution"] else "",
                "tags": row["tags"] if "tags" in row.keys() and row["tags"] else "",
                "timestamp": str(row["timestamp"])
            } for row in rows]
            return JSONResponse({"rules": items, "items": items, "data": items, "status": "success"})

        cursor.execute("SELECT id, content, problem, cause, solution, tags, timestamp FROM insights ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return JSONResponse({
                "id": row["id"],
                "content": row["content"],
                "problem": row["problem"] if "problem" in row.keys() and row["problem"] else "",
                "cause": row["cause"] if "cause" in row.keys() and row["cause"] else "",
                "solution": row["solution"] if "solution" in row.keys() and row["solution"] else "",
                "tags": row["tags"] if "tags" in row.keys() and row["tags"] else "",
                "timestamp": str(row["timestamp"])
            })
    except Exception as e:
        logger.error(f"KB Get Error: {e}")
    return JSONResponse({"content": "", "favorites": [], "rules": [], "items": []})

@api_router.get("/knowledge")
def get_knowledge(db: sqlite3.Connection = Depends(get_db)):
    return get_kb(filter="all", db=db)

@api_router.post("/kb")
def update_kb(data: KBModel, db: sqlite3.Connection = Depends(get_db)):
    try:
        insight_id = save_insight(data.content, db=db)
        return {"status": "ok", "id": insight_id}
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

class KBSearchModel(BaseModel):
    text: str

def cleanup_stuck_reports(db: sqlite3.Connection):
    max_retention = config.get("stuck_retention_max", 200)
    try:
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM stuck_reports WHERE id NOT IN (SELECT id FROM stuck_reports ORDER BY id DESC LIMIT ?)",
            (max_retention,)
        )
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to cleanup stuck_reports: {e}")

@api_router.get("/stuck")
def get_stuck_reports(limit: int = 50, db: sqlite3.Connection = Depends(get_db)):
    cleanup_stuck_reports(db)
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, agent, context, ts FROM stuck_reports ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        now = time.time()
        reports = []
        for r in rows:
            ts_val = float(r["ts"]) if r["ts"] else now
            ts_human = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts_val))
            age_sec = int(now - ts_val)
            reports.append({
                "id": r["id"],
                "agent": r["agent"],
                "context": r["context"],
                "ts_human": ts_human,
                "age_sec": age_sec
            })
        return JSONResponse({"status": "success", "reports": reports})
    except Exception as e:
        logger.error(f"Get Stuck Reports Error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@api_router.get("/stuck/stats")
def get_stuck_stats(db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        now = time.time()
        ts_24h = now - 86400
        ts_7d = now - 604800

        cursor.execute("SELECT COUNT(*) as cnt FROM stuck_reports WHERE ts > ?", (ts_24h,))
        row_24h = cursor.fetchone()
        count_24h = row_24h["cnt"] if row_24h and "cnt" in row_24h.keys() else (row_24h[0] if row_24h else 0)

        cursor.execute("SELECT COUNT(*) as cnt FROM stuck_reports WHERE ts > ?", (ts_7d,))
        row_7d = cursor.fetchone()
        count_7d = row_7d["cnt"] if row_7d and "cnt" in row_7d.keys() else (row_7d[0] if row_7d else 0)

        cursor.execute("SELECT agent, COUNT(*) as cnt FROM stuck_reports GROUP BY agent ORDER BY cnt DESC")
        rows_agent = cursor.fetchall()
        by_agent = {r["agent"]: r["cnt"] for r in rows_agent}

        return JSONResponse({
            "status": "success",
            "by_agent": by_agent,
            "total_24h": count_24h,
            "total_7d": count_7d
        })
    except Exception as e:
        logger.error(f"Get Stuck Stats Error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@api_router.post("/kb/search")
def search_kb_endpoint(data: KBSearchModel, db: sqlite3.Connection = Depends(get_db)):
    try:
        hits = search_kb(data.text, limit=5)
        return JSONResponse({"status": "success", "hits": [{"id": h[0], "content": h[1]} for h in hits]})
    except Exception as e:
        logger.error(f"Search KB Error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@api_router.get("/stats")
def get_stats(db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, agent_name, path, ts, turns, chars, est_cost, "
                       "input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens "
                       "FROM session_meta ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()

        total_turns = sum(r["turns"] or 0 for r in rows)
        total_chars = sum(r["chars"] or 0 for r in rows)
        total_cost = sum(r["est_cost"] or 0.0 for r in rows)
        total_input = sum(r["input_tokens"] or 0 for r in rows)
        total_output = sum(r["output_tokens"] or 0 for r in rows)
        total_cache_read = sum(r["cache_read_tokens"] or 0 for r in rows)
        total_cache_write = sum(r["cache_creation_tokens"] or 0 for r in rows)
        
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
            total_cost = estimate_cost(total_chars)
            
        return JSONResponse({
            "turns": total_turns,
            "errors": total_errors,
            "tools": total_tools,
            "cost": round(total_cost, 4),
            "input_tokens": total_input,
            "output_tokens": total_output,
            "cache_read_tokens": total_cache_read,
            "cache_creation_tokens": total_cache_write,
            "sessions": [{
                "id": r["id"],
                "agent": r["agent_name"],
                "path": r["path"],
                "ts": str(r["ts"]),
                "turns": r["turns"] or 0,
                "chars": r["chars"] or 0,
                "est_cost": round(r["est_cost"] or 0.0, 4),
                "input_tokens": r["input_tokens"] or 0,
                "output_tokens": r["output_tokens"] or 0,
                "cache_read_tokens": r["cache_read_tokens"] or 0,
                "cache_creation_tokens": r["cache_creation_tokens"] or 0
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
def get_session_transcript(session_id: int, raw: int = 0, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT path, agent_name, ts, turns, chars, est_cost, input_tokens, output_tokens, "
            "cache_read_tokens, cache_creation_tokens FROM session_meta WHERE id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"status": "error", "message": "Session not found"}, status_code=404)
            
        path = row["path"]
        if not os.path.exists(path):
            return JSONResponse({"status": "error", "message": f"Log file at {path} no longer exists"}, status_code=404)
            
        rendered_html, raw_lines, _ = _format_transcript_sync(path, is_initial=True)
        raw_lines_list = list(raw_lines) if raw_lines else []

        if raw == 1:
            last_200_raw = raw_lines_list[-200:]
            touched = extract_touched_files("".join(raw_lines_list)[-2000:])
            row_keys = row.keys() if hasattr(row, "keys") else []
            stats = {
                "turns": row["turns"] if "turns" in row_keys and row["turns"] is not None else 0,
                "chars": row["chars"] if "chars" in row_keys and row["chars"] is not None else 0,
                "est_cost": float(row["est_cost"]) if "est_cost" in row_keys and row["est_cost"] is not None else 0.0,
                "input_tokens": row["input_tokens"] if "input_tokens" in row_keys and row["input_tokens"] is not None else 0,
                "output_tokens": row["output_tokens"] if "output_tokens" in row_keys and row["output_tokens"] is not None else 0,
                "cache_read_tokens": row["cache_read_tokens"] if "cache_read_tokens" in row_keys and row["cache_read_tokens"] is not None else 0,
                "cache_creation_tokens": row["cache_creation_tokens"] if "cache_creation_tokens" in row_keys and row["cache_creation_tokens"] is not None else 0,
            }
            return JSONResponse({
                "status": "success",
                "id": session_id,
                "agent": row["agent_name"],
                "path": path,
                "ts": str(row["ts"]),
                "lines": last_200_raw,
                "touched_files": touched,
                "stats": stats
            })

        return JSONResponse({
            "status": "success",
            "id": session_id,
            "agent": row["agent_name"],
            "path": path,
            "ts": str(row["ts"]),
            "html": rendered_html,
            "total_lines": len(raw_lines_list)
        })
    except Exception as e:
        logger.error(f"Get Session Transcript Error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

class DigestRequestModel(BaseModel):
    session_id: Optional[int] = None
    agent_path: Optional[str] = None
    custom_instruction: Optional[str] = None

@api_router.post("/sessions/digest")
async def generate_session_digest(req: DigestRequestModel, db: sqlite3.Connection = Depends(get_db)):
    """生成会话 Post-Mortem 复盘战报与经验沉淀"""
    target_path = None
    agent_name = "CLI Agent"
    session_row = None
    
    if req.session_id:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM session_meta WHERE id = ?", (req.session_id,))
        session_row = cursor.fetchone()
        if session_row:
            target_path = session_row["path"]
            agent_name = session_row["agent_name"]
    elif req.agent_path and req.agent_path != "auto":
        target_path = req.agent_path
        cursor = db.cursor()
        cursor.execute("SELECT * FROM session_meta WHERE path = ? ORDER BY id DESC LIMIT 1", (target_path,))
        session_row = cursor.fetchone()
        if session_row:
            agent_name = session_row["agent_name"]
    else:
        active = await scan_active_agents()
        if active:
            target_path = active[0]["path"]
            agent_name = active[0]["name"]
            cursor = db.cursor()
            cursor.execute("SELECT * FROM session_meta WHERE path = ? ORDER BY id DESC LIMIT 1", (target_path,))
            session_row = cursor.fetchone()

    if not target_path or not os.path.exists(target_path):
        return JSONResponse({"status": "error", "message": "未找到有效或活跃的会话日志文件。"}, status_code=404)

    try:
        rendered_html, raw_lines, _ = _format_transcript_sync(target_path, is_initial=True)
        raw_lines_list = list(raw_lines) if raw_lines else []
        sample_lines = raw_lines_list[-120:] if len(raw_lines_list) > 120 else raw_lines_list
        transcript_sample = "\n".join(sample_lines)
        
        touched = extract_touched_files(transcript_sample)
        row_keys = session_row.keys() if session_row and hasattr(session_row, "keys") else []
        turns = session_row["turns"] if session_row and "turns" in row_keys and session_row["turns"] else len(sample_lines)
        chars = session_row["chars"] if session_row and "chars" in row_keys and session_row["chars"] else len(transcript_sample)
        est_tokens = chars // 4
        
        prompt = (
            "You are Gabriel Digest Engine (加百列会话复盘引擎). "
            "Analyze the following CLI Agent session transcript slice and metadata to generate a comprehensive, professional, and structured Post-Mortem Report in Markdown.\n\n"
            f"**Agent**: {agent_name}\n"
            f"**Turns**: {turns}\n"
            f"**Touched Files**: {', '.join(touched) if touched else 'None detected'}\n\n"
            "**Transcript Slice**:\n"
            "```\n"
            f"{transcript_sample[:7500]}\n"
            "```\n\n"
            "Please generate a Markdown report with the following structure:\n"
            "# 📊 Agent 会话复盘战报 (Session Digest)\n\n"
            "### 📌 概览看板\n"
            f"- **智能体**: `{agent_name}` | **执行步数**: `{turns}` 步 | **预估 Token**: `~{est_tokens}` | **触及文件**: {len(touched)} 个\n\n"
            "### 🎯 任务目标与执行结果\n"
            "- (简明总结 Agent 在此次会话中尝试完成的核心目标与最终达成状态)\n\n"
            "### 🛠️ 关键执行链路与工具调用\n"
            "- (提炼核心步骤如修改了哪些文件、执行了哪些命令)\n\n"
            "### ⚠️ 遇到的卡点与踩坑分析\n"
            "- (分析过程中出现的错误、异常或工具震荡，及其最终解决方式。若无明显报错则简述平稳执行)\n\n"
            "### 💡 结构化经验沉淀 (可入库)\n"
            "```json\n"
            "{\n"
            '  "problem": "简短问题描述",\n'
            '  "cause": "根本原因",\n'
            '  "solution": "解决方案",\n'
            '  "tags": ["标签1", "标签2"]\n'
            "}\n"
            "```\n"
        )

        client = get_ai_client()
        res = await retry_llm(client.chat.completions.create)(
            model=config.get("model", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a senior AI DevOps engineer and telemetry analyst generating structured Markdown reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        report_md = res.choices[0].message.content
        insight_data = parse_structured_insight(report_md)
        
        return JSONResponse({
            "status": "success",
            "agent": agent_name,
            "path": target_path,
            "turns": turns,
            "touched_files": touched,
            "est_tokens": est_tokens,
            "report": report_md,
            "insight": insight_data
        })
    except Exception as e:
        logger.error(f"Digest generation failed: {e}")
        return JSONResponse({"status": "error", "message": f"复盘报告生成失败: {str(e)}"}, status_code=500)

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

class AiderParser(BaseParser):
    @staticmethod
    def get_scan_patterns() -> list:
        return [
            os.path.join(os.getcwd(), ".aider.chat.history.md"),
            os.path.expanduser(r"~/.aider/logs/*.log"),
            os.path.join(os.getcwd(), ".aider", "logs", "*.log"),
            os.path.join(os.getcwd(), ".aider.input.history")
        ]

    @staticmethod
    def get_agent_name(filepath: str) -> str:
        return f"aider ({os.path.basename(filepath)})"

    @staticmethod
    def identify(filepath: str, line: str) -> bool:
        fp = filepath.lower()
        return "aider" in fp or line.startswith("#### ") or line.startswith("```diff")

    @staticmethod
    def parse(line: str) -> str:
        line = line.strip()
        if not line: return None
        safe_content = html.escape(line)
        
        if line.startswith("#### ") or line.startswith("> "):
            return f'<div class="log-entry"><span class="log-user">👤 [USER]:</span> <span class="log-text">{safe_content[5:200]}</span></div>'
        elif line.startswith("```diff") or line.startswith("```") or line.startswith("diff --git"):
            return f'<div class="log-entry"><span class="log-tool">🛠️ [DIFF/EDIT]:</span><br><span class="log-subtext">{safe_content[:300]}</span></div>'
        elif "Applied edit to" in line or "Commit" in line:
            return f'<div class="log-entry"><span class="log-tool">⚡ [Aider Tool]:</span> <span class="log-text">{safe_content[:200]}</span></div>'
        else:
            return f'<div class="log-entry"><span class="log-agent">⚡ [Aider]:</span> <span class="log-text">{safe_content[:200]}</span></div>'

class OpenHandsParser(BaseParser):
    @staticmethod
    def get_scan_patterns() -> list:
        return [
            os.path.expanduser(r"~/.openhands/logs/*.jsonl"),
            os.path.expanduser(r"~/.openhands/sessions/*/*.jsonl"),
            os.path.join(os.getcwd(), ".openhands", "logs", "*.jsonl")
        ]

    @staticmethod
    def get_agent_name(filepath: str) -> str:
        return f"openhands ({os.path.basename(filepath)})"

    @staticmethod
    def identify(filepath: str, line: str) -> bool:
        return "openhands" in filepath.lower()

    @staticmethod
    def parse(line: str) -> str:
        line = line.strip()
        if not line: return None
        try:
            data = json.loads(line)
            action = data.get("action") or data.get("type", "")
            obs = data.get("observation", "")
            content = data.get("message") or data.get("content") or data.get("args") or ""
            safe_content = html.escape(str(content))
            
            if action in ("run", "browse", "write", "read", "call"):
                return f'<div class="log-entry"><span class="log-tool">🛠️ [OpenHands Action - {action}]:</span><br><span class="log-subtext">{safe_content[:250]}</span></div>'
            elif obs:
                safe_obs = html.escape(str(obs)[:300])
                return f'<div class="log-entry"><span class="log-tool">👁️ [OpenHands Observation]:</span><br><span class="log-subtext">{safe_obs}</span></div>'
            elif data.get("role") == "user":
                return f'<div class="log-entry"><span class="log-user">👤 [USER]:</span> <span class="log-text">{safe_content[:200]}</span></div>'
            else:
                return f'<div class="log-entry"><span class="log-agent">🤖 [OpenHands]:</span> <span class="log-text">{safe_content[:200]}</span></div>'
        except Exception:
            return PlainTextFallbackParser.parse(line)

class GeminiCLIParser(BaseParser):
    @staticmethod
    def get_scan_patterns() -> list:
        return [
            os.path.expanduser(r"~/.gemini/logs/*.jsonl"),
            os.path.expanduser(r"~/.gemini/transcripts/*.jsonl"),
            os.path.join(os.getcwd(), ".gemini", "logs", "*.jsonl")
        ]

    @staticmethod
    def get_agent_name(filepath: str) -> str:
        return f"gemini-cli ({os.path.basename(filepath)})"

    @staticmethod
    def identify(filepath: str, line: str) -> bool:
        fp = filepath.lower()
        return "gemini" in fp and "antigravity" not in fp

    @staticmethod
    def parse(line: str) -> str:
        line = line.strip()
        if not line: return None
        try:
            data = json.loads(line)
            role = data.get("role") or data.get("type") or ""
            content = data.get("content") or data.get("text") or ""
            safe_content = html.escape(str(content))
            
            if role in ("user", "USER_INPUT"):
                return f'<div class="log-entry"><span class="log-user">👤 [USER]:</span> <span class="log-text">{safe_content[:200]}</span></div>'
            elif role in ("tool", "TOOL_RESPONSE"):
                return f'<div class="log-entry"><span class="log-tool">🛠️ [GEMINI TOOL]:</span><br><span class="log-subtext">{safe_content[:250]}</span></div>'
            else:
                return f'<div class="log-entry"><span class="log-agent">✨ [Gemini]:</span> <span class="log-text">{safe_content[:200]}</span></div>'
        except Exception:
            return PlainTextFallbackParser.parse(line)

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
    parsers = [
        AntigravityParser,
        ClaudeCodeParser,
        CursorParser,
        AiderParser,
        OpenHandsParser,
        GeminiCLIParser,
        PlainTextFallbackParser
    ]
    
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
            return "", [], []

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
        return "".join(output), cache['last_200_lines'], new_lines
    except Exception as e:
        return f"Error reading log: {e}", [], []

async def format_transcript(filepath, is_initial=False):
    return await asyncio.to_thread(_format_transcript_sync, filepath, is_initial)

STOP_WORDS = {
    "this", "that", "with", "from", "your", "have", "what", "there", "their",
    "will", "would", "could", "should", "about", "which", "when", "where", "while",
    "these", "those", "using", "system", "message", "content", "response", "planner",
    "怎么办", "如何", "什么", "为什么", "这个", "那个", "一个", "我们", "你们", "他们", "进行", "可以", "需要"
}

def extract_touched_files(text: str) -> list:
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    files = re.findall(r'\b[\w-]+\.(?:py|js|ts|jsx|tsx|css|html|md|json)\b', clean_text, re.IGNORECASE)
    return list(set(files))

def extract_keywords(text: str, max_words=4) -> str:
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    
    # 0. Chinese keywords via jieba.analyse
    zh_words = jieba.analyse.extract_tags(clean_text, topK=max_words)
    
    # 1. Extract file names (e.g., main.py, script.js)
    files = re.findall(r'\b[\w-]+\.(?:py|js|ts|jsx|tsx|css|html|md|json)\b', clean_text, re.IGNORECASE)
    
    # 2. Extract CamelCase, PascalCase, or snake_case identifiers
    identifiers = re.findall(r'\b(?:[a-z]+_[a-z0-9_]+|[A-Z][a-z0-9]+[A-Z][a-z0-9a-zA-Z]*|[a-z]+[A-Z][a-z0-9a-zA-Z]*)\b', clean_text)
    
    # 3. Extract common error keywords
    errors = re.findall(r'\b(?:error|exception|traceback|fail(?:ed|ure)?|fatal|warn(?:ing)?)\b', clean_text, re.IGNORECASE)
    
    # Combine and normalize
    all_terms = [re.sub(r'[^\w\.\_\-]', '', w.lower()) for w in (zh_words + files + identifiers + errors)]
    filtered = [w for w in all_terms if w not in STOP_WORDS and len(w) >= 2]
    
    most_common = [w[0] for w in Counter(filtered).most_common(max_words)]
    
    # Escape quotes and wrap in quotes for robust FTS5 MATCH
    return " OR ".join(f'"{w}"' for w in most_common if w) if most_common else ""

def _is_tool_response(line: str) -> bool:
    """Consecutive tool outputs are the noisiest timeline entries — detect them
    (Antigravity `"type": "TOOL_RESPONSE"` or plain-text `TOOL_RESPONSE` prefix)."""
    return '"TOOL_RESPONSE"' in line or line.startswith("TOOL_RESPONSE")

def _tool_signature(line: str) -> str | None:
    """从 transcript 行提取规范化工具签名：TOOL_CALL/tool_calls/run_command
    取工具名或命令首 token；非工具行返回 None。"""
    if not line or not isinstance(line, str):
        return None

    line_str = line.strip()
    if not line_str:
        return None

    if line_str.startswith("{") and line_str.endswith("}"):
        try:
            data = json.loads(line_str)
            if isinstance(data, dict):
                tool_calls = data.get("tool_calls")
                if isinstance(tool_calls, list) and tool_calls:
                    tc = tool_calls[0]
                    if isinstance(tc, dict):
                        name = tc.get("name") or tc.get("function", {}).get("name") or "unknown"
                        args = tc.get("args") or tc.get("function", {}).get("arguments") or {}
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except Exception:
                                args = {}
                        if name in ("run_command", "Bash", "execute_command") and isinstance(args, dict):
                            cmd = args.get("CommandLine") or args.get("command") or ""
                            if cmd:
                                first_token = cmd.strip().split()[0]
                                return f"{name}:{first_token}"
                        return name

                if data.get("type") in ("tool_use", "tool_call"):
                    name = data.get("name") or "unknown"
                    inp = data.get("input") or {}
                    if isinstance(inp, dict) and name in ("Bash", "run_command", "execute_command"):
                        cmd = inp.get("command") or inp.get("CommandLine") or ""
                        if cmd:
                            first_token = cmd.strip().split()[0]
                            return f"{name}:{first_token}"
                    return name
        except Exception:
            pass

    m_name = re.search(r'"name":\s*"([^"]+)"', line_str)
    if m_name:
        name = m_name.group(1)
        if name in ("run_command", "Bash", "execute_command"):
            m_cmd = re.search(r'"(?:CommandLine|command)":\s*"([^"]+)"', line_str)
            if m_cmd:
                first_token = m_cmd.group(1).strip().split()[0]
                return f"{name}:{first_token}"
        return name

    m_tool = re.search(r'(?:TOOL_CALL|tool_call):\s*([a-zA-Z0-9_\-]+)', line_str, re.IGNORECASE)
    if m_tool:
        return m_tool.group(1)

    return None


def detect_loop(signatures: list, window: int = 8, repeat: int = 5) -> str | None:
    """滑动窗口内同一签名出现 >= repeat 次 → 返回该签名；否则 None。"""
    if not signatures:
        return None
    recent = [s for s in signatures if s is not None][-window:]
    if len(recent) < repeat:
        return None
    counts = Counter(recent)
    for sig, count in counts.items():
        if count >= repeat:
            return sig
    return None

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

    # Fold consecutive (different-content) tool outputs down to the first one —
    # a run of TOOL_RESPONSE events usually just repeats output noise.
    folded = []
    i = 0
    n = len(compressed)
    while i < n:
        line = compressed[i]
        if _is_tool_response(line):
            j = i + 1
            while j < n and _is_tool_response(compressed[j]):
                j += 1
            run = j - i
            folded.append(f"{line} (×{run} tool outputs)" if run > 1 else line)
            i = j
        else:
            folded.append(line)
            i += 1

    return folded[-max_events:]

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
    hits = search_kb(text, limit=5)
    if hits:
        return {"id": hits[0][0], "content": hits[0][1]}
    return None

def estimate_cost(chars: int, config_ref=None) -> float:
    """Coarse per-session cost estimate: chars/4 ≈ tokens, 70/30 input/output split.

    Explicitly an estimate — full token-level billing is a Non-Goal.
    """
    cfg = config_ref if config_ref is not None else config
    # NB: no `or default` fallback here — an explicit 0.0 price (e.g. free output)
    # is a valid value and must not be coerced back to the default.
    price_in = cfg.get("price_input_per_m", 1.0)
    price_out = cfg.get("price_output_per_m", 3.0)
    return (chars / 4) * (0.7 * price_in + 0.3 * price_out) / 1e6

def extract_token_usage(lines: list) -> dict:
    """Extract exact Claude Code token usage from transcript lines.

    Claude Code JSONL entries carry `message.usage`:
      input_tokens / output_tokens / cache_read_input_tokens / cache_creation_input_tokens
    Returns summed totals; all zeros when a transcript has no usage data
    (e.g. Antigravity), which signals the caller to fall back to estimate_cost().
    """
    usage = {"input_tokens": 0, "output_tokens": 0,
             "cache_read_tokens": 0, "cache_creation_tokens": 0}
    for line in lines:
        try:
            data = json.loads(line)
            if not isinstance(data, dict):
                continue
        except Exception:
            continue
        msg = data.get("message") if isinstance(data.get("message"), dict) else None
        u = msg.get("usage") if isinstance(msg, dict) and isinstance(msg.get("usage"), dict) else None
        if not isinstance(u, dict):
            u = data.get("usage") if isinstance(data.get("usage"), dict) else None
        if not isinstance(u, dict):
            continue
        usage["input_tokens"] += u.get("input_tokens") or 0
        usage["output_tokens"] += u.get("output_tokens") or 0
        usage["cache_read_tokens"] += u.get("cache_read_input_tokens") or 0
        usage["cache_creation_tokens"] += u.get("cache_creation_input_tokens") or 0
    return usage

def token_cost(usage: dict, config_ref=None) -> float:
    """Exact cost from token counts ($ per 1M tokens).

    Cache prices default to Anthropic-style ratios of the input price
    (read 0.1x, creation 1.25x) unless explicitly configured.
    """
    cfg = config_ref if config_ref is not None else config
    price_in = cfg.get("price_input_per_m", 1.0)
    price_out = cfg.get("price_output_per_m", 3.0)
    price_cache_read = cfg.get("price_cache_read_per_m", 0.1 * price_in)
    price_cache_write = cfg.get("price_cache_creation_per_m", 1.25 * price_in)
    return (
        usage["input_tokens"] * price_in
        + usage["output_tokens"] * price_out
        + usage["cache_read_tokens"] * price_cache_read
        + usage["cache_creation_tokens"] * price_cache_write
    ) / 1e6

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
    session_token_totals = {}
    tool_signature_deques = {}
    last_loop_warnings = {}
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
                    new_html, last_lines, new_lines = await format_transcript(target_file, is_initial)
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

                        # Exact Claude Code token usage (incremental accumulation over
                        # newly appended lines); falls back to chars-based estimate when
                        # the transcript carries no usage data (e.g. Antigravity).
                        usage_delta = extract_token_usage(new_lines)
                        tok = session_token_totals.setdefault(
                            target_file, {k: 0 for k in usage_delta})
                        for k, v in usage_delta.items():
                            tok[k] += v
                        if sum(tok.values()) > 0:
                            file_cost = token_cost(tok)
                        else:
                            file_cost = estimate_cost(file_chars)

                        def update_session_stats():
                            try:
                                with sqlite3.connect(os.path.join(ROOT_DIR, "knowledge.db")) as conn:
                                    conn.execute(
                                        "UPDATE session_meta SET turns = ?, chars = ?, est_cost = ?, "
                                        "input_tokens = ?, output_tokens = ?, cache_read_tokens = ?, "
                                        "cache_creation_tokens = ? WHERE path = ?",
                                        (file_turns, file_chars, file_cost,
                                         tok["input_tokens"], tok["output_tokens"],
                                         tok["cache_read_tokens"], tok["cache_creation_tokens"],
                                         target_file))
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

                        # Only announce state *flips*; the first observation is the
                        # baseline, not an event (avoids a spurious agent_unblocked).
                        if prev_waiting is not None and is_waiting != prev_waiting:
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
                        threshold = config.get("error_alert_threshold", 5)
                        cooldown = config.get("error_alert_cooldown", 60)
                        if len(err_lines) >= threshold:
                            if time.time() - last_error_warnings.get(target_file, 0) > cooldown:
                                last_error_warnings[target_file] = time.time()
                                await broker.publish(json.dumps({
                                    "type": "error_warning",
                                    "agent": agent_name,
                                    "path": target_file,
                                    "content": "检测到连续异常，可能是卡点，是否需要我诊断？"
                                }))
                        
                        # Loop / tool oscillation detection
                        window = config.get("loop_detection_window", 8)
                        repeat = config.get("loop_detection_repeat", 5)
                        loop_cooldown = config.get("loop_detection_cooldown", 60)

                        if target_file not in tool_signature_deques or tool_signature_deques[target_file].maxlen != window:
                            tool_signature_deques[target_file] = deque(maxlen=window)

                        for line in new_lines:
                            sig = _tool_signature(line)
                            if sig:
                                tool_signature_deques[target_file].append(sig)

                        loop_sig = detect_loop(tool_signature_deques[target_file], window=window, repeat=repeat)
                        if loop_sig:
                            now = time.time()
                            if now - last_loop_warnings.get(target_file, 0) > loop_cooldown:
                                last_loop_warnings[target_file] = now
                                await broker.publish(json.dumps({
                                    "type": "error_warning",
                                    "agent": agent_name,
                                    "path": target_file,
                                    "content": f"疑似死循环：命令「{loop_sig}」在最近 {window} 次工具调用中重复 {repeat} 次，建议打断或调整策略"
                                }))

            frozen = active_tracking - current_active
            for f in frozen:
                await broker.publish(json.dumps({"type": "agent_frozen", "path": f}))
                active_tracking.remove(f)
                if f in current_contexts:
                    del current_contexts[f]
                if f in last_mtimes:
                    del last_mtimes[f]
                if f in session_token_totals:
                    del session_token_totals[f]
                if f in tool_signature_deques:
                    del tool_signature_deques[f]
                if f in last_loop_warnings:
                    del last_loop_warnings[f]
                    
        except Exception:
            logger.error("async_log_tailer 轮询异常: %s", traceback.format_exc())
        await asyncio.sleep(1)

app.include_router(api_router)

@app.get("/api/ping")
@app.get("/ping")
async def ping():
    return JSONResponse({"status": "ok", "ready": True, "token": API_KEY})

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/splash", response_class=HTMLResponse)
async def get_splash():
    splash_path = os.path.join(STATIC_DIR, "splash.html")
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
                    rendered_html, last_lines, _ = _format_transcript_sync(target_path, is_initial=True)
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
                    
                    response = await retry_llm(client.chat.completions.create)(
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
                    err_str = str(e)
                    tip = "请在【设置】中检查 API Key 或 Base URL。"
                    if "401" in err_str or "Authentication" in err_str:
                        tip = "🔑 鉴权失败 (401)：当前服务商的 API Key 无效或过期，请前往【设置】重新填入 Key。"
                    elif "404" in err_str or "Not Found" in err_str:
                        tip = f"🤖 模型未找到 (404)：模型 '{config.get('model')}' 在该 Endpoint 上不可用，建议在【设置】中点击【🔄 自动获取可用模型】。"
                    elif "429" in err_str or "Rate limit" in err_str or "quota" in err_str:
                        tip = "💳 限流或余额不足 (429/402)：服务商账号欠费或请求过于频繁，请检查余额后重试。"
                    elif "Timeout" in err_str or "Connection" in err_str:
                        tip = "🌐 无法连接 API Endpoint (504/Timeout)：网络超时，请检查代理设置或 Base URL。"

                    friendly_error = (
                        f"\n\n<div class='ai-err-card' style='background:var(--canvas-soft); border:1px solid var(--hairline-strong); "
                        f"padding:10px 14px; border-radius:8px; margin-top:8px; font-size:0.85rem; color:var(--ink);'>"
                        f"<strong>⚠️ 无法调通 AI 大模型响应</strong><br>"
                        f"<span style='color:var(--ink-mute);'>{tip}</span><br>"
                        f"<details style='margin-top:6px;'><summary style='cursor:pointer; font-size:0.75rem; color:var(--ink-mute);'>查看原始错误堆栈</summary>"
                        f"<code style='font-size:0.75rem;'>{html.escape(err_str)}</code></details></div>"
                    )
                    try:
                        await wrapper.send_text(json.dumps({
                            "type": "ai_response_chunk",
                            "content": friendly_error
                        }))
                        await wrapper.send_text(json.dumps({
                            "type": "ai_response_end"
                        }))
                        if chat_history and chat_history[-1]["role"] == "user":
                            chat_history.pop()
                    except Exception:
                        pass
                
            elif msg["type"] == "clear_history":
                chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
                
            elif msg["type"] == "merge_kb":
                combined = "\n".join([f"--- Agent: {path} ---\n{ctx}" for path, ctx in current_contexts.items()])
                kb_prompt = (
                    "请将以下开发日志中的核心问题和解决方案提炼为结构化 JSON 对象。\n"
                    "必须输出符合以下 JSON 结构的单一个 JSON 对象：\n"
                    "{\n"
                    '  "problem": "具体问题描述",\n'
                    '  "cause": "根本原因分析",\n'
                    '  "solution": "可复制粘贴的解决方案与修复代码",\n'
                    '  "tags": ["标签1", "标签2", "标签3"]\n'
                    "}\n\n"
                    f"日志上下文:\n```\n{combined}\n```"
                )
                try:
                    client = get_ai_client()
                    response = await retry_llm(client.chat.completions.create)(
                        model=config["model"],
                        messages=[{"role": "user", "content": kb_prompt}]
                    )
                    
                    raw_content = response.choices[0].message.content
                    parsed = parse_structured_insight(raw_content)
                    prob = parsed.get("problem", "")
                    cause = parsed.get("cause", "")
                    sol = parsed.get("solution", "")
                    tags_raw = parsed.get("tags", [])
                    tags_str = json.dumps(tags_raw, ensure_ascii=False) if isinstance(tags_raw, list) else str(tags_raw)

                    if prob and sol:
                        insight_content = f"# 问题: {prob}\n\n## 原因\n{cause}\n\n## 解决方案\n{sol}"
                        if tags_raw:
                            insight_content += f"\n\n**标签**: {', '.join(tags_raw) if isinstance(tags_raw, list) else tags_str}"
                    else:
                        insight_content = raw_content

                    save_insight(insight_content, problem=prob, cause=cause, solution=sol, tags=tags_raw)
                        
                    await wrapper.send_text(json.dumps({
                        "type": "kb_toast",
                        "content": insight_content
                    }))
                    
                    await wrapper.send_text(json.dumps({
                        "type": "sys_message",
                        "content": "✅ 已生成结构化知识库并存入大脑（FTS5索引完成）！"
                    }))
                except Exception as e:
                    await wrapper.send_text(json.dumps({
                        "type": "sys_message",
                        "content": f"❌ 提炼失败: {str(e)}"
                    }))
            elif msg["type"] == "inject_insight":
                insight_content = msg.get("content", "")
                save_insight(insight_content)
                await wrapper.send_text(json.dumps({
                    "type": "sys_message",
                    "content": "✅ 已注入结构化知识库草稿！(Injected into KB)"
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
            
def _find_free_port(start: int = 8080, attempts: int = 20) -> int:
    """端口自动避让：从 start 起探测可用端口（bind 探测后立即释放）。"""
    import socket as _socket
    for port in range(start, start + attempts):
        with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise SystemExit(f"Error: ports {start}-{start + attempts - 1} are all in use. "
                     "Close other applications or pass --port manually.")


def _single_instance_guard(port: int) -> bool:
    """frozen 模式单实例锁：已有实例存活则打开其页面并返回 False（本进程退出）。

    锁文件记录端口；启动时若该端口仍可连接，视为已有实例在跑（不做 PID 误杀），
    否则接管（stale 锁自然失效）。源码模式不启用，方便开发多开。
    """
    if not getattr(sys, "frozen", False):
        return True
    lock = os.path.join(ROOT_DIR, ".gabriel.lock")
    if os.path.exists(lock):
        try:
            with open(lock, "r", encoding="utf-8") as f:
                old_port = int(f.read().strip())
            import socket as _socket
            with _socket.create_connection(("127.0.0.1", old_port), timeout=0.5):
                # webbrowser.open 可能在非交互会话挂起——放守护线程，主进程立即退出
                import threading
                import webbrowser
                threading.Thread(
                    target=webbrowser.open,
                    args=(f"http://127.0.0.1:{old_port}/",),
                    daemon=True,
                ).start()
                return False
        except (OSError, ValueError):
            pass  # 旧实例已死或锁损坏 → 接管
    try:
        with open(lock, "w", encoding="utf-8") as f:
            f.write(str(port))
    except OSError:
        pass  # 数据目录不可写时锁失败不阻塞启动
    return True


def _open_browser_when_ready(url: str, timeout: float = 8.0):
    """后台轮询就绪（GET / 返回 2xx）后打开默认浏览器，避免 CONNECTION_REFUSED。"""
    import threading
    import urllib.request
    import webbrowser

    def _wait_and_open():
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=0.5) as r:
                    if r.status < 400:
                        webbrowser.open(url)
                        return
            except Exception:
                pass
            time.sleep(0.25)

    threading.Thread(target=_wait_and_open, daemon=True).start()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gabriel Control Center")
    parser.add_argument("--port", type=int, default=8080, help="preferred port (auto-advances if busy)")
    parser.add_argument("--no-browser", action="store_true", help="do not auto-open the browser")
    args = parser.parse_args()

    port = _find_free_port(args.port)
    if not _single_instance_guard(port):
        return  # 已有实例在运行，本进程退出

    print(f"Gabriel is running at http://127.0.0.1:{port}")
    if not args.no_browser:
        _open_browser_when_ready(f"http://127.0.0.1:{port}/?token={API_KEY}")

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="critical")


if __name__ == "__main__":
    main()



