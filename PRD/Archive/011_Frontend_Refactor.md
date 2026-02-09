# PRD-011: 前端架构重构 (Frontend Architecture Refactoring)

> **目标**: 将目前庞大的单体 `App.tsx` 重构为模块化、可维护且高可用的组件架构，同时保证现有功能（聊天、插件、告警）零回归。
> **价值**: 彻底解决 "黑屏死机" 风险，提升代码可读性，为后续功能（如多页面、权限管理）铺路。

## 1. 现状分析 (Current State)

### 1.1 "上帝组件" (God Component) 问题
当前的 `App.tsx` (约 400 行) 承担了过多职责：
- **布局 (Layout)**: 侧边栏、顶部导航、告警面板、聊天网格。
- **状态管理 (State)**: WebSocket 连接、聊天记录、告警轮询、UI 切换。
- **业务逻辑 (Logic)**: 消息格式化、链接路由、工具输出处理。
- **渲染 (Rendering)**: 复杂的 `react-markdown` 配置。

### 1.2 识别到的风险 (Risks)
1.  **脆弱性**: Markdown 配置的一个小错误会导致整个应用崩溃白屏 (Black Screen)。
2.  **性能**: `App` 根组件的任何状态变化都会触发所有子组件重渲染。
3.  **不可测试**: 无法单独测试 "消息气泡" 或 "输入框" 的逻辑。

## 2. 重构计划 (Phase 8)

我们将采用 **基于特性的组件结构 (Feature-based Component Structure)**。

### 2.1 目录结构演进
```text
frontend/src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx        # 顶部标题栏、状态指示器
│   │   └── MainLayout.tsx    # 侧边栏 + 内容区域封装
│   ├── features/
│   │   ├── chat/
│   │   │   ├── ChatArea.tsx       # 消息列表容器 + 滚动逻辑
│   │   │   ├── ChatMessage.tsx    # 单个消息气泡 (Markdown 渲染隔离在此)
│   │   │   └── ChatInput.tsx      # 输入框
│   │   ├── alerts/
│   │   │   └── AlertSidebar.tsx   # 告警侧边栏
│   │   └── plugins/
│   │       └── PluginDashboard.tsx (原 PluginManager 改名)
│   └── common/
│       └── StatusIndicator.tsx
```

### 2.2 关键变更点

#### A. 隔离 Markdown 渲染 (`ChatMessage.tsx`)
- **动作**: 将 `react-markdown` 的逻辑移动到独立组件。
- **收益**: 即使某条消息渲染崩溃，可以通过 `ErrorBoundary` 仅展示 "消息错误"，而不是导致整个应用白屏。

#### B. 专用布局组件 (`MainLayout.tsx`)
- **动作**: 抽离侧边栏和 CSS Grid 布局结构。
- **收益**: `App.tsx` 将变得非常干净，仅负责路由和全局状态。

#### C. 自定义 Hook 抽离
- 确保 `useChatWebSocket` 是唯一管理连接的地方。
- 创建 `useAlerts` 专门处理轮询逻辑。

## 3. 实施步骤 (Implementation Steps)

- [ ] **步骤 1: 骨架搭建 (Scaffolding)**
    - 创建新的目录结构。
    - 将 `PluginManager.tsx` 移动到 `components/features/plugins/`。

- [ ] **步骤 2: 无状态组件抽离 (Stateless Extraction)**
    - 抽离 `Header.tsx`。
    - 抽离 `AlertSidebar.tsx` (接收 `alerts` props)。
    - 抽离 `ChatInput.tsx`。

- [ ] **步骤 3: 核心逻辑拆分 (Chat Logic)**
    - 创建 `ChatMessage.tsx` (封装 Markdown)。
    - 创建 `ChatArea.tsx` (管理自动滚动)。

- [ ] **步骤 4: 重组 App.tsx**
    - 组合新组件。
    - 添加 `ErrorBoundary` (React 16+) 捕获渲染错误。

## 4. 验证计划 (Verification Plan)

### 4.1 回归测试
- **聊天**: 验证发送/接收消息功能正常。
- **Markdown**: 验证 Grafana 链接和代码块渲染正常。
- **插件**: 验证插件管理页面加载正常。

### 4.2 健壮性测试
- **崩溃测试**: 在 `ChatMessage` 中手动抛出错误。
- **预期结果**: 应用不白屏，仅该消息显示错误提示。

## 5. 未来优化 (Post-Refactor)
- **虚拟化列表**: 如果消息超过 1000 条，引入 `react-window`。
- **状态库**: 如果状态变得更复杂，考虑引入 `Zustand`。
