# Gabriel API Reference

> 2026-08-08 核对（v4.0.0 Light Indigo）。所有 `/api/*` 端点要求 `X-Gabriel-Token` 请求头（与启动时打印/`.env` 配置的 token 一致，常数时间比较）。WebSocket 用一次性 ticket 或 `?token=` 参数。

## REST 端点总表

| Method | Path | 说明 |
|---|---|---|
| GET | `/api/ping` | 存活检查（返回 `{"status":"ok","ts":...}`） |
| GET | `/api/health` | Tailer 心跳：`healthy` / `stale`(>30s) / `starting`(503)；stale 返回 503 |
| POST | `/api/auth/ticket` | 一次性 WS 鉴权票据（5 分钟有效，用后即焚） |
| GET | `/api/config` | 读取运行配置（base_url / model / prices / target_agent） |
| POST | `/api/config` | 原子更新配置（写 config.json） |
| GET | `/api/agents` | 活跃 Agent 会话列表：`[{name, path, mtime, steps}]` |
| GET | `/api/knowledge` | 知识库列表（别名，与 `/api/kb` 兼容） |
| GET | `/api/kb?filter=all\|favorite` | KB 列表：all=全部倒序；favorite=收藏（unfavorite 已剔除）；默认返回最新 1 条 |
| POST | `/api/kb` | 写入 insight（body `{"content": str}` → 走 `save_insight()`，FTS 分词 + 向量 + 结构化四段解析） |
| POST | `/api/kb/feedback` | 反馈：`{"insight_id", "action": useful\|useless\|favorite\|unfavorite}`（进 `kb_feedback`，参与检索加权） |
| POST | `/api/kb/search` | 只读检索：`{"text": str}` → `{"hits": [{id, content}]}`（卡点雷达"检索历史方案"用） |
| GET | `/api/stuck?limit=50` | 卡点报告列表（倒序）：`{id, agent, context, ts_human, age_sec}` |
| GET | `/api/stuck/stats` | 卡点聚合：`{by_agent: {agent: n}, total_24h, total_7d}`（保留上限 `stuck_retention_max`，默认 200） |
| GET | `/api/stats` | 会话统计：最近 50 个 session 的 turns / chars / est_cost / 四类 token |
| GET | `/api/sessions` | 会话历史列表（含 exists 标记） |
| GET | `/api/sessions/{id}/transcript` | 会话日志：默认返回渲染后 HTML；`?raw=1` 返回 `{lines: 末200行, touched_files, stats: {turns, chars, est_cost, input/output/cache_read/cache_creation_tokens}}`（复盘报告数据源） |
| POST | `/api/feedback` | 用户反馈（本地留存，secrets 脱敏） |

## WebSocket `/ws`

鉴权：`?ticket=<一次性票据>`（推荐）或 `?token=<token>`；拒绝时 close code **1008**（前端会引导重新登录）。

**服务端 → 客户端：**
- `context_append`：日志追加（agent / path / content / context_percent / touched_files）
- `agent_spawn` / `agent_waiting` / `agent_unblocked`：Agent 状态事件（waiting 触发系统通知）
- `kb_recommendation`：KB 主动推荐（toast）
- `error_warning`：错误预警卡片（详情折叠 + 一键诊断；死循环/震荡检测复用此通道）
- `ai_response_start` / `ai_response_chunk` / `ai_response_done`：副脑流式回答
- `kb_merge_result` / `session_sync` / `config_updated` / `pong`：回执类

**客户端 → 服务端：**
- `chat`：副脑提问 `{content, mode: light|private|audit|onedive, agent?}`
- `inject_insight`：注入 KB 条目 `{content}`
- `merge_kb`：把当前对话/上下文并入 KB
- `request_full_sync`：连接建立后的状态同步
- `ping`：30s 保活

## MCP（stdio / `--http`）

`python -m src.mcp_server` 暴露 4 个工具（供 Claude Code / Cursor 等直接调用）：

| 工具 | 说明 |
|---|---|
| `read_gabriel_kb(query)` | 检索知识库（向量+RRF+反馈加权；无 query 返回最新 5 条） |
| `add_gabriel_insight(content)` | 外部 Agent 主动写入经验（自动分词/向量化，返回 `已入库 insight #id`） |
| `report_agent_stuck(agent, context)` | 报告卡点（落 `stuck_reports`，命中历史方案时返回附注） |
| `get_session_summary(agent_path)` | 会话遥测摘要（turns / chars / est_cost / 四类 token） |

## 错误约定

- 401：token 缺失/无效（前端统一弹登录框）
- 404：会话/日志不存在（transcript 端点）
- 503：`/api/health` 在 tailer 未就绪或 stale 时
- 业务错误：`{"status": "error", "message": "..."}`；成功多为 `{"status": "success", ...}` 或直接数据体
