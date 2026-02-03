# PRD-013: 视觉升级 - 现代浅色主题 (Modern Light Theme)

> **目标**: 全面革新 UI 视觉风格，从沉重的 "Dark Mode" 切换为清新、专业的 "Modern SaaS Light" 风格，并集成 "告警置顶" 布局。
> **设计理念**: 借鉴 Linear/Stripe/Notion 的设计语言，强调内容可读性、柔和的阴影和高对比度的文字。

## 1. 核心视觉变更 (Design System)

### 1.1 配色方案 (Color Palette)
不再使用黑底霓虹色，转为白底靛蓝风格。

| Token | 旧值 (Dark) | 新值 (Light) | 说明 |
| :--- | :--- | :--- | :--- |
| **Background** | `#09090b` (Black) | `#f8fafe` (Slate-50+) | 极其柔和的冷灰白背景 |
| **Surface** | `#18181b` (Dark Grey) | `#ffffff` (White) | 纯白卡片 |
| **Primary** | `#3b82f6` (Blue) | `#4f46e5` (Indigo-600) | 深靛蓝，更稳重专业 |
| **Text** | `#e4e4e7` (Light Grey) | `#1f2937` (Gray-800) | 深灰文字，高对比度 |
| **Muted** | `#71717a` (Grey) | `#6b7280` (Gray-500) | 辅助信息 |
| **Border** | `white/10` | `#e5e7eb` (Gray-200) | 实线细边框 |

### 1.2 阴影与质感 (Depth & Texture)
- **移除**: 磨砂玻璃效果 (`backdrop-blur`)，发光边框。
- **新增**:
    - **Soft Shadow**: `shadow-sm` (0 1px 2px 0 rgb(0 0 0 / 0.05)) 用于普通卡片。
    - **Float Shadow**: `shadow-lg` (用于悬浮或弹窗)。
    - **Clean Border**: `border-gray-200` (1px 实线)。

## 2. 布局调整 (Layout Changes) (集成 PRD-012)

### 2.1 移除左侧栏 (Left Sidebar Removal)
- 移除 `AlertSidebar`。
- 侧边栏仅保留 "会话列表 (Sidebar)"，且需改为浅色风格 (白底或极淡的灰底)。

### 2.2 顶部告警面板 (Top Alerts Panel)
- 新增 `AlertsTopPanel` 组件。
- 放置在 Header 下方。
- 样式：`bg-white border-b border-gray-100 py-3`。
- 卡片：`bg-red-50` (Critical), `bg-amber-50` (Warning)。

### 2.3 聊天区域 (Chat Area)
- **气泡风格**:
    - AI: `bg-white border border-gray-100 shadow-sm text-gray-800` (类似 Notion 块)。
    - User: `bg-indigo-600 text-white shadow-md` (高亮显示)。
- **宽度**: `max-w-4xl mx-auto` (居中，限制最大宽度以提升阅读体验)。

## 3. 实施计划

- [ ] **Step 1: 配置更新**
    - 更新 `tailwind.config.js` 中的颜色变量。
    - 更新 `index.css`，重写 `.glass` 和 `.glass-card` 工具类为新风格。

- [ ] **Step 2: 组件样式重构**
    - `Header.tsx`: 白底，底部阴影。
    - `Sidebar.tsx`: 浅灰底，深色文字。
    - `ChatArea.tsx` & `ChatMessage.tsx`: 更新气泡样式，移除 Markdown 的深色背景 (`prose-invert` -> 移除)。

- [ ] **Step 3: 布局重构 (Alerts Top)**
    - 创建 `AlertsTopPanel.tsx`。
    - 修改 `App.tsx`，移除 `AlertSidebar`，插入 `AlertsTopPanel`。

- [ ] **Step 4: 验证**
    - 视觉检查：对比度是否足够？
    - 交互检查：告警点击是否正常？
