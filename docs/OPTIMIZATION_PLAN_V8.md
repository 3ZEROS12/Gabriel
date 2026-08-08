# Gabriel 优化方案 v8（供 Gemini / Agent 执行）

> 生成时间：2026-08-08。基于当前工作区（master @ `9e030ad`，v7 全量验收通过，29/29 测试全绿）逐行审计撰写。
> 执行 Agent：先读本文件全文 → 跑 §1 基线验证 → 严格按 §2 顺序推进，每项验收后才进下一项。

---

## 0. 一句话北极星

**让 Gabriel 已埋下的每一条数据都流动起来**：① `stuck_reports` 从"只写不读"的数据孤岛变成**卡点雷达**（前端可见、可统计、一键检索历史方案）；② 反馈加权从 `check_active_kb` 的内联代码收口为**共享检索管道**，让 MCP 外部 Agent 也享受"越用越准"；③ 补上**稳定性长跑验证与一键分发路径**，让项目达到 Goal Spec 的"成熟期"门槛。全程复用现有基础设施，禁止重复造轮子。

---

## 1. 当前基线（2026-08-08 逐行核实 — 以下已存在，**禁止重复实现**）

### 1.1 工具链与规模

| 项 | 值 |
|---|---|
| 测试 | `tests/test_gabriel.py`，**29 passed**（v7 后新增 P0/P1-1/P1-2 各 1+） |
| 静态检查 | ruff `All checks passed!`（仅本地，CI 未含 ruff — 见 P2-2） |
| 前端 | `node --check static/script.js` 无输出 |
| 文件规模 | `src/main.py` 2057 行 / `src/mcp_server.py` 172 行 / `static/script.js` 1696 行 / `static/index.html` 435 行 |

### 1.2 关键现状（全部 grep 实测，行号以 `rg` 再核实为准）

| 功能 | 位置 | 状态 |
|---|---|---|
| **卡点数据**：`stuck_reports` 表 | `init_schema` `main.py:293`；唯一写入 `mcp_server.py:96-110`（`report_agent_stuck`） | ⚠️ **无任何消费端**（前端/API 零引用），**无保留上限**（无限增长） |
| **检索核心**：`rrf_fuse`（纯 RRF，向量+FTS 融合） | `main.py:66` | ✅ 已有 |
| **内部检索**：`check_active_kb`（**含完整反馈加权公式**） | `main.py:1419-1473`：`delta=(useful-0.8*useless+1.5*eff_fav)/max(1,total_votes)`；`useless>=2 → score=-10`；阈值 `>-5` | ✅ 已有，但公式**内联**不可复用 |
| **外部检索**：MCP `read_gabriel_kb` | `mcp_server.py:39-67` | ⚠️ **纯 FTS5**（`MATCH ? ORDER BY rank`），无向量/RRF/反馈加权 — 外部 Agent 检索质量低于内部路径 |
| 裸建表违规 | `check_active_kb` 内 `CREATE TABLE IF NOT EXISTS kb_feedback` `main.py:1455`（`init_schema:294` 已有同表） | ⚠️ 违反护栏 #14，需清除 |
| **KB 端点** | `GET /api/kb` `:644`（filter=favorite/all/latest 纯列表，无搜索排序）；`POST /api/kb` `:705`；`POST /api/kb/feedback` `:718`（直接 INSERT） | ✅ 已有 |
| **副脑快照**：三层（`[现场]`状态/工具/文件Top5/Error计数 → `[命中历史]`KB命中 → `[时间线]`压缩事件 → `[原始尾部]`仅全文模式）；重复折叠+200字符截断（`_compress_lines`）；`logger.info` 字符数 | `build_snapshot` `main.py`（`_compress_lines` 紧邻）；单测已覆盖（`tests` 208-267） | ✅ **已全部落地，v8 禁止重做** |
| 死循环检测 / 复盘报告 / 双向 MCP（v7） | `_tool_signature` `:1210`、`detect_loop` `:1271`；`?raw=1` `get_session_transcript:816`；MCP 4 工具 | ✅ 已有 |
| 系统通知 / waiting 翻转降噪 / chat_history 持久化 / reduced-motion | `script.js:806-813`；`main.py:1697`（"avoids a spurious agent_unblocked"）；`main.py:296,1842`；`style.css` 1 处 | ✅ 已有 |
| 前端 Radar 子 Tab 模式（卡点 Tab 照此模仿） | `index.html:194` `btnRadarSubHistory` + `:262` `sessionHistoryList`；`script.js:1374` `sessionHistoryList()` | ✅ 已有 |
| 预警卡片通道（卡点复用，前端零改动） | 后端 `error_warning`（v7 基线 `:1567-1570` 区域）；前端详情折叠+⚡一键诊断 | ✅ 已有 |
| CI | `.github/workflows/ci.yml`：仅 pytest job（windows-latest, Python 3.11, `PYTHONUTF8=1`），**无 ruff、无稳定性冒烟** | ✅ 已有（可加固） |
| 桌面打包 | `Gabriel.spec`（PyInstaller）+ `build/` `dist/` 目录已存在 | ✅ 已有（未纳入本轮自动验证） |
| 发布路径 | `setup.py` + `pyproject.toml` + `MANIFEST.in`；`pip install -e .` 可用 | ⚠️ 无 sdist/wheel 构建与发布文档 |

