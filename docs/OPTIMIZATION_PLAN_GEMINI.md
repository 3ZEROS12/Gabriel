# Gabriel 优化方案 v4（供 Agent 执行）

> ⚠️ **核对注记（2026-08-07，commit `9c148a0`）**：本文档的 P0（A1/A2/A3）、B1 waiting、C2 本地化、C4 onboarding、D1 parser class 化等项已全部落地；实际完成度以 `docs/OPTIMIZATION_ROADMAP_2026.md` 顶部的"最新核对状态"为准，执行前先读该节，避免重复做功。

> 本文档由一次完整的代码审查 + 竞品调研 + 2026 设计趋势研究得出。执行 Agent（Gemini/Claude Code）应严格按下列顺序推进，每完成一项对照"验收标准"自检，禁止跳跃并行。
>
> 背景文档请先读：
> - `docs/Gabriel_Goal_Spec.md`（P0-P2 基线，本方案是其延续，新项目不得与其中 Non-Goals 冲突）
> - `docs/Agent_Handover_Log.md`（历史交接知识）
> - 权威竞品参考（联网可查）：`claude-view`、`Sidecar(haplab)`、`ccboard`、`Claude-Code-Agent-Monitor`、`agent-advisor`、`Conductor`

---

## 0. 一句话结论（给执行 Agent 的北极星）

**Gabriel 的竞争力不在"监控"，而在"副脑"——它是唯一一个能在不污染主 Agent 上下文的前提下，侧边陪问答 + 记忆历史解决方案并主动提醒的工具。优化必须把所有资源押在"副脑"体验上（P0/P1），监控与视觉是它的外衣（P2/P3），不要本末倒置去复刻 claude-view。**

---

## 1. 竞争力分析（为什么用户会离不开它，以及现在的短板）

### 1.1 已被验证的差异化能力（护城河，必须强化）
| 能力 | 现状 | 竞品情况 | 结论 |
|---|---|---|---|
| 侧边"副脑"问答（不污染主上下文） | Parser 实时注入 Terminal Snapshot，独立 LLM 流式回答，问题/历史与主 CLI 完全隔离 | **所有竞品都只做"观察"，没有一家做"问旁边的大脑"** | 唯一护城河 |
| 个人知识库（FTS5 + 主动推荐） | 日志关键词自动检索历史方案 → toast 主动提示 "已解决类似问题" | claude-view 只做 session 搜索；无人把"我的历史"变成私有知识库 | 独家能力 |
| 多 Agent 原生覆盖 | Antigravity（Gemini CLI 语义）+ Claude Code + Cursor | 竞品几乎全部只盯 Claude Code | 差异点 |

### 1.2 与头部竞品的差距（需补齐，但不能喧宾夺主）
按对我痛点排序：
1. **"等待你输入 / 卡住"检测**（claude-view / conductor 都含）——用户注意力最稀缺，这是监控里最值钱的一条
2. **Context 剩余量预估**（claude-view 的 context gauge）——防止主 Agent 在你看不见时"烧干"上下文
3. **Token / Cost / 会话统计**（ccboard / agent-monitor 标准能力）——现状完全是黑箱
4. **会话历史浏览 / 恢复**（claude-code `--resume`）——现状重启后聊天与雷达全部蒸发
5. **tool / 子 Agent 概要**（agent-advisor 的卡片式）——v1 只要"最近动了哪些文件/工具"，不必全量

### 1.3 视觉/体验现状（从 2026 设计趋势审计）
- 可保留：暗色、低干扰、终端氛围（2026 暗色是基线）
- 需修正：
  - **假遥测图表**继续在后台每秒重绘造假数据（审查已识别，#11 未完成）——必须删或接真实
  - CDN 引用（marked/dompurify/highlight/chart）**与"本地优先"核心承诺矛盾**，且本地已有 `static/vendor/purify.min.js` 却没接上（index.html 仍加载 CDN 版）——漏网之鱼
  - 无设计 tokens（硬编码颜色散落 style.css 与后端内联 style 里）→ 未来所有主题化都会很痛苦
  - 无空态/加载/错误/键盘可达性系统（2026 趋势：认知符合性是基础）

---

## 2. 分阶段优化方案（Agent 严格按序执行）

### P0-A. 强化护城河：让"副脑"值得依赖（本周的 80% 工作量）

**A1. 侧栏问答的"上下文魔法"升级**
- 现状：把整段合并的 `current_contexts` 无差别塞进 Prompt（可能几 MB），既烧费又不聚焦
- 目标：构造"结构性快照"注入
  - 最新最后 60 行 + 统计摘要（文件改动次数 Top5、Error/Exception 行数、最近一次 ToolCall 名称、当前 Agent 状态）
  - 按会话生成不超过 ~3–6K token 的压缩快照；只有用户明确要求"看全文"时才给全文
