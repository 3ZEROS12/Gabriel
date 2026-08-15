# 🚀 Gabriel (加百列) 开源宣发冷启动物料包 (Launch Kit)

本物料包为 **Gabriel 零侵入智慧副屏** 的全渠道冷启动宣发指南，包含经过转化率优化的中英文社区发帖模板、10秒分屏动图录制分镜脚本，以及发布流程指引。

---

## 目录
1. [10 秒爆款演示 GIF 录制分镜脚本 (Storyboard)](#1-10-秒爆款演示-gif-录制分镜脚本)
2. [V2EX「分享创造」发帖文案（中文精修）](#2-v2ex分享创造发帖文案)
3. [Reddit (r/ClaudeAI & r/LocalLLaMA) 发布文案（英文）](#3-reddit-发布文案)
4. [Hacker News (Show HN) 发布文案（英文）](#4-hacker-news-show-hn-发布文案)
5. [Twitter / X 爆款线程文案 (Thread)](#5-twitter--x-发布线程)
6. [GitHub Release 绿色免安装版发布指引](#6-github-release-绿色版发布指引)

---

## 1. 10 秒爆款演示 GIF 录制分镜脚本

> **核心原则**：3 秒内抓住眼球，展示“终端 Agent 在狂跑，右侧副屏零干扰拆解报错 + 战报复盘”。

| 时间 | 屏幕左侧（主终端） | 屏幕右侧（加百列副屏） | 画面看点 |
| :--- | :--- | :--- | :--- |
| **0~3s** | Claude Code / Antigravity 正在长任务执行中，终端突然爆出红字报错（如 `ConnectionResetError`）。 | 加百列顶部 Mini Status 栏瞬间亮起 `🔴 [Claude] 捕获异常: ConnectionReset...`。 | **零侵入感知**：副屏自动抓取，无需切屏复制粘贴。 |
| **4~6s** | 终端主流程保持挂起等待。 | 鼠标点击副屏上的 **`📌 引用最新报错`**，报错快照瞬间挂载至输入框，副脑立即给出精准修复建议。 | **零摩擦推演**：不需要污染主 Agent 的 Context。 |
| **7~10s** | 任务顺利完成退出。 | 用户敲入 **`/digest`**，副屏瞬间弹出高质感 **《会话复盘战报与 Token 账单》**，点击“一键沉淀经验至知识库”。 | **战果落地**：不仅是监控，更是私有工程大脑。 |

* **推荐录屏工具**：ScreenToGif (Windows) 或 OBS 导出为 60fps MP4 后转为高品质 GIF（建议压至 5MB 以内放至 README 顶部）。

---

## 2. V2EX「分享创造」发帖文案

* **发帖节点**：`分享创造` (Creative) 或 `程序员` (Programmer)
* **标题建议**：《因为用 Claude Code / Antigravity 跑长任务不敢插话，我手搓了一个桌面零侵入副屏 Gabriel》

```markdown
大家好，我是独立开发者。最近几个月重度使用 Claude Code、Antigravity、Cursor 和 Aider 跑各种自动化编码任务，但日常使用中一直有几个非常折磨人的痛点：

1. **长任务不敢插话**：Agent 在终端里跑一个 15 分钟的重构任务，我想中途查个逻辑或者问个旁支问题，根本不敢打断，更怕插话污染它宝贵的 Context Window。
2. **终端日志刷屏如瀑布**：几百行 Tool Call 呼啸而过，一旦报错想翻回去看上下文极度痛苦。
3. **跑完就忘，经验无法沉淀**：任务跑完了，改了 8 个文件、踩了 3 个坑、花了几十万 Token，没有任何结构化复盘。

为了解决自己每天的这些痛点，我手搓了 **Gabriel (加百列)** —— 一个专为 CLI AI Agents 设计的 **1/4 屏幕桌面零侵入 GUI 副屏与战术副脑**。

### 🌟 核心特性：
- 🔍 **零侵入黑匣子旁路监听**：无须配置 Agent 插件，本地静默 Tail `.jsonl` / 日志，支持 Antigravity、Claude Code、Cursor、Aider、OpenHands 等；
- 🟢 **极简状态看板与折叠日志**：余光一瞥即知 Agent 当前状态（运行/卡住/报错），超长 Tool Output 自动折叠；
- 📌 **一键快照投喂副脑**：遇到报错点击「引用最新报错」，用轻量模型（如 DeepSeek/GPT-4o-mini）独立推演方案，绝不污染主 Agent 终端；
- 📊 **会话终结复盘战报 (`/digest`)**：一键生成本次任务的目标、耗时、Token 账单与文件变动清单，并支持一键将踩坑经验沉淀进本地 SQLite 向量知识库；
- 📐 **灵动胶囊模式 (`Ctrl+M`)**：平时缩为屏幕边缘 36px 小药丸，不遮挡 IDE。

- 💻 **开源地址**：https://github.com/3ZEROS12/Gabriel
- 📦 **开箱即用**：支持 Windows 绿色免安装版（解压双击直接运行，无需配 Python 环境）。

全部代码开源，纯本地零 CDN，欢迎大家体验、吐槽和提 Issue！如果觉得对你的 CLI Agent 工作流有帮助，求个 Star 鼓励一下！⭐️
```

---

## 3. Reddit 发布文案

* **目标 Subreddits**：`r/ClaudeAI`, `r/LocalLLaMA`, `r/ChatGPTCoding`, `r/Cursor`
* **Post Title**: *I built a zero-intrusion desktop GUI sidecar for CLI AI Agents (Claude Code, Antigravity, Aider) so you don't ruin context windows while asking side questions.*

```markdown
Hey everyone!

Like many of you, I've been heavily using CLI AI agents (Claude Code, Antigravity, Aider, Cursor CLI) for daily engineering tasks. However, I kept running into the same friction points:

1. **Context Anxiety**: When a CLI agent is running a long multi-step task (10-20 min), I often have side questions or want to investigate an error. Interrupting the CLI or injecting side prompts pollutes the main agent's context and wastes expensive tokens.
2. **Terminal Log Overwhelm**: Long tool outputs flood the terminal, making it tedious to spot errors or track turn-by-turn progress.
3. **No Post-Mortem Retention**: Once a CLI session terminates, all the debugging lessons, touched files, and token usage vanish.

To solve this, I created **Gabriel** — a lightweight, zero-intrusion desktop GUI sidecar (1/4 screen or floating mini capsule) designed as a companion for CLI AI agents.

### Key Highlights:
- 🚀 **Zero Intrusion**: It doesn't modify or proxy your CLI tools. It silently tails the local trajectory logs (`.jsonl`) in the background.
- 📌 **Zero-Friction Context Pinning**: Catch an error? Click "Pin Last Error" to snapshot the trace and brainstorm solutions in Gabriel using your own auxiliary model without touching the main terminal.
- 📊 **Session Digest (`/digest`)**: Generates an instant post-mortem markdown report summarizing task outcomes, tools called, token breakdown, and lets you save bug fixes directly into a local hybrid-search Knowledge Base.
- 📐 **Mini Pill Mode (`Ctrl + M`)**: Shrinks into a 36px sleek capsule on your screen when you need pure code focus.
- 🛡️ **Zero CDN, 100% Local & Privacy-focused**: Runs locally with SQLite FTS5 + sqlite-vec RRF search.

🔗 **GitHub Repo**: https://github.com/3ZEROS12/Gabriel

Would love to hear your thoughts, feature requests, and feedback!
```

---

## 4. Hacker News (Show HN) 发布文案

* **Title**: `Show HN: Gabriel – A zero-intrusion desktop GUI sidecar for CLI AI agents`
* **URL**: `https://github.com/3ZEROS12/Gabriel`

```text
Hi HN,

I built Gabriel to solve a specific pain point when working with CLI AI coding agents (Claude Code, Antigravity, Cursor, Aider).

When CLI agents execute long, multi-turn reasoning loops, developers often need glanceable situational awareness and a separate sandbox to query errors without interrupting or bloating the primary agent's context window.

Gabriel runs as a distraction-free desktop sidecar window that:
1. Passively tails agent trajectory `.jsonl` files (zero intrusion / no IDE extension lock-in).
2. Auto-folds verbose tool calls and highlights error traces with smart collapsible details.
3. Lets you snapshot terminal errors into a secondary brain to investigate root causes in parallel.
4. Generates structured post-session war reports (`/digest`) and saves reusable engineering insights into a local vector/FTS5 knowledge base.

It's written in Python (FastAPI/PyWebview) and Vanilla JS/CSS (zero CDN, strict CSP).

GitHub: https://github.com/3ZEROS12/Gabriel

Feedback and critiques are very welcome!
```

---

## 5. Twitter / X 发布线程

* **Tweet 1 (Hook + Video/GIF)**:
  > Tired of interrupting your CLI Agent (Claude Code / Antigravity / Aider) just to investigate an error or ask side questions?
  > 
  > I built **Gabriel**: a zero-intrusion desktop GUI sidecar that watches your terminal logs silently & provides a secondary brain.
  > 
  > 🧵👇 [Attach 10s Demo GIF]

* **Tweet 2 (Core Features)**:
  > What Gabriel does:
  > 🟢 Mini status banner & auto-collapsible tool logs (glanceable cockpit)
  > 📌 One-click error snapshot pinning to investigate without polluting main context
  > 📊 `/digest` for instant post-session war reports & token costs
  > 📐 `Ctrl+M` mini capsule mode

* **Tweet 3 (Links & Open Source)**:
  > 100% Local, Zero CDN, supports OpenAI/Claude/DeepSeek/Ollama.
  > 
  > Star & try it on GitHub:
  > 👉 https://github.com/3ZEROS12/Gabriel
  > 
  > #ClaudeCode #AIAgent #OpenSource #DeveloperTools #Cursor
```

---

## 6. GitHub Release 绿色版发布指引

打包免安装版可极大降低试用门槛：

```bash
# 1. 激活虚拟环境并安装打包依赖
venv\Scripts\activate
pip install pyinstaller

# 2. 生成单文件夹绿色分发包
pyinstaller --noconfirm --onedir --windowed \
  --add-data "static;static" \
  --name "Gabriel-v4.0.0-Windows" \
  src/run.py

# 3. 将 dist/Gabriel-v4.0.0-Windows 压缩为 zip 上传至 GitHub Releases
```
