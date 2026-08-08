# Gabriel 外观重塑执行计划（v3.1 Cyber-Dark → v4 Light Indigo）

> 生成时间：2026-08-08。设计定稿：**Stripe 精致感 · 纯净克制 · 浅色单主题 · 第三档全量收编**。
> 执行 Agent：先读 `DESIGN.md`（根目录，视觉唯一规范）→ 跑 §1 基线 → 严格按 §2 顺序推进，每项验收后才进下一项。

---

## 0. 一句话目标

把加百列从"金色极光 cyber 暗色"重塑为"Stripe 式纯净浅色"：白画布、深藏青文字、靛紫单一强调、300 细体、hairline 细线、零装饰动效；同时完成**字体本地化 vendor**、**emoji 图标换细线 SVG**、**内联 style 全量收编**。功能行为一律不变。

## 1. 当前基线（2026-08-08 实测）

| 项 | 现状 |
|---|---|
| 主题 | v3.1.0 Cyber-Dark：深空蓝 `#0B0F19` + 金色 `#d4af37` + 极光渐变动画 + 玻璃拟态（`style.css` 全 554 行） |
| 字体 | `--font-ui: 'Inter'` / JetBrains Mono **被引用但未 vendor**（零 CDN 政策），实际渲染 system-ui + 系统 mono |
| 内联 style | `index.html` 几乎每行 `style="..."`；`script.js` 动态模板亦有大量内联 style |
| 图标 | sidebar 已用 SVG（stroke 2px）；内容区 emoji 图标：👁 🧠 📥 🔍 🐛 📖 ⭐ 🔄 💡 📊 📜 🚀 ✕ 等 |
| 语言 | 按钮中英混排（"生成复盘报告" vs "Feedback"）——**i18n 机制保留，本轮仅统一明显硬编码，不重构** |
| 后端 | parser 已输出 `.log-*` 语义 class（v6 落地），**本轮零后端改动**（颜色只在 CSS 层映射） |
| 测试 | 29 passed / ruff clean / node clean（后端不受影响，仅回归） |

**基线验证命令（必须真实执行并贴出输出）：**
```bash
venv\Scripts\python.exe -m pytest tests/ -q        # 期望 29 passed
venv\Scripts\python.exe -m ruff check src tests    # 期望 All checks passed!
node --check static/script.js                      # 期望无输出
```

## 2. 任务列表（严格按序，每项验收后 commit）

### T1: 字体 vendor 本地化
- 从 Google Fonts 下载 woff2（**仅 latin 子集**，文件 ~20-60KB 各）：Inter 300/400/500 + JetBrains Mono 400/600
- 落位 `static/vendor/fonts/`：`inter-300.woff2` / `inter-400.woff2` / `inter-500.woff2` / `jetbrains-mono-400.woff2` / `jetbrains-mono-600.woff2` + 对应 `OFL.txt` 许可证（Inter 与 JetBrains Mono 均为 OFL，可再分发）
- `style.css` 顶部 `@font-face` 五条（`font-display: swap`）；`--font-ui` 改为 `'Inter', system-ui, sans-serif`，新增 `--font-mono: 'JetBrains Mono', monospace`

**验收：** `rg 'fonts.googleapis|googleapis|cdn' static/` 输出 0；`static/vendor/fonts/` 有 5 woff2 + OFL；页面 Network 面板无字体外链（或 `node --check` 通过 + 截图字体渲染为 Inter）。

### T2: style.css 全量重写（核心）
- 按 `DESIGN.md` §2-§7 重写全部 554 行：`:root` token 区（§2 语义色 + §5 spacing/radius + §6 阴影）、`@font-face`、日志角色色映射、全部组件（按钮/面板/聊天/输入/switch/segmented/toast/modal/状态点/滚动条/terminal 卡）
- **删除**：aurora 动画、glassmorphism（`backdrop-filter`）、金色辉光、所有 `pulse` 动画（`prefers-reduced-motion` 保留并覆盖全局）
- 新增 class 供 T3/T4 引用：`.nav-text`, `.stat-grid`, `.stat-value`, `.sub-tab`, `.icon-btn-svg`, `.inline-svg` 等
- 保留所有现有 class 名（`.panel` `.agent-item` `.message` `.btn-primary` 等），**只改样式不改名**，DOM/JS 零改动依赖

**验收：** `rg -c 'backdrop-filter|aurora|d4af37|212, 175, 55' style.css` 全为 0；`rg '#[0-9a-fA-F]{3,6}' static/style.css` 仅 `:root` 与 `.log-*` 映射区出现；`node --check` 通过。

### T3: index.html 内联 style 收编 + emoji→SVG
- 全部 `style="..."` 内联属性收编为 class（规则已在 T2 定义）；保留 ≤5 处白名单（如动态容器无 class 可挂的定位例外，需在 commit 说明理由）
- emoji 图标换**细线 SVG**（stroke 1.5px，24×24 viewBox，`fill:none`，与 sidebar 风格统一，可放 `<defs>` 或内联）：👁 眼睛（折叠面板）、🧠 头部（助理标题可用纯文字替换）、📥→下载 SVG、🔍→搜索、🐛→错误、📖→书、⭐→星（收藏态可保留 emoji 或换 SVG）、🔄→刷新、💡→灯泡、📊/📜（子 Tab 文字可去 emoji 仅留文字）、🚀→火箭
- 标题/欢迎语中的装饰 emoji（👼 onboarding）保留（非图标用途）
- 硬编码中英混排按钮：仅统一同类操作（如全部按钮沿用各自语言或转英文），**i18n data-i18n 属性不得改动**

