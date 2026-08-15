# GEMINI.md — Antigravity (AGY) Project Rules & Memory Loader

> 🚀 **新会话启动强制指令 (Session Startup Mandate)**:  
> 每次在本项目文件夹（`Gabriel`）中启动全新对话或新任务时，Antigravity (AGY) 必须**首先阅读并遵循本文件与 `MEMORY.md`**，无缝继承项目的所有心智模型、用户习惯与架构上下文。

---

## 🛡️ 永久记忆保护铁律 (Permanent Memory Protection)

* **绝对禁止删除或清空**：`MEMORY.md`、`GEMINI.md`、`CLAUDE.md` 为本项目的永久长效记忆基石。在执行任何 `git clean`、文件删除、重构或代码收尾时，**绝对不能删除或修改这些记忆文件**。
* **用户核心工作流习惯**：用户习惯在 Windows 桌面上打开项目文件夹并直接启动 `agy` 进行开发。每次进入项目，必须保持对当前项目架构、测试矩阵（39 tests passed）和设计系统（零 CDN / Light Indigo）的绝对忠诚。

---

## 👼 加百列 (Gabriel) 核心定位与原则

1. **非 Agent、非 IDE 插件**：加百列是外部 **1/4 屏幕桌面零侵入 GUI 智慧副屏与战术副脑**，为 CLI AI Agent（Antigravity, Claude Code, Cursor, Aider, OpenHands, Gemini CLI）提供旁路黑匣子监听。
2. **核心哲学**：“主线不打断，支线不迷失” (Keep the Main Flow Unbroken; Never Lose the Details)。
3. **零侵入**：静默 Tail 本地日志文件（`.jsonl`），绝不劫持或污染主终端进程。

---

## 🧪 验证三要素 (每次改动后必须绿灯)

```bash
venv\Scripts\python.exe -m pytest tests/ -q      # 39 tests passed
venv\Scripts\python.exe -m ruff check src tests  # Ruff 零报错
node --check static/script.js static/icons.js   # 前端语法校验通过
```

---

## 📐 前端与设计规范

* **零 CDN**：所有静态依赖必须位于 `static/vendor/`。
* **缓存刷新**：修改 `style.css` 或 `script.js` 后，必须在 `static/index.html` 中同步 bump 对应引用 `?v=`。
* **XSS 防护**：所有动态注入的 HTML 必须经过 `DOMPurify.sanitize` 过滤。