**基线验证命令（必须真实执行、贴出真实输出后才开工）：**
```bash
venv\Scripts\python.exe -m pytest tests/ -q        # 期望 29 passed
venv\Scripts\python.exe -m ruff check src tests    # 期望 All checks passed!
node --check static/script.js                      # 期望无输出
```

---

## 2. 任务列表（严格按序，每项验收后才进下一项）

### P0: 卡点雷达闭环（stuck_reports 数据孤岛 → 可见、可查、可闭环）

**目标**：`stuck_reports` 有 API 消费端、有前端 UI、有保留策略、有"卡点→历史方案"即时闭环。

**实施步骤：**

1. **后端 API**（`main.py` 路由区，`/api/kb` 附近 `:644` 区域，全部走 `api_router` + `verify_token`）：
   - `GET /api/stuck?limit=50` → `{"status":"success","reports":[{id, agent, context, ts_human, age_sec}]}`（`ORDER BY id DESC LIMIT ?`，`ts` 用 `time.strftime` 转可读）。
   - `GET /api/stuck/stats` → `{"by_agent": {"<agent>": n, ...}, "total_24h": n, "total_7d": n}`（`ts > now-86400` / `ts > now-604800`，按 agent `GROUP BY`）。
   - **保留策略**（必须，防无限增长）：`DEFAULT_CONFIG` 与 `ConfigModel` 加 `stuck_retention_max: int = 200`；查询时顺带 `DELETE FROM stuck_reports WHERE id NOT IN (SELECT id FROM stuck_reports ORDER BY id DESC LIMIT ?)`（参数取 retention）。
2. **卡点→KB 即时闭环**（`mcp_server.py` `report_agent_stuck`，`:96-110`）：落库后调 `check_active_kb(context)`（现成，含反馈加权），命中则在返回串附 `📌 历史方案: <content>`（保持 MCP 工具同步、最小侵入，不推 WS 事件）。
3. **前端"🛟 卡点雷达"子 Tab**（Radar 页，完全模仿 `btnRadarSubHistory`/`sessionHistoryList` 模式，`index.html:194` 旁加 `btnRadarSubStuck` + 容器 `stuckList`）：
   - 列表渲染：agent 徽标 + 可读时间 + `context` 摘要（超长截断）；空态文案"暂无卡点报告"；加载失败态。
   - 每项"🔍 检索历史方案"按钮：**新增只读搜索端点** `POST /api/kb/search`（body `{"text": str}`，走 `verify_token`，内部调 `check_active_kb(text)` 包装成列表返回 `{"hits": [{id, content}]}`；P1 落地后该端点改调 `search_kb`）→ 前端渲染前 3 条命中 + 复制按钮（复用 `btn-insight-copy` 样式）。（**已核实**：`POST /api/kb` `:705` 是写入语义，禁止用于搜索。）
   - 顶部 mini 统计：24h / 7d 计数 + 卡点最多 agent。

