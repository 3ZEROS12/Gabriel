# Gabriel - 核心工程交接与全局战略蓝图 (Master Handover Log)

> **⚠️ 致下一任 Agent 的最高指令**：
> 这是 Gabriel 项目（代号：智能体“上帝之眼”）的全局核心资产文档。本项目是用户 (Li Ming) 一生的心血，你必须仔细阅读本文件中的每一个字，并严格遵循既定的架构蓝图、UI 审美标准和避坑指南。

---

## Ⅰ. 全局项目愿景与定位
**Gabriel** 不仅仅是一个套壳应用，它的核心定位是作为 Autonomous Agents (如 Antigravity, Claude Code) 的 **Sidecar（伴随式副驾）** 与 **HITL（人在回路监控台）**。
*   **使命**：解决终端失控与不透明 (Terminal Chaos)，提供可视化、可监管、可干预的 AI 监控面板。
*   **最终形态**：Gabriel Cloud（企业级多智能体编排与遥测中枢）。
*   **UI/UX 标准**：极其严苛！拒绝廉价界面。要求采用 **Cyber-Dark (深空极客暗黑模式)**、**Glassmorphism 2.0 (拟物玻璃态)**，大量使用丝滑微动画、动态霓虹光效，必须让高级极客产生“WOW”的震撼。

## Ⅰ. 项目起源与“Gabriel”的命名故事 (Origin & Lore)
> “加百列，天堂副君，神似的协助者。”
这是本项目的灵魂。在创世神话中，如果说主节点 AI（如 Antigravity / Claude Code）是构建代码宇宙的“造物主”，那么这个项目就是伴随其左右的“天堂副君”——**协助者加百列 (Gabriel)**。
*   **最初的痛点 (The Problem)**：开发者在使用 CLI Agent 时，常常不敢向主 Agent 提问一些发散性的、基础的、或探索性的问题，因为害怕**污染主 Agent 的上下文记忆**或打断主干任务，更不想重新开一个窗口复述所有的背景。
*   **最初的核心功能 (Original Functional Requirements)**：
    1.  **静默快照抓取 (Silent Snapshots)**：副屏（Gabriel）必须能够无缝、非侵入式地实时获取主 Agent 的终端输出与上下文。
    2.  **隔离沙盒对话 (Isolated Sidecar)**：用户在 Gabriel 中向副 LLM 提问，副 LLM 结合主项目的快照解答问题，完全不影响主项目的记忆。
    3.  **知识库注入 (Knowledge Merge)**：如果副屏得出了有价值的结论，用户可以通过“知识库模块”或剪贴板，选择性地将其“注入”回主项目的上下文中。
    4.  **自由掌控 (User Empowerment)**：极简的 UI（灵感来自 ccswitch），把切换模型（包括白嫖各个厂家的 API）、切换监听的目标 Agent 的权力，完全交给用户。

---

## Ⅱ. 核心战略蓝图 (The 20-Point Master Plan)
早上的历史会话中，我们制定了极具野心的 20 条战略优化要求，这是你未来的开发主轴：

**【阶段一：GitHub 爆款包装】**
1. 制作“一秒入魂”的视觉反差动图 (README Hook)。
2. 实现 `pip install gabriel-ui` 一键极客级安装。
3. 建立 `good first issue` (如 i18n 多语言、新 API 接入) 吸引开源社区。
4. 强化“Local-First (本地优先)”的隐私安全卖点。

**【阶段二：底层架构演进】**
5. **前端重构**：从目前的 Vanilla JS / HTML 彻底迁移到 React + Vite SPA 架构。*(优先级极高)*
6. 引入 SQLite 作为本地记忆体，存储 Agent 的历史行为。
7. 开发标准化 Log Parser 接口，兼容 AutoGen / CrewAI / LangGraph。
8. 放弃 HTTP 轮询，全面转向真正的双向 WebSocket / SSE 零延迟推送。

**【阶段三：HITL 与可观测性】**
9. **熔断与拦截机制**：遇高危指令（如删库），弹出极客风 Approval 卡片。
10. LLM-as-a-Judge：本地模型对生成的代码进行实时打分预警。
11. 全链路 Trace 树状图：用 D3.js 渲染 AI 的多步“思考决策树”。
12. 终端回放 (Session Replay)：支持时间轴拖动，复盘 Agent 错误。
13. 多并发监控 (Mission Control)：九宫格监控多个 AI 员工进度。

