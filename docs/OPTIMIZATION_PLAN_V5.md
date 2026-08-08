# Gabriel 优化方案 v5（供 Gemini / Agent 执行）

> ⚠️ **【注：本方案已被 `docs/OPTIMIZATION_PLAN_V6.md` 取代归档】**
> 生成时间：2026-08-08。基于对当前代码库（master @ `8815b89`）的逐行审计撰写，所有行号均为生成时刻的真实位置。
> 执行 Agent 请先读本文件全文，再按顺序推进；**每完成一项必须真实落盘、真实跑测试、贴出真实输出**，再进下一项。
>
> 背景文档：`docs/OPTIMIZATION_PLAN_GEMINI.md`（v4，大部分已落地）、`docs/OPTIMIZATION_ROADMAP_2026.md`（顶部有最新核对状态）。

---

## 0. 一句话北极星

**本轮目标：让"私有知识库"真正可用——看得懂中文（jieba）、记得住结构（四段入库）、检索得准（向量+关键词融合），同时补齐工程底子（重试/测试/lint）。监控与视觉不做扩张。**

---

## 1. 前置基线核对（必须先做，防重复做功）

在动手前，逐条确认以下"已知事实"仍然成立，若不成立以实际代码为准并记录：

| 事实 | 位置（生成时刻） |
|---|---|
| `format_transcript` / `_format_transcript_sync` 返回 **3 元组** `(html, last_lines, new_lines)` | `src/main.py:832`；调用方 `:578`、`:1212`、`:1418` 均按 3 元组解包 |
| `SYSTEM_PROMPT` 模块级常量必须保持定义 | `src/main.py:147` |
| 知识库三处写入 `insights_fts` | `/api/kb` POST `:451`、merge_kb `:1553`、inject_insight `:1582` |
| `extract_keywords`（英文正则）→ FTS5 查询 | `:895` → `check_active_kb` `:1034`（`MATCH ?` + 双引号包裹 + `LIMIT 5`） |
| 成本函数链 | `estimate_cost` `:1083`、`extract_token_usage` `:1095`、`token_cost` `:1124` |
| LLM 调用点（需加重试） | chat 流式 `:1469`、merge_kb `:1534`（`get_ai_client` `:163`） |
| `init_schema`（列迁移用 ALTER TABLE try/except 模式） | `:86` |

**基线验证命令（必须全部通过才开工）：**
```bash
venv\Scripts\python.exe -m unittest discover tests -v      # 期望 18/18 OK
node --check static/script.js                              # 期望无输出
```

---

## 2. 任务列表（严格按序，每项验收后才进下一项）

### P0-1 jieba 中文分词检索

**现状问题**：FTS5 默认 unicode61 分词器不切中文（连续中文 = 一个 token）；`extract_keywords`（`main.py:895`）只认英文标识符。知识库里的中文洞察（merge_kb 生成的方案全是中文）**实际搜不到**。

**实施步骤：**

1. `pip install jieba`，加入 `requirements.txt`。
2. 新增 helper（放在 `extract_keywords` 附近）：
   ```python
   def tokenize_for_fts(text: str) -> str:
       """jieba 分词后空格拼接；英文与非词字符原样保留。供 FTS5 入库前调用。"""
       return " ".join(jieba.cut(text))
   ```
3. **三处写入点**（`:451`、`:1553`、`:1582`）内容先过 `tokenize_for_fts` 再入库。
4. **`extract_keywords` 升级**：对中文文本用 `jieba.analyse.extract_tags(clean_text, topK=max_words)`，英文侧保留现有 regex（files/identifiers/errors）作为补充，两者合并去重后再走 STOP_WORDS 与双引号包裹逻辑。
5. **索引重建**（一次性迁移）：
   - `init_schema` 增加 `kb_meta(key TEXT PRIMARY KEY, value TEXT)` 表；
   - 启动时检查 `kb_meta` 的 `schema_version`，若 `< 2`：`DROP TABLE insights_fts` → 按现有 schema 重建 → 从 `insights` 表全量回填（内容过 `tokenize_for_fts`）→ 写 `schema_version=2`。
   - 注意：`insights_fts` 是 FTS5 虚拟表，`DROP` 后重建即可，无数据丢失风险（源数据在 `insights` 表）。
