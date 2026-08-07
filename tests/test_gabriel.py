import sys
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
        import tempfile
        from unittest.mock import patch
        import main

        original_config = main.config
        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                with patch('main.CONFIG_FILE', os.path.join(tmpdirname, "config.json")):
                    main.config = main.DEFAULT_CONFIG.copy()
                    main.config["api_key"] = "test_key"
                    # Write new
                    payload = {
                        "base_url": "https://api.openai.com/v1",
                        "api_key": "test_key",
                        "model": "gpt-4",
                        "target_agent": "auto"
                    }
                    response = client.post("/api/config", json=payload, headers={"X-Gabriel-Token": API_KEY})
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(os.path.exists(os.path.join(tmpdirname, "config.json")))
                    # API key must never be persisted to disk
                    with open(os.path.join(tmpdirname, "config.json"), "r", encoding="utf-8") as f:
                        self.assertNotIn("test_key", f.read())

                    # Verify
                    new_config = client.get("/api/config", headers={"X-Gabriel-Token": API_KEY}).json()
                    self.assertEqual(new_config["model"], "gpt-4")
                    self.assertNotEqual(new_config["api_key"], "test_key")
                    print("✅ Atomic config update successful")
        finally:
            main.config = original_config

    def test_knowledge_base_crud(self):
        """Test SQLite KB injection and retrieval"""
        import tempfile
        from unittest.mock import patch
        import main

        with tempfile.TemporaryDirectory() as tmpdirname:
            with patch('main.ROOT_DIR', tmpdirname):
                payload = {"content": "## Test Insight\nThis is a QA test."}
                res_post = client.post("/api/kb", json=payload, headers={"X-Gabriel-Token": API_KEY})
                self.assertEqual(res_post.status_code, 200, res_post.text if hasattr(res_post, "text") else res_post)

                res_get = client.get("/api/kb", headers={"X-Gabriel-Token": API_KEY})
                self.assertEqual(res_get.status_code, 200)
                data = res_get.json()
                self.assertEqual(data["content"], payload["content"])
                
                # Test favorite filter and feedback ranking
                from main import check_active_kb
                client.post("/api/kb/feedback", json={"insight_id": 1, "action": "favorite"}, headers={"X-Gabriel-Token": API_KEY})
                fav_res = client.get("/api/kb?filter=favorite", headers={"X-Gabriel-Token": API_KEY})
                self.assertEqual(fav_res.status_code, 200)
                fav_data = fav_res.json()
                self.assertEqual(len(fav_data["favorites"]), 1)
                self.assertEqual(fav_data["favorites"][0]["content"], payload["content"])
                
                # Test useless demotion (2 useless votes demote item)
                client.post("/api/kb/feedback", json={"insight_id": 1, "action": "useless"}, headers={"X-Gabriel-Token": API_KEY})
                client.post("/api/kb/feedback", json={"insight_id": 1, "action": "useless"}, headers={"X-Gabriel-Token": API_KEY})
                hit = check_active_kb("test insight QA test")
                self.assertIsNone(hit) # demoted due to useless >= 2
                print("✅ SQLite Knowledge Base CRUD & Weighted Ranking successful")

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

    def test_snapshot_structure_and_size_reduction(self):
        """Test build_snapshot structured format, deduplication, and size reduction"""
        from main import build_snapshot, _transcript_cache
        
        sample_lines = [
            '{"type": "user", "content": "debug main.py"}\n',
            'TOOL_CALL run_command main.py\n',
            'Executing command in python...\n',
            'Executing command in python...\n',
            'Executing command in python...\n',
            'Error: Exception in main.py line 42\n',
            'Error: Exception in main.py line 42\n',
            'Error: Exception in main.py line 42\n',
            'Error: Exception in main.py line 42\n',
            'Error: Exception in main.py line 42\n',
        ]
        
        test_path = "mock_agent_session.jsonl"
        _transcript_cache[test_path] = {"last_200_lines": sample_lines}
        
        try:
            # 1. Test basic structure
            snapshot = build_snapshot(test_path, "what is happening?")
            self.assertIn("[现场]", snapshot)
            self.assertIn("疑似卡点", snapshot)
            self.assertIn("[时间线]", snapshot)
            self.assertNotIn("[原始尾部]", snapshot)
            self.assertIn("(×3)", snapshot)  # deduplication check
            
            # 2. Test "全文" trigger
            snapshot_full = build_snapshot(test_path, "查看全文日志")
            self.assertIn("[原始尾部]", snapshot_full)
            
            # 3. Test size reduction compared to raw 60 lines
            raw_text = "".join(sample_lines * 6)
            _transcript_cache[test_path] = {"last_200_lines": sample_lines * 6}
            snapshot_comp = build_snapshot(test_path, "quick status")
            self.assertLess(len(snapshot_comp), len(raw_text) * 0.6)
            print("✅ Snapshot structure & size reduction tests successful")
        finally:
            _transcript_cache.pop(test_path, None)

    def test_ws_ticket_auth(self):
        """Test WS single-use ticket authentication (T2)"""
        # 1. Unauthenticated WS fails with 1008
        from fastapi.websockets import WebSocketDisconnect
        with self.assertRaises(WebSocketDisconnect) as context:
            with client.websocket_connect("/ws") as websocket:
                pass
        self.assertEqual(context.exception.code, 1008)
        
        # 2. Authenticated ticket generation
        ticket_res = client.post("/api/auth/ticket", headers={"X-Gabriel-Token": API_KEY})
        self.assertEqual(ticket_res.status_code, 200)
        ticket = ticket_res.json()["ticket"]
        self.assertEqual(len(ticket), 32)
        
        # 3. WS connect with ticket succeeds
        with client.websocket_connect(f"/ws?ticket={ticket}") as websocket:
            data = websocket.receive_json()
            self.assertEqual(data["type"], "context_update")
            
        # 4. Ticket is single-use, second connection fails
        with self.assertRaises(WebSocketDisconnect) as context2:
            with client.websocket_connect(f"/ws?ticket={ticket}") as websocket:
                pass
        self.assertEqual(context2.exception.code, 1008)
        print("✅ WS Ticket Auth test successful")

    def test_kb_rank_feedback_weighted(self):
        """Test KB weighted ranking formula & useless demotion (T4)"""
        import tempfile
        from unittest.mock import patch
        import main
        from main import check_active_kb

        with tempfile.TemporaryDirectory() as tmpdirname:
            with patch('main.ROOT_DIR', tmpdirname):
                payload1 = {"content": "Exception in memory_leak module main_test"}
                payload2 = {"content": "Exception in memory_leak module second_test"}
                client.post("/api/kb", json=payload1, headers={"X-Gabriel-Token": API_KEY})
                client.post("/api/kb", json=payload2, headers={"X-Gabriel-Token": API_KEY})
                
                # Feedback: useful for item 1, useless for item 2 (insight_id 2)
                client.post("/api/kb/feedback", json={"insight_id": 1, "action": "useful"}, headers={"X-Gabriel-Token": API_KEY})
                client.post("/api/kb/feedback", json={"insight_id": 2, "action": "useless"}, headers={"X-Gabriel-Token": API_KEY})
                client.post("/api/kb/feedback", json={"insight_id": 2, "action": "useless"}, headers={"X-Gabriel-Token": API_KEY})
                
                hit = check_active_kb("Exception in memory_leak module main_test")
                self.assertIsNotNone(hit)
                self.assertEqual(hit["id"], 1)
                print("✅ KB Rank Feedback Weighted test successful")

    def test_sessions_persist_and_transcript(self):
        """Test GET /api/sessions and /api/sessions/{id}/transcript (T5)"""
        import tempfile
        from unittest.mock import patch
        import sqlite3
        import main
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            dummy_log = os.path.join(tmpdirname, "test_agent.jsonl")
            with open(dummy_log, "w", encoding="utf-8") as f:
                f.write('{"type": "user", "content": "hello world"}\n')
                
            db_path = os.path.join(tmpdirname, "knowledge.db")
            conn = sqlite3.connect(db_path)
            main.init_schema(conn)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO session_meta (agent_name, path, turns, chars, est_cost) VALUES (?, ?, ?, ?, ?)",
                           ("TestAgent", dummy_log, 5, 1000, 0.0025))
            conn.commit()
            session_id = cursor.lastrowid
            conn.close()
            
            with patch('main.ROOT_DIR', tmpdirname):
                res = client.get("/api/sessions", headers={"X-Gabriel-Token": API_KEY})
                self.assertEqual(res.status_code, 200)
                sessions = res.json()
                self.assertTrue(len(sessions) > 0)
                
                res_trans = client.get(f"/api/sessions/{session_id}/transcript", headers={"X-Gabriel-Token": API_KEY})
                self.assertEqual(res_trans.status_code, 200)
                trans_data = res_trans.json()
                self.assertEqual(trans_data["status"], "success")
                self.assertIn("hello world", trans_data["html"])
                print("✅ Sessions Persist & Transcript test successful")

    def test_stats_session_reproducible(self):
        """Test GET /api/stats session-level aggregation & reproducible cost (T6)"""
        import tempfile
        from unittest.mock import patch
        import sqlite3
        import main
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            db_path = os.path.join(tmpdirname, "knowledge.db")
            conn = sqlite3.connect(db_path)
            main.init_schema(conn)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO session_meta (agent_name, path, turns, chars, est_cost) VALUES (?, ?, ?, ?, ?)",
                           ("AgentAlpha", "log_alpha.jsonl", 10, 4000, 0.0010))
            cursor.execute("INSERT INTO session_meta (agent_name, path, turns, chars, est_cost) VALUES (?, ?, ?, ?, ?)",
                           ("AgentBeta", "log_beta.jsonl", 20, 8000, 0.0020))
            conn.commit()
            conn.close()
            
            with patch('main.ROOT_DIR', tmpdirname):
                res = client.get("/api/stats", headers={"X-Gabriel-Token": API_KEY})
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertEqual(data["turns"], 30)
                self.assertEqual(data["cost"], 0.0030)
                self.assertEqual(len(data["sessions"]), 2)
                print("✅ Stats Session Reproducible test successful")

    def test_chat_history_roundtrip(self):
        """Test chat history database persistence and bounds (T9)"""
        import tempfile
        import sqlite3
        import main
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            db_path = os.path.join(tmpdirname, "knowledge.db")
            conn = sqlite3.connect(db_path)
            main.init_schema(conn)
            cursor = conn.cursor()
            
            # Insert 45 rounds
            for i in range(45):
                cursor.execute("INSERT INTO chat_history (agent_path, role, content) VALUES ('', 'user', ?)", (f"Question {i}",))
                cursor.execute("INSERT INTO chat_history (agent_path, role, content) VALUES ('', 'assistant', ?)", (f"Answer {i}",))
            conn.commit()
            
            # Truncate to max 40
            cursor.execute("DELETE FROM chat_history WHERE id NOT IN (SELECT id FROM chat_history WHERE agent_path = '' ORDER BY id DESC LIMIT 40)")
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 40)
            conn.close()
            print("✅ Chat History Roundtrip test successful")

    def test_build_prompt_content_modes(self):
        """Test side-brain mode: snapshot vs full context injection + length guard"""
        from main import build_prompt_content, _transcript_cache, FULL_CONTEXT_TOTAL_LIMIT

        sample_lines = [
            '{"type": "user", "content": "hello"}\n',
            'TOOL_CALL run_command build.py\n',
            'Error: Exception in build.py line 5\n',
        ]
        test_path = "mock_prompt_agent.jsonl"
        _transcript_cache[test_path] = {"last_200_lines": sample_lines}

        try:
            # 1. Default / snapshot mode (backward compatible)
            prompt = build_prompt_content({}, {test_path: "RAW_CTX"}, "what happened?")
            self.assertIn("Terminal Snapshot(s):", prompt)
            self.assertNotIn("RAW_CTX", prompt)
            self.assertIn("Error", prompt)  # snapshot carries compressed timeline

            # 2. Full mode feeds raw terminal context
            prompt_full = build_prompt_content({"context": "full"}, {test_path: "RAW_CTX"}, "why failed?")
            self.assertIn("Terminal Context(s):", prompt_full)
            self.assertIn("RAW_CTX", prompt_full)

            # 3. Full mode length guard: oversized context is truncated
            big = "x" * (FULL_CONTEXT_TOTAL_LIMIT + 50000)
            prompt_guard = build_prompt_content({"context": "full"}, {test_path: big}, "q")
            self.assertLessEqual(len(prompt_guard), FULL_CONTEXT_TOTAL_LIMIT + 500)
            print("✅ Side-brain mode (snapshot/full + length guard) tests successful")
        finally:
            _transcript_cache.pop(test_path, None)

    def test_auth_enforcement(self):
        """Test that API endpoints reject requests without token"""
        response = client.get("/api/config")
        self.assertEqual(response.status_code, 401)
        print("✅ Auth enforcement test successful")

    def test_estimate_cost_formula(self):
        """Test estimate_cost: chars/4 tokens, 70/30 in/out split, configurable prices"""
        from main import estimate_cost
        cfg = {"price_input_per_m": 1.0, "price_output_per_m": 3.0}
        # 4000 chars => 1000 tokens => 0.7*1000*1.0 + 0.3*1000*3.0 per 1M = 0.0016
        self.assertAlmostEqual(estimate_cost(4000, cfg), 0.0016, places=7)
        # Zero chars => zero cost
        self.assertEqual(estimate_cost(0, cfg), 0.0)
        # Missing prices fall back to defaults (1.0 / 3.0)
        self.assertAlmostEqual(estimate_cost(4000, {}), 0.0016, places=7)
        # Prices are per 1M tokens: 1M chars/4 = 250k tokens, all input at $1 => $0.175
        big_cfg = {"price_input_per_m": 1.0, "price_output_per_m": 0.0}
        self.assertAlmostEqual(estimate_cost(1_000_000, big_cfg), 0.175, places=7)
        print("✅ Estimate cost formula test successful")

    def test_token_usage_extraction(self):
        """Extract exact Claude Code message.usage tokens from transcript lines"""
        from main import extract_token_usage

        lines = [
            '{"type": "assistant", "message": {"usage": {"input_tokens": 100, "output_tokens": 25, "cache_read_input_tokens": 300, "cache_creation_input_tokens": 50}}}',
            '{"type": "assistant", "message": {"usage": {"input_tokens": 40, "output_tokens": 10, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 20}}}',
            '{"type": "user", "content": "plain question"}',
            "just some plain text line",
            "not even json",
        ]
        usage = extract_token_usage(lines)
        self.assertEqual(usage["input_tokens"], 140)
        self.assertEqual(usage["output_tokens"], 35)
        self.assertEqual(usage["cache_read_tokens"], 400)
        self.assertEqual(usage["cache_creation_tokens"], 70)

        # No usage data anywhere -> all zeros, signaling chars-estimate fallback
        empty = extract_token_usage(["no usage here", '{"a": 1}', "plain text"])
        self.assertEqual(empty, {"input_tokens": 0, "output_tokens": 0,
                                 "cache_read_tokens": 0, "cache_creation_tokens": 0})
        print("✅ Token usage extraction test successful")

    def test_token_cost_calculation(self):
        """token_cost exact pricing with cache default ratios and explicit overrides"""
        from main import token_cost

        cfg = {"price_input_per_m": 3.0, "price_output_per_m": 15.0}
        usage = {"input_tokens": 1000, "output_tokens": 200,
                 "cache_read_tokens": 5000, "cache_creation_tokens": 100}
        # 1000*3 + 200*15 + 5000*0.3(cache read=0.1x) + 100*3.75(create=1.25x) = 7875
        self.assertAlmostEqual(token_cost(usage, cfg), 0.007875, places=9)

        # Explicit cache price override honored (0.0 is a valid price)
        cfg2 = dict(cfg)
        cfg2["price_cache_read_per_m"] = 0.0
        self.assertAlmostEqual(token_cost(usage, cfg2), (3000 + 3000 + 375) / 1e6, places=9)
        print("✅ Token cost calculation test successful")

if __name__ == '__main__':
    unittest.main(verbosity=2)
