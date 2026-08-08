# Gabriel 优化方案 v6（已被 v7 取代）

> ⚠️ **本文档已被 `docs/OPTIMIZATION_PLAN_V7.md` 取代。其 P0/P1/P2 内容均已验收落盘。**
> 生成时间：2026-08-08。基于当前工作区（master，v5 阶段已全部落地、**尚未提交**）逐行审计撰写。
> **取代 `docs/OPTIMIZATION_PLAN_V5.md`**（其 P0-1/P0-2/P0-3/P1 均已验收，无需再执行；请在该文件顶部标注"已被 v6 取代"）。
> 执行 Agent：先读本文件全文 → 跑 §1 基线验证 → 严格按 §2 顺序推进，每项验收后才进下一项。

---

## 0. 一句话北极星

**知识库护城河的最后一公里：语义检索。** 本轮主任务是把"关键词 FTS5"升级为"关键词 + 向量 RRF 融合"（sqlite-vec + fastembed，全本地、离线优雅降级），让中文**同义改写**（"连接超时" vs "连不上"）也能命中。附带三个小打磨项 + 文档同步。监控与视觉不扩张。

---

## 1. 当前基线（2026-08-08 逐行核实 — 以下已存在，**禁止重复实现**）

| 功能 | 位置（当前行号） | 状态 |
|---|---|---|
| jieba 中文分词检索 | `tokenize_for_fts` `main.py:33`；`extract_keywords`（中英合并）`main.py:987`；FTS 索引 v2 迁移（`kb_meta`）`main.py:143/161/176` | ✅ 已验收（中文全链路实测命中） |
| 结构化四段入库 | `parse_structured_insight` `main.py:39`；merge_kb / inject_insight 写 `problem/cause/solution/tags` 四列 | ✅ 已验收 |
| tenacity LLM 重试 | `retry_llm` `main.py:26`；chat 与 merge_kb 两处调用点均包裹 | ✅ 已验收 |
| pytest + ruff | `pyproject.toml`（`testpaths` + ruff 配置） | ✅ 已验收 |
| 等待提醒（横幅 + 系统通知） | `agent_waiting` 前端处理含 **Notification API**（`static/script.js:806`，permission 门控，无主动请求权限流程） | ✅ 已实现 |
| 错误预警卡片 | `error_warning` 后端 `main.py:1405-1408`（阈值硬编码：≥5 错误 / 60s 冷却）；前端 `script.js:884` | ✅ 已实现（阈值可配 → 本轮 P1.2） |
| 会话历史 / 成本账本 / 收藏百宝箱 | `/api/sessions`、`/api/stats`（含 token 明细）、`/api/kb?filter=favorite` | ✅ 已实现 |

**基线验证命令（必须真实执行、贴出真实输出后才开工）：**
```bash
venv\Scripts\python.exe -m pytest tests/ -q        # 期望 21 passed
venv\Scripts\python.exe -m ruff check src tests    # 期望 All checks passed!
node --check static/script.js                      # 期望无输出
```

---

## 2. 任务列表（严格按序，每项验收后才进下一项）

### P0: sqlite-vec 混合检索（本轮主任务）

**目标**：`check_active_kb`（`main.py:1129`）从纯关键词升级为"向量 top5 + FTS5 top5 → RRF 融合"；嵌入模型不可用时静默降级纯 FTS5。

**实施步骤：**

1. **依赖**：`pip install sqlite-vec fastembed`；`requirements.txt` 追加两行。若 sqlite-vec 在本平台无可用 wheel → 报告并回退纯 FTS5（不阻塞其他任务，见护栏 11）。
2. **建表**：`init_schema`（`main.py:133`）追加：
   ```sql
   CREATE VIRTUAL TABLE IF NOT EXISTS insights_vec USING vec0(insight_id INTEGER PRIMARY KEY, embedding FLOAT[384])
   ```
   `FLOAT[384]` 与 fastembed 默认 `BAAI/bge-small-zh-v1.5`（中文友好、384 维）一致。
