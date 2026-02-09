# PRD-020: Interactive Stewardship (v0.6)

> **Status**: DRAFT
> **Goal**: 将 "AIOps Agent" 升级为真正的 "单集群管家" (Single Cluster Steward)。通过引入身份验证和交互式卡片，提供安全、确定的操作体验。

## 1. 核心愿景 (Vision)
- **安全**: "管家" 必须认识主人 (Authentication)，且操作留痕 (Audit)。
- **交互**: 告别枯燥的文本回复，使用现代化的 **Action Cards** 进行决策 (Approve/Deny)。
- **闭环**: 诊断 -> 建议 -> **点击批准** -> 执行 -> 反馈。

## 2. 功能模块 (Modules)

### 2.1 门禁系统 (The Gatekeeper / Auth)
**痛点**: 目前系统无鉴权，且高危操作仅靠简单的关键字触发，缺乏安全拦截。
**方案**:
1.  **身份验证 (Authentication)**:
    - **登录页**: 简单的登录界面 (`/login`)。
    - **认证方式**: 支持 `ADMIN_PASSWORD` (MVP) 及 OIDC。
    - **会话**: 使用 HTTP-only Cookie 存储 Session Token。
2.  **意图拦截 (Intent Interception)**:
    - **机制**: 所有用户指令不再直接触发 Tool，而是先经过 **风险评估**。
    - **流程**: LLM 分析意图 -> 识别高危操作 -> **拦截执行** -> 返回 "审批卡片"。
3.  **高危操作定义 (High-Risk Operations)**:
    - `delete` (删除资源)
    - `scale` (调整副本数)
    - `edit/patch` (修改配置)
    - `exec` (进入容器执行命令)
    - `restart` (重启工作负载)

### 2.2 交互式行动卡片 (Action Cards)
**痛点**: 用户需要打字 "yes" 或 "confirm" 来确认操作，容易出错且体验差。
**方案**: 将 Agent 的 "请求确认" 转化为结构化的卡片对象。
**卡片类型**:
1.  **审批卡 (Approval Card)**:
    - **场景**: 拦截到的高危操作 (如 "帮我重启下 nginx")。
    - **UI**: 
        - 标题: "⚠️ 高危操作确认"
        - 摘要: "将重启 `deployment/nginx` (namespace: default)"
        - 详情: (可选) 展示将被执行的 kubectl 命令。
        - 按钮: `[✅ 批准 (Approve)]` `[❌ 拒绝 (Deny)]`
    - **鉴权**: 点击 "批准" 时，后端需验证当前用户是否有 Admin 权限。
2.  **诊断卡 (Diagnosis Card)**:
    - **场景**: 告警分析结果。
    - **UI**: 折叠面板 (Accordion)。默认展示结论，点击展开查看详细 Logs/Metrics。
3.  **状态卡 (Status Card)**:
    - **场景**: 执行长任务。
    - **UI**: 进度条 + 实时日志流。

### 2.3 审计日志 (Audit Log)
**痛点**: 缺乏操作留痕。
**方案**:
- **SQLite 记录**: 记录所有 `Action Card` 的点击事件。
- **字段**: `id`, `user_id`, `intent`, `target_resource`, `command`, `timestamp`, `status` (SUCCESS/FAILED)。

### 2.4 动作验证与反馈 (Post-Action Verification)
**痛点**: "管发不管埋"，执行完命令后不知道实际效果 (如 Pod 是否真的 Running)。
**方案**:
- **自动跟进**: Agent 执行写操作后，自动进入 "Verification Phase"。
    - 轮询资源状态 (e.g., `kubectl get pod -w`)。
    - 检查 Events 是否有异常。
- **卡片状态流转**: `Wait Approval` -> `Executing` -> `Verifying` -> `✅ Success` / `❌ Failed`。

### 2.5 多端通知联动 (Notification DeepLink)
**定位**: 作为 IM 卡片的补充或降级方案。
**方案**:
- **Deep Link**: 消息包含跳转链接 `http://aiops.local/chat?card_id={uuid}`。
- **场景**: 当只需查看详情而无需操作，或 IM 交互失败时使用。
- **优先级**: **Low (P2)** - 优先实现 IM 原生交互。

