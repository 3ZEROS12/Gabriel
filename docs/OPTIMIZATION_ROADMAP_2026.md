# Gabriel 优化路线图 2026（分析文档 — 供执行，不含代码改动）

> 生成方式：本地代码全量审计（src/main.py 1225 行 / static 前端 2261 行）+ 对照 `docs/OPTIMIZATION_PLAN_GEMINI.md`（v4 方案）完成度核实 + 竞品能力格局。
> ⚠️ 说明：联网深度调研中途按用户要求终止，竞品信息以 v4 方案内嵌调研 + 已知公开能力为准（feature 级），未逐条重新联网核验。涉及具体第三方能力的结论请落地前复核。

---

## ⚠️ 最新核对状态（2026-08-07，核对于 commit `9c148a0` + 本轮优化）

> 本文档第 1 节"尚未完成"清单已大幅过时，以下项已逐行核验为**已落地**，请勿重复排期：

| 原列缺口 | 现状 |
|---|---|
| C1 假遥测图死代码 | ✅ 已删（仅留注释 `Dead code telemetryChart removed in T1`） |
| D1 后端内联 style / parser class | ✅ parser 已输出 `.log-user/.log-agent/.log-tool/.log-entry` 语义 class |
| C3 聊天历史持久化 | ✅ SQLite `chat_history` 表（40 条上限，重启恢复） |
| P1-1 会话历史浏览器 + 恢复 | ✅ 雷达页历史 Tab + `/api/sessions` + 只读回看（含"存在/已删"徽章） |
| A2 收藏"百宝箱"页签 | ✅ KB 页 ⭐ 百宝箱子 Tab（`/api/kb?filter=favorite`） |
| D4 token 泄露面 | ✅ `/api/auth/ticket` 一次性握手已接入（前端优先 ticket，fallback token） |
| A3 错误预警卡片 | ✅ 后端 `error_warning`（≥5 错误 + 60s 冷却）+ 前端卡片（详情折叠 + ⚡ 一键诊断） |
| 价格输入 UI | ✅ Settings 已有 input/output 单价输入 |

**本轮（2026-08-07 第二批）新增落地：**
- `estimate_cost()` 统一成本估算（chars/4 ≈ tokens，70/30 in/out 拆分，价格可配）+ 单测
- waiting 首轮误报修复：状态仅翻转时推送（首次观测为基线，不再误发 `agent_unblocked`）
- Settings 价格档位预设（GPT-4o / DeepSeek / Claude / Gemini，手动改价自动回"自定义"）
- 会话历史列表补"Avg: $X/turn"列
- i18n 全量补齐：6 种语言 × 77 键（ko 此前缺 33 键）
- CI 触发分支 `main` → `master`（此前 CI 从未触发）

**仍然成立、建议下一轮投入（按价值排序）：** P0-1 快照三层"现场/时间线/原始尾部"精细化（当前已有雏形，可加"连续重复 TOOL_RESPONSE 截断"与 KB/waiting 并入头部）、P0-2 KB 样本数加权公式与结构化四段入库、P1-3 系统通知与 3 分钟恢复、P2-2 设计 token 间距/圆角补全 + `prefers-reduced-motion`。

---

## 0. 一句话结论

**Gabriel 的护城河是"副脑 + 私有知识库"，这套 P0 已经做完，别再做重复功。真正没被占住的、值得投入的，是四块：①把副脑快照从"贴日志"升级成"会读现场的结构化快照"；②把知识库从"能搜到"升级成"越用越准的闭环"；③补齐竞品都有的"会话历史/账本/等待提醒"三件观察表stakes（别人有你没有的，才是缺口）；④清掉遗留的假图死代码与 token 泄露面。**

---

## 1. 现状基线（v4 方案完成度核实表）

本地逐条核实后，v4 方案大部分已落地。**以下项已实现，不要在路线图里重复排期：**

| v4 项 | 状态 | 代码定位 |
|---|---|---|
| A1 上下文快照 `build_snapshot()` | ✅ 已实现（基础版） | `src/main.py:758-790` |
| A2 KB 反馈闭环（权重排序） | ✅ 已实现 | 后端权重 `main.py:805-826`；前端 👍/👎/⭐ `script.js:788-790` |
| A3 错误预警卡片（一键诊断） | ✅ 已实现 | `script.js:811-836`，含"详情"折叠 + "⚡ 一键诊断" |
| B1 Waiting 检测（琥珀高亮+横幅） | ✅ 已实现 | `main.py:836-854` 检测；`script.js:739-760` UI |
| Context gauge（>85% 橙色） | ✅ 已实现 | `main.py:914-918` 计算；`script.js:645-668` 渲染 |
| C2 第三方库本地化 | ✅ 完成 | `index.html:9-12` 全 local vendor；无 Google Fonts 外链 |
| C4 首次运行 Onboarding | ✅ 已实现 | `index.html:320-330` |
| KB toast 主动推荐 | ✅ 已实现 | `main.py:930-940` 推送；`script.js:775-810` 渲染 |
| Merge to KB / 注入 KB | ✅ 已实现 | `main.py:1128-1194` |