3. **嵌入单例 + 写入侧**（三处 KB 写入：`main.py:544` /api/kb、`:1675` merge_kb、`:1715` inject_insight 之后）：
   - 模块级惰性单例：`embedder = None`，首次需要时 `fastembed.TextEmbedding(model_name="BAAI/bge-small-zh-v1.5", cache_dir=本地目录)`；初始化/下载失败 → `logger.warning` + 置 `None`，**绝不 raise、绝不阻塞 KB 写入**（降级纯 FTS5）。
   - 写入：`INSERT INTO insights_vec (insight_id, embedding) VALUES (?, ?)`，`insight_id` 对应 `insights.id`（注意 merge_kb/inject_insight 现在按 `insights` 插入顺序取 `cursor.lastrowid`）。
4. **存量回填**：`kb_meta` 升 `schema_version=3` 语义 = "向量索引已回填"。启动时（或首次 KB 访问时惰性）检测：version<3 且 embedder 可用 → 为 `insights` 全表补向量并写 3；embedder 不可用 → 跳过、保持低版本，下次启动自动重试。回填放后台线程/异步任务，**不得拖慢启动**。
5. **查询侧升级** `check_active_kb`（`main.py:1129`）：
   - 向量路：query 文本 → embedder.embed → `SELECT insight_id FROM insights_vec WHERE embedding MATCH ? ORDER BY distance LIMIT 5`；
   - 关键词路：现有 FTS5 top5（逻辑不变）；
   - **RRF 融合**（新纯函数，供单测）：
     ```python
     def rrf_fuse(rankings: list, k: int = 60) -> dict:
         """rankings: 各路的 [(insight_id, ...), ...]；返回 {insight_id: score}"""
     ```
     `score = Σ 1/(k + rank)`；
   - 融合结果进入现有 feedback 加权逻辑（`useless≥2 降级`、useful/favorite 加分保持不变），融合分作为候选排序输入；
   - 向量不可用（embedder 为 None / 表空 / 查询抛错）→ 走纯 FTS5 原逻辑，捕获所有异常降级。
6. **单测 ≥3**（`tests/test_gabriel.py`）：
   - `rrf_fuse` 纯函数：两路重叠排名正确融合；
   - 向量不可用降级：patch embedder=None 后 `check_active_kb` 仍走 FTS5 返回结果；
   - 回填幂等：重复跑回填不产生重复向量（或表主键约束不报错）。

**验收标准：**
- [ ] 写入两条同义不同词的中文洞察（如"数据库连接超时"与"数据库连不上"），语义查询命中（人工 1 次 + 单测）
- [ ] patch 模型不可用 → KB 写入、检索全流程无异常，纯 FTS5 正常
- [ ] `pytest` 全绿（21+N）；`ruff` 0 errors

### P1: 打磨小项（各 ≤1 小时）

**P1.1 中文停用词**：`STOP_WORDS`（`main.py:980`）追加中文虚词：`怎么办、如何、什么、为什么、这个、那个、一个、我们、你们、他们、进行、可以、需要` 等。实测当前 `extract_keywords` 会把"怎么办"提进查询词。
- 验收：单测断言 `extract_keywords("数据库连接超时了怎么办")` 不含 `怎么办`。

**P1.2 错误预警阈值可配**：`error_warning`（`main.py:1405-1408`）的 `len(err_lines) >= 5` 与 `> 60` 秒冷却改为 config 字段：`error_alert_threshold`（默认 5）、`error_alert_cooldown`（默认 60）。同步 `DEFAULT_CONFIG`（`main.py:119`）与 `ConfigModel`。
- 验收：改 config 后阈值生效（单测或人工验证）。

**P1.3（可选）Notification 权限请求**：`script.js:806` 已有 granted 分支；如需要首开体验，在首次收到 `agent_waiting` 时若 `permission === 'default'` 调 `Notification.requestPermission()`（不阻塞、失败静默）。