- 结论：对话响应更准、token 成本直降。给 `src/main.py` 的 `prompt_content` 加一个 `build_snapshot()` 函数
- 验收：
  - [ ] 术语：有专用 `build_snapshot()`，输入为 transcript 原始行 + 元数据，输出结构化快照文本
  - [ ] AI 用户提问"在干嘛" / "有没有错" / "为什么会卡住"时，回答引用到快照中的真实行为细节（人工验证 5 次）
  - [ ] 平均每问消耗增加前相比，快照注入字符数同比下降 >60%（`logger.info` 记录快照长度可用作验证）

**A2. 知识库的"有效性反馈闭环"**
- 当前：推荐后用户必须手动合并/复制，无"这条推荐有没有用"反馈
- 目标：
  - toast 上补 3 个按钮：**`用过/没用/收藏`** → 后端落库 `feedback` 字段
  - 后续推荐按"曾用过且被标记有效 > 用过无效 > 未反馈"排序；被标记无效的条目降权
  - "收藏"条目进入"个人百宝箱"，另开 KB 页签 Tab
- 结论：让 KB 真正"用起来、越用越准"，vs 竞品"只存不读"
- 验收：
  - [ ] toast 上三个反馈按钮可用，点击后数据落 SQLite 新表 `kb_feedback(id, insight_id, action, ts)`
  - [ ] 推荐排序函数读取该表（用过有效权重 1.0、无效 -0.8、未知 0.3）
  - [ ] 自动测试覆盖排序逻辑 >= 3 个用例

**A3. 会话快照的"错误预警卡片"**（护城河补充）
- 目标：tailer 检测到一段连续 Error/Exception/Timeout 时，在对话区顶部推一张**"疑似卡点"卡片**，一键"问 Gabriel 诊断"（把该错误段落喂给 AI）或"左下重建上下文"（旧上下文一般不用管）
- 验收：
  - [ ] 卡片只在同一文件出现连续 ≥5 个含 Error|Exception 的 step 时触发（阈值可配）
  - [ ] "一键诊断"按钮把该段上下文+报错送入副脑并流式返回
  - [ ] 无红色告警糊脸——卡片默认折叠，手动展开

### P1. 补齐"观察"短板（抄最好的，做到 80 分）

**B1. Waiting 检测（重要性第一名）**
- 目标：读 transcript 类型/最后几条消息，判断主 Agent 是否在**等待用户输入/确认/正在被拦截**，前端给该 Agent 卡片叠「需要你」琥珀色高亮 + 标题栏呼吸灯 + 可选桌面通知（点击弹通知需浏览器权限，先给页面内横幅）
- 验收：
  - [ ] 对 Claude Code 的 `awaiting_reason`/`permission` 类和 Antigravity 对应字段有解析（Parser 各自实现 `is_waiting(line)` 默认 False）
  - [ ] 卡片出现琥珀色边框 + 顶部横幅"需要你处理"，3 分钟内回到未等待态由自动恢复
  - [ ] 后端主推 `agent_waiting`/`agent_unblocked` 元素

**P1. context 剩余量 gauge**
- 实现"不完全精确、但有用"的估算：每步统计字/字符数 → 累积 → 进度条(0–100%)，>85% 显示橙色 + 提示"建议重开或 `/compact`"
- 验收：单 Agent 长会话中 bar 单调不降至低于某阶段；>85% 有明确 UI 干预提示

**P1. token / 会话统计页（"账本"）**
- 新增 Settings 里的模型价格配置（input/output 每 M token 单价，自动记忆）
- `/api/stats` 聚合：本次会话轮次、总估价成本、Error 数、工具调用数、平均每次回答 cost
- 对 GPT-4o/deepseek 等价格自动带入；不做完整 token 拆分（粗估即可：字符数 × k）
- 验收：给定固定 transcript 样例，统计结果稳定可复现；页面显示最近 N 会话表

**P1. 会话历史浏览器 + 恢复**
- 复用现有 JSONL 语义：每次 Agent spawn 落一条 `session_meta`（id, 时间, 路径, 名称）到 SQLite
- 雷达页增加"历史会话"子 Tab：按时间倒序，点开可只读回看 transcript 全文（复用现 parsers 渲染）
- 可选（不阻塞）：在只读回看页提供 "用此上下文续聊"→ 重建 `current_contexts` 继续问（简化版 resume）
- 验收：历史列表 >= 历史库；点开回看可用；重启后历史仍在

**P1（可选，锦上添花）。tool 活动条**
- 优先：从 Antigravity `tool_calls.name` / Claude tool_use 提取当前最近执行的工具名，在 Agent 卡片上打小圆标（如 `⚡Call: run_command`），不建全量子树
- 验收：卡片显示最近 1 个工具名，随更新变化

### C0. 基础设施/产品逻辑（成本低收益高）

**C1. 移除假数据图 + 接真实遥测（若保留图）**
- 方案 A（推荐默认）：整图 + Chart.js 引用 + `setInterval` 每周 1s 帧移除，卡面换为"最近 5 个活动时间线"文本
- 方案 B：若保留，用真实数据喂：`steps/分钟`（tailer 已可得到）、Error 事件数、token 估算曲线
- 验收：页面无任何随机数据的每秒重绘；CPU（任务管理器观察）明显下降；移除后无 `Chart` undefined 抛错

