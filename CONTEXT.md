# Project Context: K8s AIOps SRE Agent

## 1. Project Overview
**Goal**: Build an in-cluster **SRE Copilot** that autonomously diagnoses Kubernetes incidents, integrates with the observability stack (Prometheus, Loki, Alertmanager), and consolidates team knowledge.
**Target Audience**: Internal DevOps/SRE teams.
**Key Feature**: "Experience Consolidation" — The system learns from past resolutions (RAG).

## 2. Technical Architecture

### Core Stack
- **Language**: Python 3.10+
- **Framework**: FastAPI (Backend/Webhook), LangChain/LangGraph (Agent Logic)
- **Database**: SQLite (Metadata), ChromaDB/LocalVectorStore (Knowledge Base)
- **Frontend**: React + Vite + TailwindCSS (Modern, Glassmorphism UI)
- **Deployment**: Kubernetes (Deployment + Service + Ingress)

### Integration Points
- **Input**: Alertmanager Webhook (`POST /webhook/alerts`)
- **Data Source**:
    - Prometheus (Metrics)
    - Loki (Logs)
    - Kubernetes API (Cluster State)
- **Inference**: External LLM APIs (OpenAI format)

### Capabilities
- [x] **Read-Write**: Can execute kubectl commands (scoped to authorized Namespaces).
- [x] **RAG**: Stores SOPs. Supports "Auto-Learning" and "Manual Import" of MD files.
- [x] **UI**: Interactive generic chat + Incident-specific dashboard (Basic Auth protected).
- [x] **Safety**: PII Redaction for logs + Alert Debouncing.
- [x] **Notifications**: Push analysis to DingTalk/Feishu.

## 3. Directory Structure (Proposed)
```
/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI Routes
│   │   ├── core/           # Config, Logging
│   │   ├── agent/          # LangChain Tools & Graphs
│   │   ├── services/       # Prom/Loki/K8s Clients
│   │   └── rag/            # Vector Store Logic
│   ├── main.py
│   └── requirements.txt
├── frontend/               # React App
├── k8s/                    # Helm Charts / Manifests
└── docker-compose.yml      # Local Dev
```

## 4. Development Guidelines
- **Style**: PEP 8 (Python), Prettier (TS/JS).
- **Testing**: Pytest for backend logic.
- **Agent Principles**:
    - ALWAYS validate LLM output before execution.
    - Provide "Reasoning" trace to the user.
    - Fail gracefully (Circuit Breaker for API calls).

## 5. Current Phase
**Architecture Locked**. Ready for **Phase 1 Implementation**: Project Scaffold & Basic Webhook Handler.

## 6. Skill Injection Strategy (Mandatory)
> **Instruction for Agent**: When working on specific components, you MUST strictly adhere to the corresponding skill sets defined below.

### Phase 1: Backend Core & Scaffolding
**Scope**: `/backend`, `Dockerfile`, `Main Entrypoint`
**Trigger**: When initializing the project or writing FastAPI logic.
**Required Skills**:
- **@python-expert**: 
  - 强制使用 Type Hints (Pydantic models)。
  - 确保 FastAPI 的 `Async/Await` 正确使用，避免阻塞。
- **@docker-expert**: 
  - 编写 Multi-stage Dockerfile，确保 Python 镜像体积最小（使用 `slim` 或 `alpine`）。
- **@api-design**: 
  - 规范 Webhook (`POST /webhook/alerts`) 的 Request/Response 结构，确保与 Alertmanager 格式兼容。

### Phase 2: Agent Logic & K8s Integration
**Scope**: `/backend/app/agent`, `/backend/app/services`
**Trigger**: When implementing the LangGraph logic or K8s Client.
**Required Skills**:
- **@kubernetes-infrastructure-expert**: 
  - **注意**：此处不仅用于写 YAML，也用于指导 **Python Kubernetes Client (`kubernetes-python`)** 的编写。
  - 确保对 K8s API 的调用包含重试机制 (Retries) 和超时设置 (Timeouts)。
  - 编写 Pod 内使用的 ServiceAccount 逻辑。
- **@clean-code**:
  - Agent 逻辑容易变得混乱（Spaghetti Code），强制要求模块化设计。

### Phase 3: Frontend Dashboard
**Scope**: `/frontend`
**Trigger**: When building the React UI.
**Required Skills**:
- **@react-design-patterns** (or `@nextjs-best-practices` if applicable):
  - 使用 Hooks 封装 API 请求。
  - 确保组件复用（Glassmorphism UI 组件库）。
- **@ui-ux-pro-modes**:
  - 设计“黑客风”或“指挥中心风”的 SRE 仪表盘。

### Phase 4: Deployment & Security
**Scope**: `/k8s`, Security Logic
**Trigger**: When generating Helm Charts or PII Redaction logic.
**Required Skills**:
- **@kubernetes-infrastructure-expert**:
  - 生成 Production-Ready 的 YAML (LivenessProbe, Resources Requests/Limits)。
- **@security-review**:
  - **Critical**: 审查 `kubectl` 执行权限。确保 Agent 只能操作授权的 Namespace，防止提权攻击。