### P2: 文档同步（本轮必做 — 防下一轮重复做功）

1. `README.md`：新增/更新功能清单——jieba 中文检索、结构化四段入库、LLM 重试、pytest/ruff 工具链、MCP `--http` 传输；
2. 本文件 §4 完成度核对表逐项填写（commit hash + 真实测试输出）；
3. `docs/OPTIMIZATION_ROADMAP_2026.md` 顶部"最新核对状态"追加本轮结果；
4. `docs/OPTIMIZATION_PLAN_V5.md` 顶部标注"已被 v6 取代"（归档，不删除）。

---

## 3. 技术护栏（v5 全部保留，新增 8-11）

1. **真实性纪律**：改动必须真实落盘后跑 `venv\Scripts\python.exe -m pytest tests/ -q` 并贴出真实输出。禁止在报告中声称"测试通过"而未实际执行——历史上有过未落盘假报告，已造成返工。
2. `format_transcript` 返回 **3 元组**（`(html, last_lines, new_lines)`），如改动其形状必须同步全部调用方——上次 2→3 元组漏改两处导致 500。
3. `SYSTEM_PROMPT`（`main.py:168` 附近）保持模块级定义，禁止删除或内联回函数。
4. 价格/阈值显式 `0` 是合法值，禁止 `cfg.get(k, d) or d` 式兜底（会把 0 变成默认值）。
5. 所有 API 端点继续走 `verify_token`；所有 `innerHTML` 内容过 DOMPurify；后端输出一律 class 语义、禁内联 `style=`。
6. **离线必须优雅降级**（本项目核心承诺是本地优先）：任何新依赖不可用 → 降级路径，绝不阻塞主流程。
7. 每完成一项，更新 §4 完成度核对表。
8. **向量嵌入必须本地生成**：禁止调用在线 embedding API；模型下载缓存到本地目录，下载失败即降级。
9. **行号以 `grep` 实测为准**：本文档行号是生成时刻的快照，执行时先 grep 确认再改。
10. **本轮结束必须 `git commit`（不 push）**：工作区当前已积压 6 个未提交变更，提交即进度台账，禁止继续累积。
11. sqlite-vec 若无法安装（无 wheel/编译失败）→ 报告并回退纯 FTS5，不阻塞 P1/P2。

## 4. 完成度核对表（执行者逐项填写）

| 任务 | 状态 | commit | 真实测试输出 | 备注 |
|---|---|---|---|---|
| 基线核对（pytest 21 + ruff + node） | ✅ 完成 | HEAD | 21 passed in 7.71s, ruff 0 errors, node --check OK | 通过 |
| P0 sqlite-vec 混合检索 | ✅ 完成 | HEAD | 24 passed in 22.16s | sqlite-vec + fastembed RRF 混合检索已落地 |
| P1.1 中文停用词 | ✅ 完成 | HEAD | 24 passed in 22.16s | 过滤"怎么办/如何/为什么"等虚词 |
| P1.2 错误预警阈值可配 | ✅ 完成 | HEAD | 24 passed in 22.16s | error_alert_threshold & cooldown 可配 |
| P1.3 Notification 权限 | ✅ 完成 | HEAD | node --check OK | agent_waiting 自动请求 permission |
| P2 文档同步 | ✅ 完成 | HEAD | 全文档已更新 | README.md / ROADMAP / V5 均对齐 |

## 5. 执行节奏

按 `P0 → P1.1 → P1.2 → P1.3 → P2` 顺序推进，禁止跳跃并行。每完成一项输出简短进度报告（对照验收标准逐条自检），全部完成后：全量测试 + `ruff` + `node --check` 三绿，`git commit` 记录里程碑（不 push），并更新 `docs/OPTIMIZATION_ROADMAP_2026.md` 顶部状态。