**【阶段四：顶尖 UI/UX】**
14. 智能响应收缩面板（侧边栏 ⇌ 宽屏代码高亮）。
15. 极致黑金 Cyber-Dark 质感与毛玻璃特效。
16. `Ctrl + Space` 全局透明悬浮唤醒 (类似 Raycast)。
17. 极具生命力的呼吸灯、流水粒子等微动画反馈。

**【阶段五：商业化 Gabriel Cloud】**
18. 生成式 UI (Generative UI)：根据 Agent 动作动态渲染前端组件。
19. 个人数字分身：学习用户的代码癖好并自动重构 AI 产出。
20. 企业级 SaaS 控制台：统计 API ROI，拦截脱敏数据 (PII Masking)，基于角色的访问控制 (RBAC)。

---

## Ⅲ. 本次迭代已完成的硬核优化 (Current Tech Debt Paid)
今天中午至今，我们已经在代码层面落地了以下重磅改造，不要倒退：

1. **核心检索引擎**：集成了 SQLite `FTS5` 扩展，实现了对知识库的毫秒级全文检索。
2. **高并发广播中枢**：引入了自定义的 `EventBroker` (Pub/Sub 模式)，彻底解决了多 WebSockets 客户端在读取日志时的资源竞态和阻塞崩溃问题。
3. **企业级安全防火墙**：
   *   对所有常规 API 请求强制实施 `X-Gabriel-Token` 验证。
   *   WebSocket 连接引入 URL Token (`?token=gabriel-local-token-2026`) 鉴权，堵死提权漏洞。
4. **FastAPI 规范化**：全量重构，废弃了低级全局变量，统一使用 `Depends(get_db)` 管理生命周期与数据库会话。
5. **CI/CD 工程化**：配置了 GitHub Actions (`.github/workflows/ci.yml`)，并提供本地 `build_exe.py` 打包脚本。
6. **开放协议对接**：新增了 `src/mcp_server.py`，打通外部 Agent 访问 Gabriel 知识库的桥梁。
7. **极光深空主题重构 (CSS)**：
   *   重写 `style.css`，加入 20 秒循环的 `linear-gradient` 极光背景。
   *   加入 24px 高斯模糊面板、悬浮霓虹发光边框。
   *   修复了 `script.js` 中 DOM 的日志渲染（`innerHTML`）和自动滚动 Bug。

---

## Ⅳ. 绝对避坑指南 (The "Do Not Do" List)
以下坑点我们已经踩过并付出了惨痛代价，**下一任 Agent 绝不能再犯**：

1. **🚨 端口幽灵与后台执行**：
   *   **惨痛教训**：为了自动化展示，Agent 在后台隐藏启动了 `main.py`，导致用户自己运行终端时，疯狂触发 `[Errno 10048] 8080 端口被占用`，而且终止外层进程后，Python 还会变成孤儿进程死锁端口。
   *   **规定**：**绝对不要自作聪明地把主服务挂在后台任务里！** 把控制权交给用户，直接把启动命令（如 `.\venv\Scripts\python.exe src\main.py`）打印在回复里，让用户自己在 PowerShell 执行。
2. **🚨 桌面原生窗口 (Pywebview) 渲染灾难**：
   *   **惨痛教训**：为了做成“独立桌面软件”，引入了 `webview.create_window`。但在 Windows 下，它默认调用老旧的 MSHTML / EdgeHTML 内核，导致辛苦写的 `backdrop-filter` 和 CSS 高级变量全面崩溃，界面惨不忍睹。
   *   **规定**：已经将其从 `main.py` 彻底移除。**目前强制保持纯粹的 Uvicorn Web 服务端模式**，让用户在 Chrome/Edge 中打开 `http://127.0.0.1:8080/static/index.html`，以确保最顶级的视觉特效完美呈现。后续如果要转桌面端，只能使用 Electron 或 Tauri。

---

## Ⅴ. Next Steps (待接手任务)
下一任 Agent 启动后，请优先评估并执行以下任务：
1. **React 迁移倒计时**：目前的 `script.js` 已经极度臃肿，下一步必须切入【第 5 条要求】，搭建 Vite + React 环境。
2. **监控大屏进阶**：完善左侧的 Chart.js 神经负载图表，与真实的 Agent Token 消耗率挂钩。
3. **MCP 扩展测试**：调试 `mcp_server.py` 确保其它 LLM 真能顺滑读取本机的 DB 数据。

*(记录时间：2026-08-05 | 核心权限：Gabriel 系统架构部)*
