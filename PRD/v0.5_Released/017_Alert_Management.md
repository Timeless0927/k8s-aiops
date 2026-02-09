# PRD: 告警历史与管理系统 (Alert Management)

## 1. 目标
构建一个告警管理中心，用于持久化存储所有接收到的告警，并允许用户在前端查看历史告警、当前状态（已解决/未解决）以及关联的 AI 调查对话。

## 2. 核心功能

### 2.1 后端 (Backend)
- **数据模型 (`Alert`)**:
    - `id`: UUID
    - `fingerprint`: 告警指纹 (用于去重)
    - `title`: 告警标题 (e.g., "High CPU Usage")
    - `severity`: 严重程度 (critical, warning, info)
    - `status`: 状态 (`active` / `resolved`)
    - `source`: 来源 (e.g., "k8s-cluster-1")
    - `summary`: 简要描述
    - `conversation_id`: 关联的 AI 调查会话 ID (Deep Link)
    - `created_at`: 创建时间
- **API**:
    - `GET /api/alerts`: 获取告警列表 (支持按状态过滤)。
    - `POST /api/alerts`: (内部) `AlertQueueService` 接收到 Webhook 后存入数据库。
    - `PUT /api/alerts/{id}`: 更新状态 (如手动标记为已解决)。
    - `DELETE /api/alerts/{id}`: 删除单条告警。
    - `DELETE /api/alerts/prune`: 清理过期告警 (如 > 30天) 或清理所有已解决告警。

### 2.2 前端 (Frontend)
- **新页面 (`/alerts`)**:
    - 展示告警表格/卡片流。
    - 显示字段: 时间、级别、标题、状态、操作。
    - **操作**:
        - "查看对话": 跳转到 `/chat?id={conversation_id}`。
        - "标记解决": 手动关闭告警。
        - "删除": 删除单条记录。
    - **顶部工具栏**:
        - "清理已解决": 批量删除所有 Status=Resolved 的记录。

### 2.3 数据保留策略 (Retention Policy)
- **自动清理**: 每次启动后端 (Startup Event) 或通过定时任务，自动删除 `created_at < NOW - 30 days` 的非 Critical 告警。
- **配置**: 在 `Settings` 中增加 `alert_retention_days` 配置项 (默认 30)。

## 3. 技术实现路径

### 3.1 数据库 Schema (SQLAlchemy)
```python
class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True)
    title = Column(String)
    severity = Column(String)
    status = Column(String, default="active") # active, resolved
    summary = Column(Text)
    conversation_id = Column(String) # ForeignKey to conversations
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 3.2 业务逻辑
1.  **接入点**: 修改 `AlertQueueService`，在触发 Agent 之前，先创建 `Alert` 记录 (`status=active`)。
2.  **关联**: 将生成的 `conversation_id` 写入 `Alert` 记录。
3.  **状态流转**:
    - 自动: 如果 AlertManager 发送 `status=resolved`，自动更新 DB。
    - 手动: 用户在 UI 点击 "Resolve"。

## 4. 交付清单
- [x] 后端 Model & Migration (`Alert`).
- [x] 后端 Service (`AlertService`).
- [x] API Endpoints (`/api/alerts`).
- [x] 前端 Page (`AlertsPage.tsx`).
- [x] 导航项更新 (`Sidebar.tsx`).
