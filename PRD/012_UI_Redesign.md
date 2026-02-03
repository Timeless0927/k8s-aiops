# PRD-012: UI 布局重构 - 告警置顶 (Alerts Top Placement)

> **目标**: 优化主界面布局，将 "Active Alerts" 从左侧垂直列表移动到顶部横向面板 (Horizontal Panel)。
> **背景**: 当前三栏布局在小屏幕上显得拥挤，且左侧告警列表占用了宝贵的水平空间，导致代码块和宽表格显示不全。用户建议将告警 "移动到上面单独展示"。

## 1. 现有问题
- **聊天区过窄**: 3 栏布局导致中间聊天区域受限。
- **告警视觉流**: 用户视线需要不断左右切换 (左侧看告警 -> 中间看诊断)。
- **空间浪费**: 如果没有告警，左侧栏是空白的，但依然占位。

## 2. 重构方案

### 2.1 新布局结构
```text
[Header]
[AlertsTopPanel] (Conditional: 仅当有告警时显示，或者始终显示头部但内容可折叠)
[ChatArea] (Full Width / Centered)
```

### 2.2 组件设计: `AlertsTopPanel.tsx`
- **位置**: 放置在 `Header` 之后，`ChatArea` 之前。
- **布局**: Flex Row (横向排列)，支持水平滚动 (Horizontal Scroll)。
- **卡片样式**: 紧凑型卡片 (Compact Card)。
    - 左侧: 严重性 (CRITICAL/WARNING) icon + 名字。
    - 右侧: 时间。
    - 点击行为: 保持不变 (触发诊断)。

### 2.3 交互优化
- **无告警状态**: 显示一个简洁的 "系统运行正常 (All Systems Operational)" 绿色横条，增加安全感。
- **有告警状态**: 红色/黄色背景的容器，突出显示警报卡片。

## 3. 实施步骤

- [ ] **Step 1: 创建新组件**
    - 创建 `frontend/src/components/features/alerts/AlertsTopPanel.tsx`。
    - 实现横向滚动布局。

- [ ] **Step 2: 修改主布局**
    - 修改 `App.tsx`。
    - 移除 `AlertSidebar`。
    - 在 `MainLayout` 或 `App` 中插入 `AlertsTopPanel`。
    - 调整 Grid 布局为单栏 (或两栏: 侧边导航 + 主内容)。

- [ ] **Step 3: 样式微调**
    - 确保新布局在宽屏下聊天气泡不会过宽 (需设置 `max-w-4xl mx-auto`)。

## 4. 预览效果 (ASCII)

```
+-------------------------------------------------------+
|  [SHIELD] K8s AIOps Agent              [Dashboard]... |  <-- Header
+-------------------------------------------------------+
|  [CRITICAL] Pod CrashLoopBackOff  |  [WARN] CPU High  |  <-- AlertsTopPanel
+-------------------------------------------------------+
|                                                       |
|                  Hello! How can I help?               |
|                                                       |
|                                            [User Msg] |
|                                                       |
+-------------------------------------------------------+
|  [ Input Box ...................................... ] |
+-------------------------------------------------------+
```