**C2. 本地下所有第三方库（落实"本地优先"承诺）**
- 把 `marked`、`highlight.js`、`Chart.js` 下载到 `static/vendor/`（与已有 `purify.min.js` 同目录）
- `index.html` 全部改为 `/static/vendor/xxx`；连同 Google Fonts 一并替换为本机字体栈
- 验收：断开网络后刷新页面，日志 tail、聊天、KB、预览全部正常；无任何受挫痕迹
- 引用：此前安全审查已识别 CDN 被劫持风险——这步从源头解决

**C3. 持久化关键状态**
- 聊天历史（每会话最多保留 40 条）+ KB 草稿 + 当前语言 → SQLite 或 localStorage
- 重启后自动恢复聊天上下文、语言与草稿
- 验收：重启 server 后 chat 历史与上次一致；语言设置不丢

**C4. 首次运行引导（Onboarding）**
- 首次打开（无 config 且无 token）：登录 Modal 上方自动弹 3 步引导：①填 token ②设置 base_url/api_key ③选中目标 Agent
- 侧边栏出现"省略号引导提示"那只有第一次
- 验收：全新浏览器无 localStorage 时打开首页能看到引导滴罩；步进后可点 skip

**C5. 键盘效率 / 快捷指令（符合 2026 交互趋势）**
- 已有 Ctrl+B/K//；补：`1/2/3/4` 快速切 Tab、`Esc` 关闭 toast/banner、`Ctrl+Enter` 发送
- 统一 tooltip（`title`）说明所有快捷键；加 `/help` 画遮罩帮助页

### D0. 视觉与动效（只做"有目的的玻璃"）

**D1. 统一设计 tokens（先行，其余视觉改造都基于它）**
- 在 `style.css` 顶部建立 CSS 变量集群：颜色（语义 5 组）、间距（4/8/12/16/24/32）、圆角（sm/md/lg/full）、阴影、字体
- 后端 parsers 生成的每行内联 `style="color:..."` 全部改为 class（如 `.log-user/ .log-tool/ .log-error`），前端 ALLOWED_ATTR 收回到 `class` 即可，**顺便彻底解决 #6 白名单 style 隐患**
- 验收：`rg -n "style=\"color:" src/main.py` 输出为 0；纯文本通道不依赖 style

**D2. 暗色"玻璃但不糊"**
- 背景：深层黑 + 一个角落渐变光晕（orbs），为 backdrop-blur 提供"可虚化"的素材（2026 关键：纯黑下玻璃无感）
- 卡片：`bg rgba(255,255,255,0.04)` + `backdrop-filter:blur(12px)` + `border 1px rgba(255,255,255,0.1)`（"Light Catcher"）+ 配 `@supports not (backdrop-filter)` 的 90% 不透明回退，保可读性
- 文本对比：一律近白/浅灰，杜绝深色玻璃上的深色字（WCAG AA 底线）
- 动效：transition 150–250ms；`prefers-reduced-motion` 关闭（减视动效）

- D3. 微交互（functional，非装饰）
  - 所有按钮有 hover/focus-visible/active/disabled 完整态
  - 新消息气泡入场 detect 8px + 淡入 120ms；toast 滑动入场
  - 卡片状态色 = 语义（waiting=琥珀/error=红/ok=绿），不只是装饰

- D4. 细节收尾
  - 字体：JetBrains Mono 用于数字/终端内容；Inter 用于 UI（已有，保证 fallback 栈）
  - 消除重复 i18n 缺失（ko 等补全键）
  - 首 URL `?token=` 用后 clean；卸载掉 ws url 上的 token（改为握手换 session ticket，或用 header）→ 避免 token 进 URL 历史与日志

---

## 3. 明确 Non-Goals（本方案不做的）
- ❌ 前端框架迁移（React/Vue）——现有 Vanilla JS 不是瓶颈（复述 Goal_Spec）
- ❌ 桌面封装（Electron/Tauri）——保持 Web 服务
- ❌ 企业级功能（RBAC/多租户/云同步）
- ❌ 完整 token 级计费（专利级 → 价格仅粗估）
- ❌ 一次性做全部作战项——**按序推进，每项带验收再进下一项**

## 4. 技术护栏（执行时强制）
1. 新增/重构代码不违反 Goal_Spec 技术护栏 1–7（后台任务不得隐藏、硬编码禁用、API 都过 token、innerHTML 必净化、Parser 走注册表）
2. 删除假图（C1）时必须同时删 `telemetryChart*` 引用，任何代码在 Chart.js 不可用时不崩
3. 新 CSS 一律走 tokens，`rg` 不得再出现硬编码颜色；后端生成 HTML 的 `style=` 一律替换为 class 语义
4. 所有改动跑通 `python -m unittest discover tests`；`node --check` 通过 script.js

## 5. 执行建议节奏（给 Agent）
先 **P0-A1→A2→A3**，每完成一个对 Goal_Spec 自检并输出小报告；随后 **B0-P1(Waiting)→Context→Stats→History**；再 **C0 清理与持久化**；最后 **D0 视觉**。全部完成后跑一遍全 Guide 验收总表（音频后用 `git log` 记录里程碑节）。