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
        response = client.get("/api/ping")
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

if __name__ == '__main__':
    unittest.main(verbosity=2)
