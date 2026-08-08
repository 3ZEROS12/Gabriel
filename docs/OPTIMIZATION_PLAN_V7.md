# Gabriel 优化方案 v7（供 Gemini / Agent 执行）— 取代 v6

> 生成时间：2026-08-08。基于当前工作区（master @ `cf7726b`，CI 已全绿）逐行审计撰写。
> **取代 `docs/OPTIMIZATION_PLAN_V6.md`**（其 P0/P1/P2 均已验收；在该文件顶部标注"已被 v7 取代"）。
> 执行 Agent：先读本文件全文 → 跑 §1 基线验证 → 严格按 §2 顺序推进，每项验收后才进下一项。

---

## 0. 一句话北极星

**把"副脑"从被动应答升级为生态节点**：① 外部 Agent 可通过 MCP 主动写入经验、报告卡点、查询进展（双向 MCP）；② Gabriel 自己侦测死循环/工具震荡并预警；③ 长会话一键生成复盘报告。全程复用现有基础设施，禁止重复造轮子。

---

## 1. 当前基线（2026-08-08 逐行核实 — 以下已存在，**禁止重复实现**）

| 功能 | 位置（当前行号） | 状态 |
|---|---|---|
| MCP read 工具（唯一工具） | `src/mcp_server.py:21` MCPServer、`:37` `read_gabriel_kb`、`:68` main() | ✅ 已有（stdio + `--http`） |
| KB 写入三处（已重复 3 次，本轮必须收敛为共享函数） | `update_kb` `/api/kb` POST `main.py:639`；merge_kb / inject_insight WS（grep `insights_fts (content` 定位） | ✅ 已有 |
| 结构化/分词/向量辅助 | `parse_structured_insight` `:120`、`tokenize_for_fts` `:114`、`store_insight_vector` `:95`、`get_embedder` `:46` | ✅ 已有 |
| 错误预警通道（详情折叠 + 一键诊断，前端已渲染） | 后端 `error_warning` `main.py:1567-1570`（阈值/冷却已 config 化）；前端 `static/script.js` error_warning handler | ✅ 已有，**死循环检测直接复用此通道，前端零改动** |
| 会话数据源 | `get_sessions` `:741`、`get_session_transcript` `:768`、`get_stats` `:681`、`extract_touched_files` `:1097`、`build_snapshot` `:1182` | ✅ 已有 |
| 前端会话回看/导出 | `openSessionReview` `script.js:1417`、`exportAgentLog` `:1548`、`sessionHistoryList` `:1374` | ✅ 已有 |

**基线验证命令（必须真实执行、贴出真实输出后才开工）：**
```bash
venv\Scripts\python.exe -m pytest tests/ -q        # 期望 26 passed
venv\Scripts\python.exe -m ruff check src tests    # 期望 All checks passed!
node --check static/script.js                      # 期望无输出
```

---

## 2. 任务列表（严格按序，每项验收后才进下一项）

### P0: 双向 MCP（生态价值最高、成本最低）

**目标**：`src/mcp_server.py` 从单工具扩展为 4 工具；**KB 写入收敛为单一共享函数**（当前三处拷贝必须合并，禁止再复制第四份）。

**实施步骤：**

1. **抽取共享写入函数**（放 `main.py`，`update_kb` `:639` 附近）：
   ```python
   def save_insight(content: str, problem: str = "", cause: str = "", solution: str = "", tags: str = "", agent_path: str = "") -> int:
       """单一 KB 写入入口：insights + insights_fts(分词) + insights_vec(向量)。
       返回新 insight id；任何单步失败不得影响主流程（向量失败仅 warning）。"""
   ```
   - `/api/kb` POST（`:639`）、merge_kb、inject_insight 三处全部改调 `save_insight`（保留各自现有行为与降级语义）。
2. **新增 MCP 工具**（`src/mcp_server.py`，复用 `save_insight` / `parse_structured_insight` / `_transcript_cache`）：
   - `add_gabriel_insight(content: str) -> str`：`parse_structured_insight` → `save_insight` → 返回 `"已入库 insight #id"`；解析失败时四字段为空、content 整段入库（不丢数据）。
   - `report_agent_stuck(agent: str, context: str) -> str`：写入新表 `stuck_reports(id, agent, context, ts)`（**必须在 `init_schema` 建表**），返回确认；不推送任何事件（保持最小）。
   - `get_session_summary(agent_path: str = "") -> str`：读 `session_meta` 最新一条 + `_transcript_cache` 尾部（或 transcript 文件末 60 行），输出文本摘要（turns / chars / est_cost / 四类 token / 最近工具 / waiting 状态）。
3. 三工具均为同步函数，`@mcp.tool(name=..., description=...)` 装饰；保持 `read_gabriel_kb` 不动。

**验收标准：**
- [ ] 单测 ≥3（patch `main.ROOT_DIR` 临时库直调三个工具函数）：add 后 `/api/kb` 可读且 FTS/向量可检索；report 落库可查；summary 含 cost/tokens 字段
- [ ] `save_insight` 收敛后 `rg "INSERT INTO insights" main.py` 仅剩 1 处（`save_insight` 内）
- [ ] `uvx mcp dev src/mcp_server.py`（或单测直调）验证 4 工具全部注册
- [ ] pytest 全绿（26+N）

### P1-1: 死循环/震荡检测

**目标**：`async_log_tailer` 在 `error_warning` 逻辑（`:1567`）旁增加滑动窗口循环检测，复用现有预警卡片通道。

**实施步骤：**

1. **纯函数**（放 `_compress_lines` 附近，供单测）：
   ```python
   def _tool_signature(line: str) -> str | None:
       """从 transcript 行提取规范化工具签名：TOOL_CALL/tool_calls/run_command
       取工具名或命令首 token；非工具行返回 None。"""

   def detect_loop(signatures: list, window: int = 8, repeat: int = 5) -> str | None:
       """滑动窗口内同一签名出现 >= repeat 次 → 返回该签名；否则 None。"""
   ```