**尚未完成 / 真正的缺口（本文档的全部内容）：**

| 缺口 | 状态 | 证据 |
|---|---|---|
| C1 假遥测图死代码 | ⚠️ 仍在 | `script.js:1057-1128` `telemetryChart` + 每秒随机数 `setInterval`；页面已无 canvas（不生效但误导） |
| D1 设计 token 化 + 后端内联 style | ❌ | parser 全部吐 `style="color:#..."`（`main.py:521-629`） |
| C3 聊天历史持久化 | ❌ | `chat_history` 内存态，仅留 11 条，重启即失（`main.py:1035,1057`） |
| P1 会话历史浏览器 + 恢复 | ❌ | `/sessions` 端点有（`main.py:448`），前端无 UI |
| P1 成本账本（价格配置/会话级） | ❌ | `/stats` 全局粗估：正则数关键词 + char/4 + 固定 $0.00001/M（`main.py:424-446`） |
| D4 token 泄露面 | ❌ | WS 用 `?token=`（`main.py:997`）；URL `?token=` 未清理（`script.js:155`） |
| A2 收藏"百宝箱"页签 | ❌ | 收藏有按钮无落点 |
| B1 桌面通知 / 3 分钟自动恢复 | ❌ | 仅页面横幅，无系统通知；`agent_unblocked` 每 tick 都发（噪音） |

---

## 2. 分层建议（按价值/成本排序）

### P0 — 副脑护城河再深一档（别人抄不走）

#### P0-1. 副脑快照从"贴日志"→"会读现场"的结构化快照
- **为什么**：现 `build_snapshot()` 只做"最近 60 行原样贴 + 三个统计"，原始日志含大量重复/噪音，token 浪费且 AI 回答靠猜。护城河是"副脑"，副脑的原料就是快照——这是性价比最高的一步。
- **怎么做**：
  1. 快照分三层：`[现场]`（agent 状态: 运行中/等待/报错、最近工具名、最近改动文件 Top5、Error 计数）、`[时间线]`（去重后最近 N 个事件，每事件 ≤1 行）、`[原始尾部]`（用户明确要"全文"才给）。
  2. 行去重/压缩：连续重复的 `TOOL_RESPONSE` 截断到首行；每行截 200 字符。
  3. 把 `check_waiting_status()`、`check_active_kb()` 结果并入快照头部，让 AI 能直接引用"该 agent 正在等输入 / 刚刚命中过历史方案"。
  4. `logger.info` 记录每次快照字符数，用于验收（字符数应显著小于 60 行原文）。
- **验收**：①问"在干嘛/有没有错/为什么卡住"5 次，回答均引用快照真实细节；②快照平均字符数 < 原 60 行 60%；③`rg "build_snapshot" tests/` 有 ≥2 个单测。

#### P0-2. 知识库从"能搜到"→"越用越准 + 收藏有落点"
- **为什么**：反馈权重已埋好（`main.py:805-826`），但①所有条目起始 0.3，投票少时权重不起作用；②收藏没有 UI 落点；③提取是纯关键词 FTS5，无"错误→方案"的结构化。
- **怎么做**：
  1. 收藏落点：Radar 或 KB 页新增"百宝箱"子 Tab，列 `action='favorite'` 的 insights（`/api/kb/favorites` 或复用 `/api/kb` 加 `?filter=favorite`）。
  2. 排序公式改为**反馈样本数加权**：`score = 0.3 + (useful - 0.8*useless + 1.5*favorite) / max(1, 总反馈数)`，投票多的条目权重更可信；`useless` 计数 ≥2 的条目直接降到最后。
  3. 结构化入库（可选进阶）：`merge_kb` 时让 LLM 输出 `问题/原因/方案/标签` 四段，存独立列，FTS 之外再加标签检索。
- **验收**：①给某 insight 投 1 次 useful 后它排到同类前面；②收藏 1 条后百宝箱页签出现并列出；③测试覆盖排序 ≥3 用例（`tests/test_gabriel.py`）。