### 2.6 首次启动导引 (Onboarding)
**痛点**: 初始环境无账号，环境变量配置密码不安全且繁琐。
**方案**:
- **Setup Wizard**: 检测到无 Admin 账号时，强制重定向到 `/setup` 页面。
- **流程**: 设置管理员用户名/密码 -> 生成 JWT Secret -> 初始化 SQLite。
- **安全**: 密码使用 `bcrypt` 哈希存储，不再依赖明文环境变量。

### 2.7 IM 双向对话与卡片 (DingTalk & Feishu)
**痛点**: 用户希望直接在 IM 中对话/审批，但内网环境无法接收 Webhook 回调。
**方案**:
- **钉钉 (DingTalk)**: 使用官方 `DingTalk Stream SDK` (基于 WebSocket)。
- **飞书 (Lark)**: 使用官方 `WebSocket 长连接` 模式。
- **共同特性**:
    - **零公网IP**: Agent 主动连接云端，无需内网穿透。
    - **卡片交互**: 支持直接点击卡片按钮回传指令 (ActionCallback)。
    - **群聊对话**: 在运维群 @Agent 直接提问。



## 3. 技术设计 (Technical Design)

### 3.1 多通道通知架构 (Multi-Channel Architecture)
Agent 后端将维护一个统一的 **`NotificationRouter`**，负责将消息路由到不同渠道。

```python
class NotificationRouter:
    async def send_card(self, card: ActionCard):
        # Channel 1: WebSocket (Web Dashboard)
        if card.channel == "web":
            await ws_manager.broadcast(card)
            
        # Channel 2: DingTalk Stream
        if settings.DINGTALK_ENABLED:
            await dingtalk_stream.send_interactive_card(card)
            
        # Channel 3: Feishu WebSocket
        if settings.FEISHU_ENABLED:
            await feishu_ws.send_card(card)
```

### 3.2 数据库设计 (SQLite Schema)
```sql
-- 用户表 (Local Auth)
CREATE TABLE users (
    id TEXT PRIMARY KEY, 
    username TEXT UNIQUE, 
    password_hash TEXT, 
    role TEXT DEFAULT 'admin',
    created_at DATETIME
);

-- 审计日志 (Audit Log)
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT, -- 关联 users.id 或 IM_OpenID
    action_type TEXT, -- e.g., "approve_restart"
    target_resource TEXT, -- e.g., "deployment/nginx"
    command_snapshot TEXT, -- 实际执行的命令
    status TEXT, -- "SUCCESS", "FAILED", "PENDING"
    client_ip TEXT, -- 若来自 Web
    platform TEXT, -- "web", "dingtalk", "feishu"
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 实施阶段 (Implementation Plan)

### Phase 1: 核心基础 (Core Foundation)
- [ ] **Onboarding**: 实现 `/setup` 页面和 `UserRepository`。
- [ ] **Auth**: 实现 `Login` 接口和 `JWT` 签发。
- [ ] **DB**: 创建 `users` 和 `audit_logs` 表。

### Phase 2: 双向通信 (Connectivity)
- [ ] **Stream SDK**: 集成 `DingTalk Stream` 或 `Feishu WS`。
- [ ] **Router**: 实现消息多路路由。
- [ ] **Bot Logic**: 处理 IM 端的 `@Agent` 消息。

### Phase 3: 安全拦截与卡片 (Interception)
- [ ] **LLM Upgrade**: 增加意图识别 Prompt (Intent Recognition)。
- [ ] **Card Engine**: 定义卡片数据结构 (JSON Schema)。
- [ ] **Safety Gate**: 实现高危操作拦截逻辑。

### Phase 4: 闭环验证 (Verification)
- [ ] **Action Runner**: 执行命令并捕捉输出。
- [ ] **Verify Logic**: 实现 "执行后检查" (Post-Check) 机制。
- [ ] **Audit**: 记录全链路日志。

## 5. 风险与缓解 (Risks & Mitigation)
- **IM 延迟**: Stream 连接断开？
    - **缓解**: 自动重连机制 + 本地日志缓存。

