# Gabriel — Project Map for AI Assistants

> 🚀 **新会话启动强制指令 (Session Startup Mandate)**:  
> 每次开启全新对话或新任务时，AI 助理必须**首先阅读并遵循 `MEMORY.md`、`GEMINI.md` 与本文件**，无缝继承用户的桌面工作流习惯与核心心智模型。在任何文件清理或重构中，**绝对禁止删除或清空 `MEMORY.md`、`GEMINI.md`、`CLAUDE.md`**！

Gabriel（加百列）是 CLI 型 AI Agent（Claude Code / Gemini CLI / Cursor / Antigravity / Aider / OpenHands）的**零侵入 GUI 副屏**：旁路 tail 它们的 transcript 日志，提供实时仪表盘、副脑问答、私有知识库（FTS5 + 向量 RRF）、会话统计与 MCP 生态接口。**不 hook 主 Agent 的终端**（纯只读 tail）。

## Run

```bash
python -m venv venv && venv\Scripts\activate   # 一次性
pip install -r requirements.txt                 # 一次性（必须先于 -e .）
cp .env.example .env                            # 可选；GABRIEL_TOKEN 留空则每次随机
python -m src.main --port 8080                  # 或 pip install -e . 后用 gabriel
# 打开 http://127.0.0.1:8080，粘贴终端打印的 Token
```

- 桌面模式：`python src/run.py`（pywebview 窗口）
- MCP 服务：`python -m src.mcp_server`（stdio）或 `--http`

## Verify (must be green after any change)

```bash
venv\Scripts\python.exe -m pytest tests/ -q      # 39 tests passed
venv\Scripts\python.exe -m ruff check src tests
node --check static/script.js static/icons.js
```

## Architecture

| Path | Role |
|---|---|
| `src/main.py` | FastAPI 后端：REST + WebSocket + 日志 tailer + FTS5/向量 KB + 卡点雷达。`@api_router` 路由区在 :577 起；`save_insight()` 是 KB 写入唯一入口；`search_kb()` 是检索唯一入口；`check_active_kb()` 是主动推荐（内部检索） |
| `src/mcp_server.py` | stdio MCP：`read_gabriel_kb` / `add_gabriel_insight` / `report_agent_stuck` / `get_session_summary` |
| `src/run.py` | pywebview 桌面壳（不动业务） |
| `static/index.html` · `style.css` | 前端（Vanilla JS，零框架零 CDN）。**视觉规范见 `DESIGN.md`**（v4 Light Indigo：白底 `#ffffff` / 藏青 `#0d253d` / 靛紫 `#533afd` 唯一 CTA） |
| `static/script.js` | 前端逻辑（WS 客户端、i18n、渲染） |
| `static/icons.js` | Lucide 图标模块（`ICONS.search` 等，stroke 1.5，`currentColor`）；源文件在 `static/vendor/lucide/` |
| `static/vendor/` | 本地 vendor：字体（Inter/JetBrains Mono woff2）、marked、DOMPurify、highlight.js、lucide |
| `knowledge.db` | SQLite：`insights` / `insights_fts`(jieba 分词) / `insights_vec`(sqlite-vec) / `kb_feedback` / `session_meta` / `chat_history` / `stuck_reports` / `kb_meta` |

## Conventions & guardrails (non-negotiable)

1. **零 CDN**：新前端资源必须 vendor 进 `static/vendor/`（字体 woff2 + 许可证；图标取 lucide 仓库 SVG）。
2. **颜色唯一来源**：裸 hex 只允许出现在 `style.css` 的 `:root` 与 `.log-*` 映射区；HTML/JS 用 `var(--token)`。
3. **鉴权**：所有 `/api/*` 必须走 `verify_token`；WS 用 ticket 优先、`?token=` fallback。
4. **XSS**：动态 `innerHTML` 一律过 DOMPurify；后端输出语义 class（`.log-*`），颜色只在 CSS。
5. **KB 写入/检索单一来源**：写入只走 `save_insight()`，检索只走 `search_kb()`；禁止复制第四份 SQL。
6. **新表必须进 `init_schema`**，禁止业务代码裸建表。
7. **数据库 schema 迁移**：用 `kb_meta.schema_version` 递增 + 迁移分支，勿重建表。
8. **前端收编纪律**：新 UI class 化（不写内联 style）；emoji 不充当功能图标（用 `ICONS`）；改 `style.css`/`script.js` 后把 `index.html` 里对应引用 bump `?v=`。
9. **离线降级**：sqlite-vec / fastembed / 模型不可用 → 静默回退纯 FTS5，禁止阻塞主流程。
10. **测试护栏**：`search_kb` 无反馈时结果序必须与纯 RRF 一致（回归护栏）；`check_active_kb` 返回形状 `{"id","content"}` 不许改。
11. **开源对比全局指令**：全局约束——在后续所有功能迭代与 UI/UX 优化中，必须持续联网参考开源优质项目（Cherry Studio, LobeChat, NextChat, One-API）的设计规范与技术最佳实践。

## Common tasks

- **加一个 API 端点**：`src/main.py` 加 `@api_router.get(...)` + `verify_token` 依赖 + 单测（`tests/test_gabriel.py` 用 `TestClient` + 临时 `ROOT_DIR` 库）。
- **改样式**：只动 `static/style.css` token/class 层；改完 bump `index.html` 的 `style.css?v=`；用 Edge headless 截图对比（`docs/screenshots_v4/` 有范例流程）。
- **加图标**：从 `https://github.com/lucide-icons/lucide/tree/main/icons` 下载 SVG 进 `static/vendor/lucide/`，跑生成脚本更新 `static/icons.js`（`<svg>` 内部提取为 `ICONS.<name>`）。
- **排查"Error fetching agents."**：先 `curl -H "X-Gabriel-Token: $GABRIEL_TOKEN" http://127.0.0.1:8080/api/agents` —— 401 是 token 不匹配（前端现在会弹登录框），500 才是后端 bug。
- **日志/数据库**：服务日志在 `logs/`；`knowledge.db` 可用 `sqlite3` 直查。

## Docs index

`docs/DEVELOPMENT_ROADMAP.md`（开发全景图与路线图）· `docs/ARCHITECTURE.md`（架构设计）· `docs/API_REFERENCE.md`（端点全表）· `DESIGN.md`（视觉规范）· `docs/AUTOSTART.md`（Windows 自启）· `docs/RELEASE.md`（打包发布）。
