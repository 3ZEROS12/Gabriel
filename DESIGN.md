# Gabriel Design System — v4 "Light Indigo"

> 设计基调：**纯净克制 · Stripe 精致感**（2026-08-08 定稿，取代 v3.1.0 "Cyber-Dark"）
> 本文件为 Gabriel 前端（`static/`）唯一视觉规范。执行 Agent 对任何 UI 改动必须先读本文件。
> 格式遵循 [DESIGN.md 规范](https://getdesign.md/)（Google Stitch 生态）；token 参照 [Stripe DESIGN.md](https://getdesign.md/stripe/design-md) 调整为本项目语义。

## 1. Visual Theme & Atmosphere

浅色单主题（**无暗色模式**）。白画布上的克制编辑感：大留白、hairline 细线、300 细体、单一靛紫强调。
气质：像 Stripe 的定价页——干净、可信、信息密度由留白而非装饰控制。
**移除**：极光渐变动画、玻璃拟态 blur、金色辉光、发光阴影、装饰性渐变背景。`prefers-reduced-motion` 关闭全部动效。

## 2. Color Palette & Roles

### 语义 token（唯一权威定义，代码中不得出现裸 hex）

| Token | 值 | 角色 |
|---|---|---|
| `--canvas` | `#ffffff` | 页面主背景 |
| `--canvas-soft` | `#f6f9fc` | 分区底（面板、卡片容器、统计块） |
| `--canvas-hover` | `#eef2f7` | hover 微抬升 |
| `--ink` | `#0d253d` | 正文（**深藏青，永不用纯黑**） |
| `--ink-secondary` | `#3b4c63` | 次级文字 |
| `--ink-mute` | `#64748d` | 辅助/标签/时间戳 |
| `--hairline` | `#e3e8ee` | 1px 边框/分隔线 |
| `--hairline-strong` | `#c9d4e0` | 输入框边框 |
| `--indigo` | `#533afd` | **唯一 CTA/强调色**：主按钮底、焦点环、链接、活动态 |
| `--indigo-press` | `#2e2b8c` | 主按钮按下 |
| `--indigo-soft` | `#eef0ff` | 强调色浅底（选中项、标签底） |
| `--success` | `#16a34a` | 成功/在线/运行中 |
| `--error` | `#dc2626` | 错误/断连/警告条 |
| `--warn` | `#d97706` | 等待/琥珀提示 |
| `--on-indigo` | `#ffffff` | 靛紫面上的文字 |

### 日志角色色（parser 已输出 `.log-*` class，仅 CSS 层映射）

| Class | 色 | 用途 |
|---|---|---|
| `.log-user` | `--indigo` | 用户输入 |
| `.log-agent` | `--ink`（bold） | Agent 回复 |
| `.log-claude` | `#7c3aed` | Claude 专属（保留区分） |
| `.log-cursor` | `--indigo` | Cursor 专属 |
| `.log-tool` | `--success` | 工具调用 |
| `.log-text` | `--ink` | 普通文本 |
| `.log-subtext` | `--ink-mute` | 元信息 |
| `.log-header` | `--ink`（bold） | 段落标题 |

## 3. Typography Rules

- **UI 字体**：Inter（300/400/500），`font-feature-settings: "ss01"`，正文负字距 `-0.01em`
- **终端/日志/代码**：JetBrains Mono（400/600）
- 字体必须 **vendor 本地**（`static/vendor/fonts/`，woff2 + OFL 许可证），**禁止 CDN**
- 数字统计（turns/cost/tokens/上下文%）用 `font-variant-numeric: tabular-nums`（等宽数字）
- 层级：页标题 `22px/300`，统计大数字 `24px/300`，卡片标题 `15px/500`，正文 `14px/400`，辅助 `12px/400`，微标签 `11px/500` 大写

## 4. Component Stylings

### 按钮
- `btn-primary`：`--indigo` 底、白字、**药丸 `border-radius: 9999px`**、`padding 8px 16px`、按下 `--indigo-press`；全站同屏最多 1 个主按钮
- `btn-outline`：白底、`--hairline-strong` 边框、`--ink` 字、圆角 `8px`
- `btn-danger`（清空/删除）：`--error` 描边文字，仅此场景用红
- 小号按钮：`font-size 12px / padding 4px 10px`（子 Tab、导出、快捷操作）

### 面板与卡片
- `panel`：`--canvas` 底、1px `--hairline`、圆角 `12px`、Level 1 阴影；hover 仅边框加深，无发光
- 统计块（Radar）：`--canvas-soft` 底、`12px` 圆角、内部数字 `tabular-nums` 24px/300
- agent 终端卡：白底 hairline，左侧 3px 状态色条（绿运行/琥珀等待/红卡死），hover 微上浮 + Level 2 阴影

### 聊天
- `ai-message`：白底、hairline、左侧 3px `--indigo` 条，圆角 `10px`，max-width 85%
- `user-message`：`--indigo` 底、白字、药丸偏圆角 `14px`（右侧收角）
- 代码块：`#f8fafc` 底 + hairline 边框，JetBrains Mono 13px

### 输入
- `sleek-input`：白底、`--hairline-strong` 边框、`6px` 圆角、`padding 8px 12px`、min-height 40px
- focus：`border --indigo` + 3px `--indigo-soft` 光环（非阴影发光）
- `chat-input`：药丸 `20px` 圆角，focus 同规则

### 其他组件
- 状态点 `status-dot`：绿 `--success`（在线，无脉冲动画）/ 红 `--error`（断连，无动画）
- 等待 banner：`--warn` 浅底 `#fef3c7` + `--warn` 文字，无 pulse 动画
- 错误横幅：`--error` 底白字（顶部全宽）
- toast（KB 推荐）：白底、hairline、`--indigo` 左侧条、Level 2 阴影
- 标签 pill：`--indigo-soft` 底 + `#4434d4` 文字，圆角 `9999px`
- modal：半透明遮罩 `rgba(13,37,61,0.4)`（无 blur）+ 白底面板 hairline + `16px` 圆角 + Level 2 阴影
- segmented control：`--canvas-soft` 底、选中项白底 + 1px hairline + 无阴影
- 滚动条：8px，thumb `#c9d4e0`，hover `#94a3b8`

## 5. Layout Principles

- 8pt 网格：间距只用 `4/8/12/16/24/32`（`--space-1..6` 保留）
- 圆角 scale：`4px` 标签 / `6px` 输入 / `10px` 聊天 / `12px` 卡片 / `16px` modal / `9999px` 药丸
- 面板内边距 `16px`；页面容器 max-width `1400px` 居中
- 信息密度：一行不超过 2 个动作按钮；统计块间距 `16px`

## 6. Depth & Elevation

- Level 0：无
- Level 1（卡片）：`box-shadow: 0 1px 3px rgba(0,55,112,0.08)`
- Level 2（浮层/toast/modal）：`0 8px 24px rgba(0,55,112,0.10), 0 2px 6px rgba(0,55,112,0.05)`
- 禁止：发光、金色投影、彩色 glow

## 7. Do's and Don'ts

**Do**：靛紫只留给主 CTA 和焦点；数字一律 tabular-nums；错误红只用于错误语义；hover 只加深边框或微上浮；字体用本地 vendor；后端输出 class、CSS 层定义颜色。

**Don't**：禁止裸 hex 出现在 HTML 内联 style（一切走 token/class）；禁止 emoji 充当图标（细线 SVG，stroke 1.5px）；禁止纯黑 `#000` 文字；禁止 `style.css` 之外出现动效（reduced-motion 优先）；禁止重新引入暗色主题或玻璃拟态；不改 i18n 键。

## 8. Responsive Behavior

- `<768px`：侧栏收窄为纯图标（隐藏 `.nav-text`），统计块 2 列，终端卡单列
- 统计数字 `24px→20px`；面板内边距 `16px→12px`
- 触摸目标 ≥40×40px

## 9. Agent Prompt Guide

改任何前端视觉，先回答三个问题再动手：
1. 这个元素的状态语义是什么（运行/等待/错误/成功/中性）？→ 映射到 §2 语义色
2. 它是主操作吗？→ 是才用 `--indigo` 实底药丸；否则 outline
3. 间距和圆角是否在 §5 的 scale 内？

快速色卡：背景 `#ffffff` · 分区 `#f6f9fc` · 文字 `#0d253d` · 次要 `#64748d` · 边框 `#e3e8ee` · 强调 `#533afd` · 成功 `#16a34a` · 错误 `#dc2626` · 等待 `#d97706`