6. **查询侧**：`check_active_kb`（`:1034`）无需改动查询结构（`extract_keywords` 已产出词），但确认查询词对中文有效（用 jieba 分词后的词 OR 连接）。

**验收标准：**
- [ ] 写入中文洞察（如"数据库连接超时 重试")后，`extract_keywords("数据库连接超时了怎么办")` 产出可命中 FTS5 的中文词
- [ ] `tokenize_for_fts("数据库连接失败")` 输出分词后的空格串
- [ ] 单测 ≥ 2：`tokenize_for_fts` 中文分词、`extract_keywords` 中文关键词提取（`tests/test_gabriel.py`）
- [ ] 全量测试 18+N 通过；旧库迁移后旧洞察仍可检索

### P0-2 结构化知识入库（四段 JSON）

**现状**：`merge_kb`（`:1529`）让 LLM 输出整段 Markdown，无结构，无法按"问题/方案"维度检索。

**实施步骤：**

1. `init_schema` 的 ALTER 列表追加：`problem TEXT`、`cause TEXT`、`solution TEXT`、`tags TEXT`（沿用 try/except 模式，`:97` 附近）。
2. 新增解析 helper（放 `redact_secrets` 附近）：
   ```python
   def parse_structured_insight(raw: str) -> dict:
       """从 LLM 输出提取 {problem, cause, solution, tags}。
       依次尝试：```json 代码块 → 直接 json.loads → 正则抓取 JSON 对象。
       全部失败返回空 dict（调用方降级为整段 content）。"""
   ```
3. **merge_kb prompt 改造**（`:1529` 附近）：要求 LLM 输出严格 JSON 对象，字段为 `problem`（问题描述）、`cause`（原因分析）、`solution`（可复制修复代码/步骤）、`tags`（3-5 个检索标签，数组）。prompt 中给出 JSON 示例。**保持纯 prompt + 解析，不要引入 instructor 库**（我们的端点是任意 OpenAI 兼容 provider，instructor 只对部分 provider 生效，且多一个依赖）。
4. **写入改造**：`content` 仍存原 Markdown（向前兼容）；四字段落 `insights` 表新列。解析失败 → 四字段为空，`content` 存整段，**绝不因解析失败丢弃内容**。
5. `/api/kb` 与 `/api/knowledge` 返回四字段；前端 `kbRulesList` 卡片（`static/script.js` 的 fetchKbRules 附近）渲染 `tags` chip（`#标签` 样式，纯文本，走 DOMPurify）。

**验收标准：**
- [ ] 单测 ≥ 3：`parse_structured_insight` 正常 JSON / ```json 包裹 / 非 JSON 三态
- [ ] merge_kb 在 LLM 输出非 JSON 时不丢内容（降级为整段）
- [ ] `/api/kb` 返回含 `problem/cause/solution/tags` 字段
- [ ] 前端 KB 卡片显示标签 chip

### P0-3 tenacity LLM 调用重试

**现状**：`:1469`、`:1534` 两处 `chat.completions.create` 裸调用，网络抖动直接报错弹红。

**实施步骤：**
1. `pip install tenacity`，加入 `requirements.txt`。
2. 提取重试装饰器（放 `get_ai_client` 附近）：
   ```python
   RETRYABLE = (openai.APIConnectionError, openai.APITimeoutError, openai.RateLimitError)
   retry_llm = retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=8),
                     retry=retry_if_exception_type(RETRYABLE),
                     reraise=True)
   ```
3. 两处调用点包 `@retry_llm`（或 `retry_llm(client.chat.completions.create)(...)`）。流式调用同样适用（重试整个 create）。
4. 不重试业务性错误（4xx 认证类），仅重试网络/超时/限流。

**验收标准：**
- [ ] 单测 1：mock client 前两次抛 `APIConnectionError`、第三次成功，断言调用 3 次且结果正确
- [ ] 3 次重试耗尽后原异常正常抛出（前端错误卡片逻辑不变）

### P1 pytest + ruff 工程底子

**实施步骤：**
1. `pip install pytest pytest-asyncio`；`pyproject.toml` 新增：
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   ```
2. 现有 `tests/test_gabriel.py` 是 `unittest.TestCase`，pytest 原生兼容，**不要重写**。验证 `venv\Scripts\python.exe -m pytest tests/ -q` 跑通 18 个测试。
3. `.github/workflows/ci.yml` 的测试步骤从 `python -m unittest discover tests -v` 改为 `python -m pytest tests/ -q`。
4. `pip install ruff`；`pyproject.toml` 增加：
   ```toml
   [tool.ruff]
   line-length = 120
   target-version = "py310"
   [tool.ruff.lint]
   select = ["E9", "F7", "F8", "F401"]   # 先只开语法错误/未定义/未使用导入
   ```
5. `venv\Scripts\python.exe -m ruff check src tests` 修复报出的问题（重点是未使用导入与可能的语法级问题），**禁止大范围风格重构**。
6. README 开发节同步 pytest/ruff 命令。

**验收标准：**
- [ ] `pytest tests/ -q` 全绿（18+ 用例）
- [ ] `ruff check src tests` 0 error
- [ ] CI 的测试 job 使用 pytest

### P2 sqlite-vec 混合检索（可选，仅当前序全部稳定）

**现状**：纯关键词 FTS5。中文同义改写（"连接超时" vs "连不上")命中不了。

**实施步骤：**
1. `pip install sqlite-vec fastembed`，加入 `requirements.txt`。
2. `init_schema` 建向量表（fastembed 默认 `BAAI/bge-small-zh-v1.5`，384 维，中文友好）：
   ```sql
   CREATE VIRTUAL TABLE IF NOT EXISTS insights_vec USING vec0(insight_id INTEGER PRIMARY KEY, embedding FLOAT[384])
   ```
3. 写入 KB 时同步生成 embedding（`fastembed.TextEmbedding` 惰性单例；**模型下载失败/离线 → 跳过向量写入，绝不阻塞主流程**，纯 FTS5 继续工作）。
4. `check_active_kb` 升级：向量 top5 + FTS5 top5 → **RRF 融合**（`score = Σ 1/(k+rank)`，k=60）→ 取最佳。向量不可用时走纯 FTS5 原逻辑。
5. 首次运行提示模型下载（启动日志打印），模型缓存到本地目录。

**验收标准：**
- [ ] 写入两条同义不同词的中文洞察后，语义查询能命中（人工/单测各一次）
- [ ] 模拟模型不可用（patch 下载失败）→ 全流程不报错、KB 写入成功、FTS5 检索正常
- [ ] 单测 ≥ 2：RRF 融合函数、embedding 不可用降级路径

---

## 3. 技术护栏（强制执行，违反即返工）

1. **真实性纪律**：所有改动真实落盘后跑 `venv\Scripts\python.exe -m pytest tests/ -q` 并**贴出真实输出**。禁止在报告中声称"测试通过"而未实际执行——历史上有过未落盘假报告，已造成返工。
2. `format_transcript` 返回 **3 元组**，如改动其形状必须同步全部调用方（`:578`、`:1212`、`:1418`）——上次改 2→3 元组时漏改两处导致 500。
3. `SYSTEM_PROMPT`（`:147`）保持定义，禁止删除或内联回函数——上次"常量化"改完忘了定义常量导致 WS 连接 NameError、测试挂死。
4. 价格配置显式 `0.0` 是合法值，禁止 `cfg.get(k, d) or d` 式兜底（会把 0 变成默认值）。
5. 所有 API 端点继续走 `verify_token`；所有 `innerHTML` 内容过 DOMPurify；后端输出一律 class 语义、禁内联 `style=`。
6. 新增库必须能离线工作或优雅降级（本项目核心承诺是本地优先）。
7. 每完成一项，更新第 4 节完成度核对表（commit hash + 真实测试输出）。

## 4. 完成度核对表（执行者逐项填写）

| 任务 | 状态 | commit | 真实测试输出 | 备注 |
|---|---|---|---|---|
| 基线核对（18/18 + node --check） | | | | |
| P0-1 jieba 中文分词检索 | | | | |
| P0-2 结构化四段入库 | | | | |
| P0-3 tenacity 重试 | | | | |
| P1 pytest + ruff | | | | |
| P2 sqlite-vec 混合检索 | | | | |

## 5. 执行节奏

按 `P0-1 → P0-2 → P0-3 → P1 → P2` 顺序，禁止跳跃并行。每完成一项输出简短进度报告（对照验收标准逐条自检），全部完成后跑一遍全量测试 + `node --check`，更新 README 与 `docs/OPTIMIZATION_ROADMAP_2026.md` 顶部状态，用 `git log` 记录里程碑。
