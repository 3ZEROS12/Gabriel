# 🧠 Gabriel 项目持久化长效记忆 (Project Memory)

> ⚠️ **永不删除铁律 (Permanent Retention Guardrail)**:  
> 本文件及 `GEMINI.md`、`CLAUDE.md` 记录了本项目的核心心智模型、开发习惯与架构演进，**在任何 Git 提交、文件整理、清理或重构过程中，绝对禁止删除或清空！**

---

## 👤 用户开发习惯与偏好 (User Preferences & Habits)

1. **桌面工作流习惯**：
   - 用户习惯在 Windows 桌面上为每个独立项目建立专属文件夹（如 `C:\Users\Jason\Desktop\Gabriel`），并直接在该文件夹中启动 `agy` (Antigravity CLI) 或 `claude-code` 进行结对编程。
2. **对话启动指令 (Session Startup Directive)**：
   - 每次在本项目开启**全新对话 / 新 Session** 时，AI 助理必须**主动阅读并遵循当前项目文件夹下的 `MEMORY.md`、`GEMINI.md` 与 `CLAUDE.md`**，无缝继承所有历史经验、开发原则与技术上下文。
3. **沟通与协作风格**：
   - 注重实效，拒绝华而不实的空话，追求极高工效；
   - 深度理解加百列的核心定位，不将加百列误解为 agent 本身或 IDE 插件。

---

## 👼 加百列 (Gabriel) 的核心灵魂与三位一体哲学

```
                👑 人类开发者 (The Creator / 造物主)
                   /                          \
                  /                            \
   ⚔️ 主 Agent · Michael (米迦勒)         🕊️ 副屏 · Gabriel (加百列)
   【斩断乱麻的裁决之剑】                 【手持百合的启示信使】
   在终端战场冲锋、重构、修 Bug             在造物主身旁静默低语、传递智慧与战报
```

* **核心起源**：源自用户用 Gemini 3.1 Pro 备考雅思时的切肤之痛 —— **“主线不打断，支线不迷失”**。
* **生态位**：专为 CLI AI Agent（Antigravity, Claude Code, Cursor, Aider, OpenHands, Gemini CLI）设计的 **1/4 屏幕桌面零侵入 GUI 智慧副屏与战术副脑**。
* **物理隔离**：不代理终端流量，不修改主 Agent 上下文，纯本地增量 Tail `.jsonl` / 日志文件。

---

## 🛠️ 项目里程碑与核心架构状态 (v4.0.0)

1. **质量与测试护栏**：
   - 自动化测试用例：`tests/test_gabriel.py`（**39 项测试 100% 通过**，`pytest tests/ -q`）；
   - 代码规范：`ruff check src tests`（零错误通过）；
   - 前端规范：`node --check static/script.js static/icons.js`（零 CDN，纯本地 vendor）。
2. **已交付的核心能力**：
   - 🟢 **Mini Status 看板**：实时余光态势感知（运行/思考/报错，带状态脉冲灯）；
   - 📑 **智能折叠日志**：`<details class="log-fold">` 收拢超长 Tool Output，遇错自动展开高亮；
   - 📌 **零摩擦报错快照挂载**：一键截取异常，副脑轻量推演，零污染主终端；
   - 📊 **会话终结复盘战报 (`/digest`)**：自动生成 Markdown 战报，一键沉淀经验至本地 `knowledge.db`；
   - 🚢 **多 Agent 舰队标签栏 (`#fleetTabBar`)**：动态聚合多终端 Agent，支持 `⚡ Auto-Follow`；
   - 📐 **灵动胶囊模式 (`Ctrl + M`)**：一键切换 36px 极简桌面药丸形态；
   - 📦 **免安装绿色发布**：`Gabriel-v4.0.0-Windows.zip` (23.32 MB) 已正式发布至 GitHub Releases。
3. **支持的解析器生态 (`ParserRegistry`)**：
   - `AntigravityParser`、`ClaudeCodeParser`、`CursorParser`、`AiderParser`、`OpenHandsParser`、`GeminiCLIParser`、`PlainTextFallbackParser`。

---

## 📌 后续维护注意事项

- 修改 `style.css` 或 `script.js` 后，必须在 `static/index.html` 里将对应的 `?v=` 查询版本号同步递增（防浏览器缓存）；
- 严格遵循 `DESIGN.md` 的视觉规范（Light Indigo，Claude 暖羊皮纸背景 `#faf8f5`，零外部 CDN 引入）；
- 所有新增端点必须经过 Token 鉴权保护。