2. **tailer 接入**（`async_log_tailer`，`last_error_warnings` 附近 `:1421`）：
   - 每文件维护 `collections.deque(maxlen=window)`（`window = config.get("loop_detection_window", 8)`）；
   - 每次 mtime 变化对 `new_lines` 逐行 `_tool_signature` 入队；
   - `detect_loop` 命中且距上次同文件预警 > `loop_detection_cooldown`（默认 60）→ 复用 `error_warning` 消息：
     ```json
     {"type": "error_warning", "agent": ..., "path": ..., "content": "疑似死循环：命令「X」在最近 N 次工具调用中重复 M 次，建议打断或调整策略"}
     ```
   - 前端 `error_warning` 卡片（已有"详情"+"⚡ 一键诊断"）**零改动**直接可用。
3. **配置**：`DEFAULT_CONFIG` 与 `ConfigModel` 加 `loop_detection_window: int = 8`、`loop_detection_repeat: int = 5`、`loop_detection_cooldown: int = 60`。

**验收标准：**
- [ ] 单测 ≥2：`detect_loop` 命中/未命中两态；`_tool_signature` 对 JSON 工具行与普通行正确区分
- [ ] config 可调（窗口/重复数/冷却）
- [ ] 推送复用 `error_warning` 类型（前端无新增 UI）

### P1-2: Session 复盘报告（一键 Markdown）

**目标**：会话回看页一键生成含成本/文件/错误的复盘报告，复用现有数据源与导出模式。

**实施步骤：**

1. **后端**：`get_session_transcript`（`:768`）支持 `?raw=1` → 返回：
   ```json
   {"status": "success", "lines": [...末200行原始行...], "touched_files": [...], "stats": {turns, chars, est_cost, input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens}}
   ```
   （`touched_files` 用 `extract_touched_files`；`stats` 从 `session_meta` 取。）
2. **前端**：`openSessionReview`（`script.js:1417`）回看面板加"📝 生成复盘报告"按钮：
   - 拉 `?raw=1` + `/api/sessions` → 组装 Markdown（任务耗时 / turns / token 与 cost 明细 / 触碰文件列表 / 错误行摘要（Error|Exception 行前 10 条，代码块包裹）/ 报告头尾）；
   - 下载复用 `exportAgentLog`（`:1548`）的 Blob 下载模式；
   - **原始日志行必须放入 Markdown 代码块**（防格式注入）。
3. 不做新后端端点聚合（现有接口够用）。

**验收标准：**
- [ ] 单测：`?raw=1` 响应结构完整
- [ ] 人工：回看页点击产出包含 cost/tokens/文件/错误摘要的 .md 文件

---

## 3. 技术护栏（v6 全部保留，新增 12-15）

1. **真实性纪律**：改动真实落盘后跑 `venv\Scripts\python.exe -m pytest tests/ -q` 并贴出真实输出；禁止声称未执行的测试结果。
2. `format_transcript` 返回 **3 元组**，改形状必须同步全部调用方。
3. `SYSTEM_PROMPT` 保持模块级定义。
4. 价格/阈值显式 `0` 合法，禁止 `cfg.get(k, d) or d` 兜底。
5. 所有 API 端点走 `verify_token`；`innerHTML` 过 DOMPurify；后端输出 class 语义。
6. 离线优雅降级，任何新依赖不可用不得阻塞主流程。
7. 每完成一项更新 §4 完成度核对表。
8. 向量嵌入必须本地生成。
9. **行号以 `grep` 实测为准**（本文档行号是生成时刻快照）。
10. 本轮结束必须 `git commit`（不 push 除非用户要求）。
11. sqlite-vec 不可用 → 回退纯 FTS5。
12. **KB 写入单一来源**：新增 `save_insight()`，现有三处拷贝（/api/kb、merge_kb、inject_insight）全部收敛；MCP 工具不得再复制插入代码。
13. **死循环检测不得刷屏**：默认冷却 + 可配阈值；单测用确定性输入。
14. **新表必须进 `init_schema`**（`stuck_reports`），禁止在业务代码里裸建表。
15. 复盘报告中的原始日志必须进 Markdown 代码块，禁止裸拼。

## 4. 完成度核对表（执行者逐项填写）

| 任务 | 状态 | commit | 真实测试输出 | 备注 |
|---|---|---|---|---|
| 基线核对（pytest 26 + ruff + node） | ✅ 已通过 | `cf7726b` | 26 passed, 0 ruff errors, node clean | 基础健全 |
| P0 双向 MCP（save_insight 收敛 + 3 工具） | ✅ 已通过 | `927d080` | 27 passed, 0 ruff errors | 收敛 KB 写入为单一 save_insight，扩展 MCP 4 工具全绿 |
| P1-1 死循环检测 | ✅ 已通过 | `bd1cc95` | 28 passed, 0 ruff errors | 滑动窗口 tool signature 检测死循环与工具震荡 |
| P1-2 Session 复盘报告 | ✅ 已通过 | `c63a532` | 29 passed, 0 ruff errors, node clean | 支持 ?raw=1 端点与前端一键生成 Markdown 复盘 |

## 5. 执行节奏

按 `P0 → P1-1 → P1-2` 顺序，禁止跳跃并行。每完成一项输出简短进度报告（对照验收标准逐条自检）并 `git commit`；全部完成后：pytest + ruff + node 三绿、更新 `docs/OPTIMIZATION_ROADMAP_2026.md` 顶部状态、在 `docs/OPTIMIZATION_PLAN_V6.md` 顶部标注"已被 v7 取代"。
