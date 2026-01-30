# PRD-003: WebSocket 流式对话实现方案 (已完成)

> **目标**: 将当前同步的 Chat API 升级为 WebSocket，以支持实时的 Token 流式传输和“思考过程”可视化。
> **状态**: **已上线/已验证**
> **价值**: 提升用户体验 (降低首字延迟 TTFB)，让用户清晰看到 Agent 的工具执行步骤。

## 1. 架构概览 (Architecture Overview)

### 1.1 协议选择 (Protocol)
*   **选型**: **WebSocket**
*   **理由**: 全双工通信允许未来实现“打断”功能。

### 1.2 通信标准 (WebSocket Protocol)
**服务端点**: `ws://{host}/api/chat/ws`

**服务端 -> 客户端 (Events)**
1.  **Token Delta**: `{"type": "token", "content": "..."}`
2.  **Tool Start**: `{"type": "tool_start", "tool": "...", "args": "..."}`
3.  **Tool Result**: `{"type": "tool_result", "output": "..."}`
4.  **Final/Error**: `{"type": "done"}` 或 `{"type": "error", "content": "..."}`

## 2. 后端实现 (Backend Implementation)

- [x] 创建 `backend/app/api/chat_ws.py`。
- [x] 实现 `stream_chat` 生成器函数，处理 OpenAI 流式传输 + 工具执行逻辑。
- [x] 在 `main.py` 中注册新路由。
- [x] **错误处理**: 增加 `try/except` 捕获 LLM 流式异常，防止 WebSocket 意外断开 (1006)。

## 3. 前端实现 (Frontend Implementation)

- [x] 在前端创建 `useChatWebSocket` Hook。
- [x] 实现“断线重连”与“消失消息自动保存”逻辑 (Commit on Close)。
- [x] 更新 `App.tsx` 以处理流式事件。
- [x] 将“思考步骤”与“消息内容”渲染分离。
- [x] **Proxy 修复**: 修正 Vite 配置，强制使用 IPv4 (`127.0.0.1`) 代理以解决 Windows 兼容性问题。

## 4. 验证清单 (Verification Checklist)
- [x] 用户输入消息 -> 立即响应 (首字延迟 < 1s)。
- [x] 工具执行 (如 `run_kubectl`) 在 UI 上实时可见。
- [x] 网络断开能被优雅处理 (自动保存已生成内容)。
