# Gabriel 开发全景图与路线图 (Master Development Roadmap)

> **文档定位**：本文件为 Gabriel（加百列）项目的全局开发历程、核心架构设计、版本演进以及后续重启开发的唯一索引与路线图指南。

---

## Ⅰ. 项目定位与起源 (Vision & Lore)

### 1. 核心定位
**Gabriel（加百列）** 是 CLI 型 AI Agent（Antigravity / Claude Code / Cursor 等）的**零侵入 GUI 副屏与旁路控制台**。
- **旁路 Tail**：静默监控已知 Agent 轨迹日志（如 `~/.gemini/antigravity-cli/brain/**/logs/transcript.jsonl`），增量字节偏移读取。
- **物理安全**：无 PTY / STDOUT / 终端 Hook，绝不会阻塞或导致主 Agent 崩溃。
- **副脑隔离问答**：允许开发者随时向副屏 Ask/Debug，不占用、污染主 Agent 的上下文记忆。
- **私有知识库注入**：将副脑调试得出的经验 / 踩坑点，一键结构化存入知识库，并可通过 MCP / 剪贴板注入会话。

### 2. 命名由来
> “加百列，天堂副君，神似的协助者。”  
如果主 CLI Agent 是构建代码宇宙的“主执行器”，Gabriel 就是伴随其左右的“旁路监视与副大脑”。

---

## Ⅱ. 演进历程与版本里程碑 (Development Trajectory)

Gabriel 经历了从简单日志 Tail 界面，到具备双重 RRF 知识库、MCP 工具链、桌面免环境发行版以及 Stripe 风格视觉的完整演进：

```mermaid
flowchart TD
    V1_3["v1.0 - v3.0<br/>基础架构落地<br/>FastAPI + WebSocket Tailer"] --> V4["v4.0<br/>设计与打包重塑<br/>Light Indigo + PyInstaller onedir 免环境包"]
    V4 --> V5["v5.0<br/>安全与持久化<br/>Ticket 鉴权 + Chat SQLite + Zero CDN"]
    V5 --> V6["v6.0<br/>私有知识库<br/>sqlite-vec + jieba FTS5 RRF 融合 + 4段 Insights"]
    V6 --> V7["v7.0<br/>生态与防震荡<br/>Stdio MCP 4工具 + 工具死循环检测 + Session 复盘导出"]
    V7 --> V8["v8.0<br/>卡点雷达与高可靠<br/>Stuck Radar + 统一 search_kb + 34 单测 100% 绿 Pass"]
```

### 详细版本履历

#### 1. v1.0 ~ v3.0 (基础架构构建)
- 建立基于 FastAPI 的 REST + WebSocket 日志广播服务。
- 智能识别 Antigravity / Claude Code / Cursor 的 `transcript.jsonl` 日志结构。
- 提供多卡片并行监控与静态文件服务。

