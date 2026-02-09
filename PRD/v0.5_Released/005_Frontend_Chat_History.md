# PRD-005: Frontend Chat History
> **Status**: Released

## 1. 概述
本文档描述了前端如何管理对话历史，包括持久化存储、WebSocket 同步和状态管理。

## 2. 状态管理 (State Management)
- **Current Conversation ID**:
  - 存储在 `App` 组件状态中。
  - **持久化**: 使用 `localStorage.getItem('activeConversationId')` 初始化，并在变更时更新。
  - **目的**: 防止页面刷新后丢失当前会话上下文。

## 3. 会话同步 (Session Synchronization)
### 3.1 现有会话
- 用户点击侧边栏 -> `setCurrentConversationId` -> `localStorage.setItem`.
- `useEffect` 检测 ID 变更 -> `fetch('/api/conversations/{id}/messages')`.

### 3.2 新建会话 (Lazy Creation)
- 初始状态 `currentConversationId` 为 `null`。
- 用户发送第一条消息 -> WebSocket 发送给后端。
- **后端行为**:
  - `ChatHistoryService.create_conversation` 创建新记录。
  - WebSocket 发送 `type: "init"` 事件，包含 `conversation_id` 和 `title`。
- **前端行为**:
  - `useChatWebSocket` 接收 `init` 事件 -> 调用 `onConversationInit` 回调。
  - `App` 组件回调 -> `setCurrentConversationId(newId)` -> 更新 `localStorage`。

## 4. 异常处理
- **404 Not Found**: 如果 localStorage 中的 ID 在后端不存在（已删除），`fetch` 返回 404，前端自动清除本地存储并重置状态。