**验收标准：**
- [ ] 单测 ≥4：`GET /api/stuck` 列表倒序与 limit 生效；`/api/stuck/stats` 24h/7d 聚合正确；保留策略超限后旧记录被清理；鉴权（无 token → 401）
- [ ] 单测 ≥1：`POST /api/kb/search` 命中已有 insight、未命中返回空列表不报错
- [ ] 手工：`python -c "import asyncio; from src.mcp_server import report_agent_stuck; print(report_agent_stuck('test-agent', '反复执行 build 失败'))"` 后，前端卡点 Tab 出现该条；点"检索历史方案"有结果（或空态不报错）
- [ ] `rg "stuck_reports" static/` 非空（消费端存在）；pytest 全绿（29+N）

### P1: 检索管道收口（"越用越准"惠及所有入口）

**目标**：把 `check_active_kb:1419-1473` 内联的检索+加权逻辑抽为**共享纯函数**，`check_active_kb` 与 MCP `read_gabriel_kb` 双入口收敛；清除 `:1455` 裸建表。**行为不得回退**：无反馈输入时输出与 v7 完全一致（回归护栏 #17）。

**实施步骤：**

1. **共享检索函数**（放 `rrf_fuse` `:66` 附近）：
   ```python
   def search_kb(text: str, limit: int = 5) -> list:
       """统一检索管道：FTS5(分词) + sqlite-vec + RRF 融合 + 反馈加权重排。
       返回 [(insight_id, content, score)]，按分降序；无反馈时与纯 RRF 输出一致。
       复用：extract_keywords / tokenize_for_fts / get_embedder / store_insight_vector 同源工具。"""
   ```
   - 反馈加权逻辑**原样搬移**（delta 公式、`useless>=2 → -10`、阈值过滤），公式不许改；`kb_feedback` 按 insight `GROUP BY` 一次性聚合（替代现有逐条 SELECT，顺带修 N+1）。
   - 向量/嵌入失败静默降级（沿用 `load_sqlite_vec` 降级语义）。
2. **收敛入口**：
   - `check_active_kb` 改为 `hits = search_kb(text, limit=5)` 后取 best（保留现有返回形状 `{"id","content"}`，**返回 JSON 形状不得变**——调用方：`build_snapshot`、toast 推荐、`error_warning` 一键诊断）。
   - MCP `read_gabriel_kb` 改为调 `search_kb(query, limit=5)`（`mcp_server.py` 已 import `save_insight, init_schema, ROOT_DIR`，补 import `search_kb`）；无 query 时保持"最新 5 条"语义（`ORDER BY timestamp DESC` 不动）。
   - `POST /api/kb/search`（P0 产出）内部由 `check_active_kb` 切换为 `search_kb`，返回形状不变。
   - 删除 `check_active_kb` 内 `:1455` 裸建表（`init_schema:294` 已有）。
3. 全程单测保护：现 29 个测试中 `test_rrf_fuse_and_vector_fallback`、快照 KB 命中测试即回归网，禁改其断言。

**验收标准：**
- [ ] 单测 ≥3：`search_kb` 无反馈时结果序 == 纯 RRF 序（回归护栏）；给某条投 1 次 useful 后其排位提升；`useless>=2` 条被降权至末尾
- [ ] `rg "CREATE TABLE IF NOT EXISTS kb_feedback" src/main.py` 仅剩 `init_schema` 内 1 处（`:294`）
- [ ] MCP `read_gabriel_kb("相同查询")` 结果序与 `check_active_kb` 同源一致（人工对比或单测）
- [ ] pytest 全绿（29+N，含既有 RRF/快照用例原样通过）

### P2: 稳定与分发（Goal Spec "成熟期"门槛）

**目标**：可参数化的长跑稳定性验证 + CI 加固 + 发布路径文档化。**禁止默认长时间阻塞**（护栏 #19）。

**实施步骤：**

1. **稳定性脚本** `scripts/stability_run.py`（参考 `scripts/` 现有脚本风格）：
   - 启动 `src.main` app（`TestClient` 或子进程 + 随机端口），`--hours` 参数（默认 **0.25** 冒烟，最大 72）。
   - 每 60s 采样：RSS（`psutil` 若可用，否则 `os`/子进程内存）、WS 连接数（`/api/stats` 代理）、chat 一轮、KB 读写一轮、WS 断线重连一次（正常关连接再重连）。
   - 结束断言：后半程内存均值 ≤ 前半程均值 × 1.15（无单调泄漏）；进程退出后端口可复用（无残留）；错误日志零新增（error 级）。
   - 输出 `stability_report.txt`（采样表 + 断言结果），退出码非 0 表示失败。
