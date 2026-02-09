# 当前系统现状说明书
**版本**: 0.3
**日期**: 2026-01-29
**状态**: 迭代开发阶段

## 1. 已实现功能 (Implemented Features)

### 1.1 后端 (Backend)
- **Plugin Architecture**: 动态插件加载、启停管理、持久化。
- **Streaming Chat** (New): 
  - 基于 WebSocket 的实时流式对话 (`/api/chat/ws`)。
  - 支持工具调用过程的可视化（"Thinking..." 状态）。
  - 具备断线重连与异常捕获机制。
- **Webhooks**: 支持接收 Alertmanager 告警 (`/api/webhook/alerts`)。

### 1.2 前端 (Frontend)
- **Page**: 
  - Dashboard: 告警列表 + 聊天窗口。
  - PluginManager: 插件管理。
- **Hooks**: `useChatWebSocket` 封装了心跳、重连及消息状态管理。
- **Config**: Vite Proxy 配置已修正为 IPv4 模式。

## 2. 待完成功能 (TODO List)

### 高优先级
- [ ] **数据库持久化**: 
  - 目前插件状态用 JSON，对话历史全在前端内存。
  - 需要引入 SQLite/PostgreSQL 存储历史记录、插件元数据、告警分析结果。
- [ ] **Agent 逻辑增强**: 引入 LangGraph。

### 中优先级
- [ ] **前端组件拆分**: 优化 `App.tsx`。
- [ ] **Auth**: 鉴权机制。

## 3. 技术债务 (Tech Debt)
- **Mock Data**: 告警数据目前未持化，重启后清空。
- **Error Handling**: 部分 API 的错误返回格式需统一。