#### P0-3. 副脑的"差异点问答"（可选，锦上添花）
- 现状：副脑是纯被动（用户问才答）。竞品没有副脑，这是独家；但"主动发现→我替你问"的闭环（error 卡片已有雏形）可以再往前一步：**错误预警卡片上多一个"自动对比：这条错以前遇过吗"**，点开直接给 KB 命中 + 差异诊断。不扩展成常驻自动提问，避免打扰。

### P1 — 补齐观察三件"表stakes"（竞品都有，你没有 = 直接差距）

#### P1-1. 会话历史浏览器 + 恢复（差距最大的一项）
- **为什么**：`/sessions` 与 `session_meta` 已就绪（`main.py:448,891`），但前端雷达页没有历史 Tab——这是 claude-view / ccboard 的标配能力，用户重启后所有上下文蒸发。
- **怎么做**：
  1. Radar 页加"历史会话"子 Tab：倒序列表（agent/时间/路径），点开**只读回看**该 transcript（复用 `ParserRegistry` 渲染）。
  2. 回看页提供"用此上下文续聊"：把该文件塞回 `current_contexts`，副脑即可对旧会话继续问答（简化版 resume，不需要真 `--resume`）。
- **验收**：①历史列表 = session_meta 库；②点开可回看、重启后仍在；③续聊后副脑能回答"刚才那会话最后在干嘛"。

#### P1-2. 成本账本（会话级 + 可配价格）
- **为什么**：`/stats`（`main.py:424-446`）是全局正则粗估（char/4 当 token、固定 1e-5/M），既不真实也不可复现。
- **怎么做**：
  1. Settings 加模型价格（input/output 每 M token 单价，默认带 GPT/deepseek/Claude 档位，记忆到 config.json）。
  2. `/api/stats` 改成**按会话**聚合：每个 `session_meta` 累计该 transcript 的字符/步数/错误/工具，落库 `session_cost` 表；页面显示最近 N 会话表（agent、时长、turns、est 成本）。
  3. 价格只做粗估（字符 × k），明确不拆完整 token（Non-Goal）。
- **验收**：固定 transcript 样例下统计结果可复现（测试）；页面显示会话级成本表。

#### P1-3. 等待提醒的"不打扰"打磨
- **为什么**：检测已通（琥珀边框+横幅），但①`agent_unblocked` 每 tick 都推送（`main.py:951-955`）——无意义流量；②无系统通知；③无"3 分钟自动恢复"逻辑。
- **怎么做**：
  1. 只有状态**发生翻转**时才推 `agent_waiting` / `agent_unblocked`（记录每文件上次状态）。
  2. 系统通知：`Notification` API 权限流，waiting 且用户已授权时弹一次（页面内横幅优先，权限可选）。
  3. 横幅 3 分钟内未处理不重复弹。
- **验收**：日志里 `agent_unblocked` 不再每秒出现；授权后 waiting 弹系统通知 1 次。

### P2 — 基础设施清理（低风险、立刻收益）

#### P2-1. 删假图死代码（C1）
- `script.js:1057-1128` 整段 `telemetryChart` + `chartData` + 每秒随机 `setInterval` + `initChart()` 调用全部删除；确认删除后无 `Chart` 引用报错（页面本就无 canvas，纯死代码）。若日后要真实遥测，用 tailer 已算好的 `context_percent`/error 数喂，不要造假。
- 验收：`rg "telemetryChart|Chart\." static/` 为 0；刷新页面控制台无报错；任务管理器 CPU 无明显下降需求（本就未渲染，删除是清理）。

#### P2-2. 设计 token 化 + 后端内联 style 收编（D1）
- **为什么**：parser 全吐内联 `style="color:#60a5fa..."`（`main.py:521-629`），①主题化痛苦；②DOMPurify 为放行 style 被迫开白名单（历史 #6 隐患）。`style.css` 已有 `:root` 颜色 token（`style.css:1-17`），但缺间距/圆角/阴影/动效开关。
- **怎么做**：
  1. 后端 parser 的每行内联 style 改为语义 class（`.log-user` / `.log-tool` / `.log-error` / `.log-agent`），后端只输出 class。
  2. `style.css` 补全 token：间距（4/8/12/16/24/32）、圆角（sm/md/lg）、阴影、`prefers-reduced-motion`。
  3. 前端 DOMPurify `ALLOWED_ATTR` 收回为 `class`（不再放 style）。
