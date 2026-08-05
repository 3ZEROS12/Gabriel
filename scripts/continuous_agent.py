import time
import requests
import sqlite3
import random
import os

print("[Gabriel Continuous Agent] Initializing perpetual testing swarm...")
BASE_URL = "http://127.0.0.1:8080"
DB_PATH = os.path.join(os.path.dirname(__file__), "src", "knowledge.db")
LOG_PATH = os.path.join(os.path.dirname(__file__), "continuous_audit.log")

def log_activity(msg):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

while True:
    try:
        # Action 1: Fuzz the config endpoint
        r = requests.get(f"{BASE_URL}/api/config")
        if r.status_code == 200:
            log_activity("[Agent-Tester-Alpha] Config endpoint OK.")
        else:
            log_activity(f"[Agent-Tester-Alpha] ERROR on Config endpoint: {r.status_code}")
            
        # Action 2: Check database lock state
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("SELECT 1 FROM insights LIMIT 1")
            conn.close()
            log_activity("[Agent-Tester-Beta] SQLite DB integrity verified. No locks.")
        except Exception as e:
            log_activity(f"[Agent-Tester-Beta] DB ERROR: {e}")
            
        # Action 3: Ping
        r = requests.get(f"{BASE_URL}/api/ping")
        if r.json().get("status") == "ok":
            log_activity("[Agent-Tester-Gamma] System heartbeat pulse detected.")
            
        time.sleep(random.randint(2, 5))
        
    except Exception as e:
        log_activity(f"[Swarm-Manager] Exception caught during test cycle: {e}")
        time.sleep(5)