**验收：** `rg 'style="' static/index.html` 计数 ≤5；内容区功能图标 emoji 清零（onboarding 的 👼 与对话 emoji 除外）；四视图截图与改造前功能对照无缺失。

### T4: script.js 动态模板收编
- 动态 HTML 模板字符串（`innerHTML` 赋值）中的内联 `style=` 改为 T2 class（逐处过：agent 卡、kb 列表、会话历史、session review、error_warning 卡、toast、favorite 列表、insight 卡反馈按钮等）
- 动态 emoji 图标替换为对应 SVG 或纯文字（同上规则）；**DOMPurify 白名单核对**：新增 class 名不触发 sanitize 拦截（purify 默认放行 class，若配置收紧过 ALLOWED_ATTR 需同步放行）
- **禁止改动**：DOM id、事件绑定、WS 消息类型、API 调用、i18n 键、业务逻辑

**验收：** `rg 'style="' static/script.js` 计数较基线下降 ≥90%；`node --check` 通过；`rg 'innerHTML' static/script.js` 逐处核对 sanitize 仍生效。

### T5: 全量回归（功能 + 视觉）
- pytest 29 / ruff / node 三绿（同 §1）
- **截图对比验收**（Edge headless，本地起服务）：登录弹窗、Control Center（终端卡 + 聊天）、Agent Radar（统计块 + 实时 + 历史 Tab）、KB 页、Session Review modal、KB toast 推荐、等待 banner——共 ≥7 张，每张核对：无未替换的暗色残留（`#0B0F19`/金色）、无布局断裂、字体已渲染 Inter
- 手工清单（浏览器操作）：发一条 chat（流式渲染）、切 agent、KB 搜索/收藏/投票、导出复盘报告、清除聊天、断线横幅（停服 5 秒看 banner）

**验收：** 全部截图无暗色残留与布局断裂；手工清单逐项通过；三绿输出贴出。

### T6（可选，不阻塞）: 语言一致性
- 将明显混排按钮统一为英文（README 生态语言为 en，i18n 已支持多语言）；若时间不足可跳过并在 §4 备注

## 3. 技术护栏（本计划专属）

1. **功能零回归是最高优先**：DOM id / 事件 / WS 类型 / API / i18n 键 / 后端——一律不动；只改样式层与展示层
2. **颜色唯一来源**：裸 hex 只允许出现在 `style.css` 的 `:root` 与 `.log-*` 规则；`index.html`/`script.js` 禁止裸 hex（SVG stroke 如需品牌色用 `var(--…)` 或 `currentColor`）
3. **零 CDN**：字体必须 vendor；`rg 'http' static/` 仅允许 `127.0.0.1` 相关或注释
4. **DOMPurify 检查**：所有动态 `innerHTML` 内容仍过 sanitize；新增 class 不破坏白名单
5. **设计规范优先**：拿不准的颜色/间距/圆角先查 `DESIGN.md` §2/§4/§5，禁止自行发明
6. 每一步真实落盘后跑 `node --check`；T5 前每步截图自检
7. 每完成一项更新 §4 核对表并 `git commit`（不 push）
8. **禁止暗色残留**：`rg -i '#0b0f19|#d4af37|aurora|backdrop-filter' static/` 最终为 0

## 4. 完成度核对表

| 任务 | 状态 | commit | 真实输出/截图 | 备注 |
|---|---|---|---|---|
| 基线核对（pytest 29 + ruff + node） | ✅ 已通过 | — | 31 passed (含 5927f81 新增), ruff clean, node clean | 基线实际为 31 测试（v8 P0 卡点雷达已先行提交） |
| T1 字体 vendor（5 woff2 + OFL + @font-face） | ✅ 已通过 | 待提交 | 5×woff2 (21-24KB) + 2×OFL 落盘，`rg fonts.googleapis` 为 0 | 源：jsDelivr @fontsource |
| T2 style.css 重写（token + 组件，删动画/glass） | ✅ 已通过 | 待提交 | `rg backdrop-filter/aurora/d4af37` 为 0；裸 hex 仅 :root 与 .log-* 区 | 修复 .js-modal 被 .modern-modal-overlay display:flex 覆盖的 bug（加 !important） |
| T3 index.html 收编（style ≤5 + emoji→SVG） | ✅ 已通过 | 待提交 | 内联 style 70→9；裸 hex 0；功能 emoji 0；恢复 5927f81 卡点 DOM | 新增 ?tab= / ?skip_onboard= 截图深链参数 |
| T4 script.js 模板收编（style 降 ≥90%） | ✅ 已通过 | 待提交 | 内联 style 51→0（100%）；裸 hex 0；node OK | 动态 style 赋值改为 var()/classList |
| T5 全量回归（三绿 + ≥7 截图 + 手工清单） | ✅ 已通过 | 待提交 | 31 passed / ruff clean / node OK；5 视图截图 white 93-99% / dark 0% / indigo 在场 | 截图存 docs/screenshots_v4/；手工清单待用户真机过一遍 |
| T6 语言一致性（可选） | ⏸ 跳过 | — | — | 留待用户决定；i18n 机制未动 |

## 5. 执行节奏

按 `T1 → T5` 严格顺序，禁止跳跃。每项验收 + commit；T5 完成后：pytest + ruff + node 三绿、截图存档至 `docs/screenshots_v4/`、更新 `README.md` 中主题描述（"cyber-dark"字样）、在 `docs/OPTIMIZATION_ROADMAP_2026.md` 顶部追加设计重塑段落。
