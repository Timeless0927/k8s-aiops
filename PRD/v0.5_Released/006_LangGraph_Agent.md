# PRD-006: LangGraph Agent Integration
> **Status**: Released
> **目标**: 引入 `LangGraph` 框架，替换当前基于 `while` 循环的简易 ReAct 模式，实现更复杂的任务编排和状态管理。
> **价值**: 提升复杂故障排查能力，支持子任务拆解、人机回环 (Human-in-the-loop) 和更稳定的工具调用。

## 1. 现状问题 (Problem)

当前 `chat.py` 和 `chat_ws.py` 使用了一个简单的 `while` 循环来实现 ReAct (Reason+Act) 模式。存在以下问题：
1.  **状态管理弱**: 难以处理多轮对话中的上下文丢失或混淆。
2.  **流程僵化**: 无法轻松定义复杂的 workflow (如：先诊断 -> 需要授权 -> 暂停 -> 用户确认 -> 继续执行)。
3.  **扩展性差**: 增加新的逻辑分支（如反思、规划）会导致代码极度复杂。

## 2. 解决方案 (Solution): LangGraph

利用 `LangGraph` 的 Graph 概念构建 State Machine。

### 2.1 State Definition
```python
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    context: dict  # 存储提取出的 K8s 上下文 (Namespace/Pod)
    error_count: int
```

### 2.2 Graph Flow
1.  **Start** -> **Agent Node** (LLM Decide)
2.  **Agent Node** ->
    *   If tool_calls -> **Tools Node** -> **Agent Node**
    *   If final_answer -> **End**
3.  **Tools Node**: 执行 Kubectl/K8sGPT 等工具。

### 2.3 增强特性
*   **Structured Output**: 强制 LLM 输出结构化诊断结论。
*   **Error Handling**: 工具执行失败时，自动重试或让 LLM 修正参数。

## 3. 详细设计 (Detailed Design)

### 3.1 目录结构
```text
backend/app/agent/
├── graph.py          # LangGraph 定义
├── nodes/            # 图节点实现
│   ├── agent.py      # LLM 决策节点
│   └── tools.py      # 工具执行节点
├── state.py          # State 类型定义
└── orchestrator.py   # (Refactor) 调用 Graph.run
```

### 3.2 技术栈
*   `langgraph`
*   `langchain-openai` (或者直接用 SDK 封装 Node)

## 4. Execution Plan

- [x] **Dependency**: Install `langgraph`, `langchain-core` (if needed, or build simple graph manually).
    *   *Note*: 为了轻量化，如果不想引入全套 LangChain，我们可以仿照 LangGraph 手写一个轻量级 StateMachine，或者直接引入 `langgraph`。鉴于扩展性，建议引入 `langgraph`。
- [x] **Infrastructure**: 创建 `backend/app/agent/graph/` 目录。
- [x] **Refactor**: 改造 `chat_ws.py`，将 WebSocket 消息转发给 Graph 执行。
- [x] **Testing**: 验证基础对话和工具调用是否正常。

## 5. Verification
- [x] 1. 用户询问 "检查 default 命名空间下的 pod"。
- [x] 2. Agent 调用 `run_kubectl`。
- [x] 3. Agent 根据结果回答。
- [ ] 4. (进阶) 用户询问复杂问题，观察 Agent 是否能多次调用工具。

## 6. Technical Challenges & Architectural Evolution
在此次实施过程中，遇到并解决了以下关键技术挑战：

### 6.1 Frontend State Management (Black Screen Issue)
- **Problem**: 页面刷新或新会话时出现黑屏（White Screen/Black Screen of Death）。
- **Cause**: `App.tsx` 中的状态更新逻辑存在死循环，且 `localStorage` 可能存储了字符串 `"null"`，导致初始化判断错误。
- **Solution**: 
    1.  增强 `localStorage` 读取的健壮性（Null Safety）。
    2.  解耦 UI 选中状态 (`uiSelectedId`) 与 WebSocket 连接状态 (`currentConversationId`)，防止渲染流程中的 Race Condition。

### 6.2 Data Persistence & Transaction Isolation
- **Problem**: 刷新页面后，AI 的回复消失，只有用户消息被保存。
- **Cause**: `chat_ws.py`（WebSocket 处理器）和 `executor.py`（Graph 执行器）分别创建了独立的数据库 Session。
    - WebSocket 事务提交了用户消息。
    - Executor 的事务在异步流中可能未正确提交，或因隔离级别导致主线程不可见。
- **Solution**: 重构 `run_agent_graph` 签名，支持传入 Shared Session。
    - 确保 WebSocket 生命周期内的所有读写操作（用户消息 + AI 回复 + 工具日志）在同一个 DB 事务上下文中执行。