2. **CI 加固**（`.github/workflows/ci.yml`）：
   - test job 追加 `ruff check src tests` 步骤（`pip install ruff`）。
   - 新增可选 job（`workflow_dispatch` 或独立 `stability-smoke.yml`）：`python scripts/stability_run.py --hours 0.25`。
3. **发布路径文档化**（`docs/RELEASE.md`，新增）：
   - `python -m build`（sdist+wheel，`build` 包加进 `requirements-dev` 或文档注明）→ `twine check` → 全新 venv `pip install dist/*.whl` → `gabriel` 命令冒烟 → PyPI 发布命令（**写明需用户凭据，文档不代跑**）。
   - 桌面打包：`pyinstaller Gabriel.spec` 命令与产物冒烟步骤（人工执行，列入手工验收）。
4. **禁止改动**：`setup.py`/`pyproject.toml` 仅允许按需加 build 依赖，不改入口命令。

**验收标准：**
- [ ] 冒烟 `--hours 0.25`（15 分钟）跑通，报告含 3 组以上采样且断言通过；`--hours 72` 有文档说明为人工长跑项
- [ ] CI 含 ruff 步骤且通过；stability 冒烟 job 可手动触发
- [ ] 全新 venv `pip install dist/*.whl` 后 `gabriel --help` 有输出
- [ ] `docs/RELEASE.md` 覆盖 sdist/wheel 构建、twine 检查、PyPI 发布、PyInstaller 四条路径

---

## 3. 技术护栏（v1-v15 全部保留，新增 16-20）

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
12. KB 写入单一来源：`save_insight()`（v7 已收敛），本轮**检索单一来源**由 `search_kb()` 接管，禁止再复制检索代码。
13. 死循环检测不得刷屏（v7 已配冷却），本轮卡点保留策略同理：**stuck_reports 必须有上限**（护栏 #16 同源）。
14. 新表必须进 `init_schema`，禁止业务代码裸建表——**现 `:1455` 违规必须清除**。
15. 复盘报告原始日志必须进 Markdown 代码块（v7 已落地，本轮不回退）。
16. **stuck_reports 保留上限**：默认 200 条（`stuck_retention_max` 可配），禁止无限增长。
17. **回归护栏（最重要）**：`search_kb` 收敛后，**无反馈输入时的输出必须与 v7 完全一致**；`check_active_kb` 返回 JSON 形状（`{"id","content"}`）不得变；既有 29 测试的断言不得改。
18. **快照禁止重做**：三层结构、压缩、字符数日志、测试均已落地（§1.2），只允许修 bug，禁止重构。
19. **长跑脚本参数化**：默认 ≤15 分钟冒烟，72h 为人工触发，禁止默认长跑阻塞 CI。
20. **前端新 UI 一律模仿既有模式**：子 Tab 照 `btnRadarSubHistory`/`sessionHistoryList`，卡片照 `btn-insight-copy`/error_warning 卡片，不引入新视觉语言。

## 4. 完成度核对表（执行者逐项填写）

| 任务 | 状态 | commit | 真实测试输出 | 备注 |
|---|---|---|---|---|
| 基线核对（pytest 29 + ruff + node） | | | | |
| P0 卡点雷达（API + 保留策略 + 即时闭环 + 前端 Tab） | | | | |
| P1 检索管道收口（search_kb + 双入口收敛 + 清裸建表） | | | | |
| P2 稳定与分发（stability 脚本 + CI 加固 + RELEASE.md） | | | | |

## 5. 执行节奏

按 `P0 → P1 → P2` 顺序，禁止跳跃并行。每完成一项输出简短进度报告（对照验收标准逐条自检）并 `git commit`；全部完成后：pytest + ruff + node 三绿、更新 `docs/OPTIMIZATION_ROADMAP_2026.md` 顶部状态（追加 v8 落地段落）、在 §4 填完核对表。