#### 2. v4.0 (设计重塑与 Windows 免环境打包发行)
- **浅色单主题（Stripe 精致感）**：基于 [`DESIGN.md`](file:///C:/Users/Jason/Desktop/Gabriel/DESIGN.md) 实现纯净白底 (`#ffffff`) + 藏青 (`#0d253d`) + 靛紫 (`#533afd`) 唯一 CTA 视觉规范。
- **PyInstaller 免环境发行**：使用 `PyInstaller Gabriel.spec` 打包为 `onedir` 绿色包 (`Gabriel-v4.0.0-win64.zip` ~113MB)。
- **数据/代码分离**：解压运行模式下 `DATA_DIR` 自动落入 exe 同级目录，static 资源打包于 `_MEIPASS`。
- **单实例锁与端口自适应**：`.gabriel.lock` 单实例保护，8080 端口被占自动递增重试。

#### 3. v5.0 (安全与持久化增强)
- **鉴权安全收拢**：所有 `/api/*` 端点基于 `X-Gabriel-Token` 验证；引入 `/api/auth/ticket` 一次性 Ticket 握手，避免 WebSocket URL 泄露 Token。
- **Side-brain 聊天持久化**：建立 SQLite `chat_history` 表，单 Agent 保留 40 轮问答，服务重启不丢失。
- **零 CDN 纯离线**：字体（Inter 300/400/500, JetBrains Mono 400/600 woff2）、Icons (Lucide SVG)、JS 库（marked, DOMPurify, highlight.js）全量 Vendor 进 `static/vendor/`。

#### 4. v6.0 (混合检索与 4 段结构化知识库)
- **向量 + 全文 RRF 混合检索**：结合 `sqlite-vec` + `fastembed` (`BAAI/bge-small-zh-v1.5`) 向量语义检索与 `jieba` 中文分词 FTS5 全文检索，采用倒数排名融合 (RRF) 算法。
- **优雅降级**：模型 / 向量库不可用时静默回退纯 FTS5 模式。
- **4 段结构化 Insight**：输入输出统一结构化为 `{problem, cause, solution, tags}`，支持 Tag Chips 渲染。
- **Tenacity 重试**：API 连接与大模型请求配置指数退避重试（防御 429/500/Timeout）。
- **标准测试集**：引入 `pytest` 单元测试与 `ruff` 代码检查。

#### 5. v7.0 (MCP 工具链与死循环检测)
- **Stdio MCP 服务**：[`src/mcp_server.py`](file:///C:/Users/Jason/Desktop/Gabriel/src/mcp_server.py) 提供 `read_gabriel_kb` / `add_gabriel_insight` / `report_agent_stuck` / `get_session_summary` 4 大工具。
- **工具死循环/震荡检测**：通过滑动窗口算法识别频繁调用的重复工具签名，自动触发预警。
- **统一写入入口**：收敛所有 KB 写入方法为单一函数 `save_insight()`。
- **Session 复盘 Markdown 导出**：支持导出包含 Character/Token 统计、触及文件列表及完整日志的 Markdown 报告。

#### 6. v8.0 (卡点雷达、统一检索管道与稳定性验收)
- **卡点雷达 (Stuck Radar)**：建立 `stuck_reports` 表，配合 MCP 自动抓取 Agent 报错并提供 KB 一键解法匹配。
- **统一检索管道**：收敛所有 KB 查询为单一函数 `search_kb()`，统一反馈重排逻辑。
- **自动化稳定性与断言**：提供 `scripts/stability_run.py` 进行长跑内存泄漏断言。
- **全量测试与规范 100% 绿灯**：34/34 pytest 单元测试通过，`ruff check` 0 警告，前端 JS `node --check` 语法纯净。

---

## Ⅲ. 核心架构与工程守则 (Architecture & Guardrails)

### 1. 代码库结构
```
Gabriel/
├── src/
│   ├── main.py            # FastAPI 后端: REST API + WebSocket + 日志 Tailer + FTS5/向量 KB
│   ├── mcp_server.py      # Stdio MCP 服务 (供 External Agent 调用)
│   └── run.py             # pywebview 桌面包装壳
├── static/
│   ├── index.html         # Dashboard 页面 (4 大视图 + Token 登录)
│   ├── script.js          # 前端交互逻辑
│   ├── style.css          # v4 Light Indigo 样式系统
│   ├── icons.js           # Lucide 图标模块
│   └── vendor/            # 本地 Vendor 字体与 JS 依赖 (零 CDN)
├── docs/
│   ├── ARCHITECTURE.md    # 系统架构设计
│   ├── API_REFERENCE.md   # API 端点参考
│   ├── AUTOSTART.md       # Windows 开机自启配置
│   ├── RELEASE.md         # 打包发布指南
│   ├── LICENSE_RATIONALE.md # GPL 许可证说明
│   └── DEVELOPMENT_ROADMAP.md # 本文件 (全景开发路线图)
└── tests/
    └── test_gabriel.py    # Pytest 自动化测试集
```

### 2. 绝对不可逾越的开发守则
1. **零 CDN 依赖**：绝不从外部 CDN 动态加载 CSS/JS/字体，保证 100% 离线可用。
2. **颜色 Token 规范**：十六进制颜色值只能存在于 `style.css` 的 `:root` 与 `.log-*` 映射区；HTML/JS 严禁内联 style 硬编码颜色。
3. **KB 写入与检索单一入口**：写入强制走 `save_insight()`，检索强制走 `search_kb()`，禁止手写平行 SQL 逻辑。
4. **离线降级策略**：向量库缺失或 LLM 连接失败时必须无缝平滑降级至本地 FTS5，严禁抛错阻塞主流程。
5. **变动必须通过验证**：修改后必须确保 `pytest tests/` (34 个测试)、`ruff check` 和 `node --check` 全绿。

---

## Ⅳ. 后续重启开发路线图 (Future Roadmap When Resuming)

如果未来恢复 Gabriel 的开发，建议按以下优先级逐步推进：

### 阶段 1：精细化遥测与快照增强 (P0)
- **三层上下文快照优化**：将 Ask Side-brain 时的上下文抓取升级为“现场状态 + 关键时间线 + 增量日志尾部”，自动对连续重复的 `TOOL_RESPONSE` 进行压缩截断。
- **KB 权重动态衰减**：在 `kb_feedback` 的基础上引入时间衰减与样本数加权公式，让最近且验证有效的解法排序更高。

### 阶段 2：系统级体验与多 Agent 编排 (P1)
- **OS 原生托盘与系统通知**：支持 Windows 系统托盘驻留，当 Agent 处于长等待 (Waiting) 或反复卡点 (Stuck) 时触发系统级 Notify 弹窗。
- **多并发 Agent Dashboard**：进一步强化 Grid 视图，支持按任务标签筛选多 Agent 会话，并实时展示 Token / Cost 消耗曲线。

### 阶段 3：前端工程化与跨平台打包 (P2)
- **前端组件化评估**：当 Vanilla JS 控制规模进一步扩大时，可评估将 `script.js` 拆分为 ES Module 或迁移至 Vite + React 架构。
- **跨平台 CI 发行**：配置 GitHub Actions 构建 Linux AppImage 与 macOS DMG 发行包。

---

*(文档整理时间：2026-08-11 | 校验状态：代码库 34/34 测试通过)*
