# Gabriel 👼 (加百列)

> **CLI AI Agent 的零侵入 GUI 副屏与旁路监视器** —— 零卡顿、零侵入、自带私有大脑。  
> *A zero-intrusion, local-first GUI sidecar for Antigravity, Claude Code, and Cursor.*

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](pyproject.toml)
[![Tests: 34 Passed](https://img.shields.io/badge/Tests-34%20Passed-success.svg)](tests/test_gabriel.py)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-000000.svg)](pyproject.toml)

---

## 💡 开发初衷与起源 (Origin Story)

Gabriel 最初是我在日常使用 CLI AI Agent（如 Antigravity / Claude Code / Cursor）时，为了解决**自己切身体会**而打造的个人工具：

> 💬 **核心痛点**：  
> 每当主 Agent 在终端里执行一项复杂的**长任务**时，我常常产生很多发散性的问题（例如“这行报错是什么原理？”“它现在用的算法是什么？”“帮我解释一下这个库”）。  
> 但是在主终端里我**完全不敢随便打扰它** —— 生怕打断它的执行链路、污染主干记忆，或是让它在主任务中分心做无用功。

**Gabriel 就是为了解决这个问题而诞生的旁路副屏 (Sidecar)。**  
它在后台静默 Tail 日志，提供独立的**副脑问答沙盒**与**实时可视化大屏** —— 让你在主 Agent 默默干活的同时，随时向副屏 Ask / Debug，**完全不占用、不打扰主 Agent 的上下文记忆**，物理级保证绝不阻塞或挂掉主流程。

---

## ✨ 核心亮点

- 🛡️ **零侵入 Tailer (Zero-Intrusion)**  
  基于增量字节偏移监听 Agent Transcript (`.jsonl`) 日志。无 PTY / 无 STDOUT 钩子，主 Agent 就算崩溃也影响不到 Gabriel，Gabriel 崩溃也绝不会打断主 Agent。
- 🧠 **Side-brain 隔离沙盒问答**  
  独立副脑对话框，自带终端上下文快照挂载。随心提问“它现在在干嘛？”“帮我分析这个 Trace”，问答记录持久化在 SQLite 中，完全不占用主 Agent 上下文。
- 🎨 **Light Indigo 极简设计**  
  借鉴 Stripe 的现代美学设计（`DESIGN.md`）：纯净白底 (`#ffffff`) + 藏青文字 (`#0d253d`) + 靛紫 (`#533afd`) 唯一 CTA。**100% 零 CDN 外部依赖**，字体与图标全本地 Vendor，断网也能丝滑使用。
- 🔍 **双重 RRF 混合知识库 (FTS5 + Vector)**  
  `jieba` 中文分词 + `sqlite-vec` 向量语义检索，通过倒数排名融合 (RRF) 算法合并。Agent 报错时主动弹出过去积累的解决方案，并支持优雅离线降级。
- 🛟 **卡点雷达与死循环检测 (Stuck Radar)**  
  滑动窗口识别工具震荡与死循环，一键匹配知识库解决方案；自带保留策略与统计看板。
- 🔌 **Stdio MCP 生态接口**  
  原生内置 Stdio MCP 服务 (`src/mcp_server.py`)，暴露 4 大工具，让 Claude Code / Cursor 直接通过 MCP 调阅和写入 Gabriel 知识库。
- 📦 **免环境绿色发行 (PyInstaller onedir)**  
  支持 Windows 解压即用双击运行，数据目录 (`knowledge.db`) 与代码区隔离，自带单实例锁与端口自动避让。

---

## 🚀 30 秒快速上手

### 1. 安装与启动 (开发模式)

**预备条件：** Python 3.10+

```bash
# 克隆仓库
git clone https://github.com/3ZEROS12/Gabriel.git
cd Gabriel

# 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS / Linux

# 安装依赖
pip install -r requirements.txt
pip install -e .              # 可选：注册 gabriel 全局命令

# 启动服务
gabriel                        # 或 python -m src.main --port 8080
```

### 2. 打开仪表盘
终端启动后会打印随机生成的安全 Token：
```
🔐 Security Token Generated: 8f3a9b2c...
🌐 Gabriel running at http://127.0.0.1:8080
```
在浏览器打开 `http://127.0.0.1:8080` 并粘贴 Token 即可登录！

> 💡 **桌面模式**：运行 `python src/run.py` 可在独立 pywebview 桌面窗口中打开 Gabriel。

---

## 🖥️ 4 大可视化大屏

| 视图 | 核心功能 |
|---|---|
| 💬 **控制中心 (Control Center)** | 分屏视图：Live Agent 终端卡片阵列 + 副脑对话沙盒（支持快照挂载、模型切换、一键 Markdown 复盘导出） |
| 📡 **Agent 雷达 (Agent Radar)** | 全域会话监测：排序/锁定活跃 Agent，实时会话 Token 消耗、成本计算与历史 Turn 复盘 |
| 📖 **私有知识库 (Knowledge Base)** | 图谱式经验卡片 + Markdown 结构化编辑器（支持 `{problem, cause, solution, tags}` 自动解析与注入） |
| ⚙️ **运行配置 (Settings)** | 自定义 OpenAI 兼容 Endpoint、模型预设单价配置、Token 鉴权管理与多语言切换 |

---

## 📡 API & MCP 一览

### REST & WebSocket
所有 REST API 均要求 `X-Gabriel-Token` 请求头，WebSocket 连接推荐采用一次性 Ticket 握手 (`/api/auth/ticket`)。

- `GET /api/health` — Tailer 状态与心跳检查
- `GET /api/agents` — 当前活跃 Agent 会话列表
- `GET /api/kb` · `POST /api/kb` — 知识库 CRUD 与结构化四段写入 (`save_insight()`)
- `POST /api/kb/search` — 基于 RRF 混合检索的只读搜索
- `GET /api/stuck` · `GET /api/stuck/stats` — 卡点报告列表与 24h/7d 统计
- `GET /api/sessions/{id}/transcript?raw=1` — 获取带有文件触及与 Cost 统计的完整 Session 导出数据
- `WS /ws` — 双向日志追加、Waiting/Stuck 状态事件广播与副脑流式响应

### Stdio MCP 4 大工具
运行 `python -m src.mcp_server` 即可作为 Stdio MCP 服务器供 external agents 使用：
- `read_gabriel_kb(query)`：检索私有知识库（含反馈加权）
- `add_gabriel_insight(content)`：主动记录坑点与经验
- `report_agent_stuck(agent, context)`：上报 Agent 卡点并匹配解法
- `get_session_summary(agent_path)`：获取当前会话遥测摘要

---

## 📁 项目结构

```
Gabriel/
├── src/
│   ├── main.py            # FastAPI 后端: REST + WebSocket + 日志 Tailer + FTS5/向量 KB
│   ├── mcp_server.py      # Stdio MCP 服务器
│   └── run.py             # pywebview 桌面包装壳
├── static/
│   ├── index.html         # Dashboard 页面 (4 大视图 + Token 登录)
│   ├── script.js          # 前端交互与 WebSocket 客户端 (DOMPurify 渲染)
│   ├── style.css          # v4 Light Indigo 视觉规范
│   ├── icons.js           # Lucide 图标模块
│   └── vendor/            # 本地 Vendor 字体与库 (零 CDN 依赖)
├── docs/
│   ├── DEVELOPMENT_ROADMAP.md # 【主索引】开发全景图与路线图
│   ├── ARCHITECTURE.md        # 系统架构设计说明
│   ├── API_REFERENCE.md       # API 端点完整参考手册
│   ├── AUTOSTART.md           # Windows 开机自启配置指南
│   └── RELEASE.md             # PyPI / PyInstaller 打包分发指南
├── tests/
│   └── test_gabriel.py    # 34 个 Pytest 自动化测试
├── scripts/               # 开机启动与稳定性冒烟测试脚本
├── requirements.txt       # Python 运行时依赖
├── pyproject.toml         # Ruff & Pytest 工具链配置
└── setup.py               # `pip install -e .` 安装入口
```

---

## 🛠️ 质量验证与护栏

在提交任何代码变动前，需确保以下三项防护全部通过：

```bash
# 1. 运行 Pytest 全量测试 (34 passed)
venv\Scripts\python.exe -m pytest tests/ -q

# 2. 运行 Ruff 代码规范检查
venv\Scripts\python.exe -m ruff check src tests

# 3. 运行 Node 前端语法静态检查
node --check static/script.js static/icons.js
```

---

## 📄 许可证

本项目采用 [AGPL-3.0 开源许可证](LICENSE)。
