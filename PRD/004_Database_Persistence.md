# PRD-004: Database Persistence (数据持久化) [已完成]

> **目标**: 引入轻量级数据库 (SQLite) 以替代当前的内存存储，实现核心数据的持久化。
> **范围**: 后端 (`SQLAlchemy` + `SQLite`)。
> **价值**: 重启服务后不丢失对话记录、插件状态及告警历史。

## 1. 架构设计 (Architecture)

### 1.1 选型 (Tech Stack)
*   **Database**: SQLite (单文件 `app.db`，部署简单，适合单体 Agent)。
*   **ORM**: SQLAlchemy (Async) + Alembic (Migrations)。
*   **Reason**: 无需额外的 Docker 容器，Python 原生支持极佳。

### 1.2 数据模型 (Schema)

#### A. Chat History (`conversations`, `messages`)
```python
class Conversation(Base):
    id = Column(String, primary_key=True)  # UUID
    title = Column(String)
    created_at = Column(DateTime)

class Message(Base):
    id = Column(Integer, primary_key=True)
    conversation_id = Column(String, ForeignKey('conversations.id'))
    role = Column(String)  # user/assistant/tool
    content = Column(Text)
    created_at = Column(DateTime)
```

#### B. Plugin State (`plugins`)
```python
class PluginState(Base):
    name = Column(String, primary_key=True)
    enabled = Column(Boolean, default=False)
    config = Column(JSON)  # 预留配置项
```

#### C. Alerts (`alerts`)
```python
class Alert(Base):
    id = Column(Integer, primary_key=True)
    fingerprint = Column(String, index=True)
    raw_data = Column(JSON)
    analysis = Column(JSON) # 分析结果
    created_at = Column(DateTime)
```

## 2. 详细设计 (Detailed Design)

### 2.1 Backend Implementation
1.  **Project Structure**:
    ```text
    backend/
    ├── app/
    │   ├── db/
    │   │   ├── base.py       # Declarative Base
    │   │   ├── session.py    # Async Session Factory
    │   │   └── models/       # Models defined here
    │   ├── migrations/       # Alembic scripts
    │   └── services/
    │       ├── chat_history.py  # Service for chat
    │       └── plugin_store.py  # Service for plugins
    ```
2.  **Migration Strategy**:
    *   Initialize `alembic`.
    *   Create initial migration.
    *   Run migration on app startup (or manual).

### 2.2 Integration Points
*   **PluginManager**:
    *   Before: Reads `plugin_status.json`.
    *   After: Queries `PluginState` table via `PluginStoreService`.
*   **Chat API**:
    *   Before: Empty history / Memory list.
    *   After: Load last N messages from DB by `session_id`.
*   **Webhooks**:
    *   Before: `alert_store` (Memory).
    *   After: Insert into `Alert` table.

## 3. Execution Plan

### Phase 1: Infrastructure
- [ ] Install `sqlalchemy`, `aiosqlite`, `alembic`.
- [ ] Configure `app/db/session.py`.
- [ ] Define Models (`Message`, `PluginState`, `Alert`).
- [ ] Setup Alembic and generate initial migration.

### Phase 2: Refactor Plugin Manager
- [ ] Replace `json` file operations with DB queries.

### Phase 3: Refactor Chat & Alerts
- [ ] Update `chat_ws.py` to save messages to DB.
- [ ] Update `webhook.py` to save alerts to DB.

## 4. Verification Checklist
- [ ] Restart backend -> Plugin status remains.
- [ ] Restart backend -> Chat history loads (need simple API to fetch history).
- [ ] SQLite file `app.db` is created and populated.