- 验收：`rg 'style="color:' src/main.py` 输出 0；`rg '#[0-9a-fA-F]{3,6}' static/style.css` 除 `:root` 外为 0。

#### P2-3. 聊天历史持久化（C3）
- `chat_history` 现为 ws 处理器内存态、仅 11 条（`main.py:1035,1057`）。落 SQLite `chat_history(agent_path, role, content, ts)`，每会话最多 40 条；重启时按目标 agent 恢复。语言/草稿已走 localStorage，一并确认。
- 验收：重启 server 后聊天记录与上次一致；切 agent 后各自历史隔离。

#### P2-4. token 泄露面收口（D4）
- WS 用 `?token=` 会进 URL/日志（`main.py:997`）；URL `?token=` 用后未清（`script.js:155`）。
- **怎么做**：WS 鉴权改 header（`X-Gabriel-Token`）或一次性握手 ticket；前端读 URL token 后立即 `history.replaceState` 清掉参数。
- 验收：`rg '?token='` 前端为 0；打开含 `?token=` 的 URL 后地址栏参数被清除。

### P3 — 体验收尾（低成本高感知）

- **P3-1 键盘效率**：已有 Ctrl+B/K；补 `1/2/3/4` 切 Tab、`Esc` 关 toast/banner、`Ctrl+Enter` 发送；统一 tooltip + `/help` 遮罩帮助页。
- **P3-2 空态/加载/错误态**：KB 列表"Fetching…"占位、空 agent 网格提示、WS 断线横幅（已有）扩展为可重试。
- **P3-3 动效降级**：body 的 `aurora` 20s 循环动画（`style.css:27-43`）与 waiting-banner `pulse` 加 `@media (prefers-reduced-motion: reduce)` 关闭。
- **P3-4 权限最小化**：`scan_active_agents`（`main.py:277`）扫描范围写死 3 个 agent 目录，符合 README 承诺，无需改；可在 Settings 展示"当前监控目录白名单"增强信任。

---

## 3. 表stakes vs 差异化 对照

| 能力 | 地位 | 依据 |
|---|---|---|
| 会话历史浏览/恢复 | **表stakes**（claude-view/ccboard 标配） | Gabriel 缺失 → 最高优先级缺口 |
| 成本/会话统计 | **表stakes**（ccboard/agent-monitor 标配） | 现为粗估黑箱 |
| Waiting 检测 + 通知 | **表stakes**（conductor/claude-view 都有） | 已做基础版，缺通知与降噪 |
| Context 剩余量 | **表stakes**（claude-view gauge） | 已实现 |
| Tool/文件活动概要 | **表stakes**（agent-advisor 卡片） | 已做 touched_files + tool 圆标雏形 |
| 副脑侧边问答 | **差异化**（无竞品做"问旁边的大脑"） | 独家 → 押注快照质量（P0-1） |
| 私有知识库主动推荐 | **差异化**（无人把历史变知识库） | 独家 → 押注反馈闭环（P0-2） |
| 多 Agent（Antigravity+CC+Cursor） | 差异点 | 已实现 |

**结论**：差异化部分已建成，路线图重心=**把差异化做深（P0）+ 把表stakes 补齐（P1）**，避免在视觉上过度投入（D 系列是外衣，不是护城河）。

---

## 4. 建议执行顺序（给执行 agent）

1. **P2-1 删假图 + P2-4 token 收口**（15 分钟，先清雷）
2. **P0-1 结构化快照**（本周主攻，护城河）
3. **P0-2 知识库闭环 + 百宝箱**（副脑的第二条腿）
4. **P1-1 历史浏览器**（最大表stakes 缺口）
5. **P1-2 账本 / P1-3 等待降噪**（观察三件套收尾）
6. **P2-2 设计 token / P2-3 持久化 / P3 体验**（最后统一做）

每完成一项跑 `python -m unittest discover tests`（venv Python）+ `node --check static/script.js`。

---

## 5. 风险与注意

- 竞品能力为 feature 级判断，未逐条联网复核（调研中途按用户要求终止）；若要对标落地，先抽查 1-2 个竞品 README/演示。
- `session_meta` 表已存在（`main.py:891`），但缺少 duration/成本字段，P1-2 需迁移表结构（用 `ALTER TABLE` 加列，勿重建）。
- 聊天持久化注意脱敏：存储的应为用户问题与副脑回答，不含 transcript 全文。
- 假图删除是纯清理，若追求"有图"，唯一正当来源是 tailer 已产出的真实 `context_percent` 曲线——但推荐不做（表stakes 里没人靠装饰性曲线赢）。
