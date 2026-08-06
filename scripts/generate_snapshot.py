import os

files_to_dump = [
    'src/main.py',
    'static/script.js',
    'static/index.html',
    'tests/test_gabriel.py'
]

test_output = """C:\\Users\\Jason\\Desktop\\Gabriel\\venv\\Lib\\site-packages\\fastapi\\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
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
"""

known_issues = """
### 已知问题 / 未处理事项

1. **多用户并发连接状态同步问题**: 当前的 Token 免重复输入使用的是 `localStorage`。由于 Gabriel 的定位是单机运行，暂时没有问题。但如果未来暴露在局域网下多用户并发访问（例如团队共享），基于 WebSocket 的状态同步机制可能会将一个用户的切换操作广播给所有连接的客户端，这会导致"幽灵切换"。
2. **`script.js` 现存语法残留**: 在修复合并时发现 `script.js` 约 673 行 `document.getElementById('btnMerge').addEventListener` 内部有未闭合或结构混乱的残留代码（`initTabs(); initChart();`）。虽然 JavaScript 能够勉强运行或部分失败，但这是前几次重构留下的隐患，由于本次主要集中在稳定性、健康检查与 Token 本地化，没有贸然深入重构前端事件绑定。
3. **日志轮转（Log Rotation）的并发写入风险**: 使用了 `RotatingFileHandler` 解决了无限增长问题。但在高并发多进程测试（类似之前被清理掉的 benchmark 脚本模拟的环境）下，默认的 RotatingFileHandler 在 Windows 下可能会因为文件占用导致轮转失败（PermissionError）。如果要求极其严苛的稳定性，后续应引入 `ConcurrentRotatingFileHandler`。
4. **WebSocket 心跳机制缺失**: 虽然增加了 `/api/health` 轮询检查后端 tailer 的存活，但 WebSocket 层面仍然缺乏标准的 Ping/Pong 心跳，如果底层连接默默断开（Half-open connection），只能依赖浏览器的超时机制，偶尔会出现状态断联没有及时显示的问题。
"""

with open('docs/Code_Review_Snapshot.md', 'w', encoding='utf-8') as out:
    out.write('# Code Review Snapshot\\n\\n')
    
    for fpath in files_to_dump:
        out.write(f'## File: `{fpath}`\\n\\n')
        
        ext = os.path.splitext(fpath)[1][1:]
        if ext == 'js': ext = 'javascript'
        if ext == 'py': ext = 'python'
        
        out.write(f'```{ext}\\n')
        with open(fpath, 'r', encoding='utf-8') as f:
            out.write(f.read())
        out.write('\\n```\\n\\n')
        
    out.write('## Unit Test Results\\n\\n')
    out.write('```\\n')
    out.write(test_output)
    out.write('\\n```\\n\\n')
    
    out.write('## Known Issues / Unresolved Items\\n\\n')
    out.write(known_issues)
    
print('Snapshot generated successfully.')
