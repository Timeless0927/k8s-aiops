# ☸️ Kubernetes AIOps Agent

> **下一代智能 K8s 运维专家 | 基于 LLM 的全自动故障排查与自愈平台**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**K8s AIOps Agent** 是一个集成了 **大语言模型 (LLM)** 、**图编排 (LangGraph)** 与 **专家知识库 (RAG)** 的智能运维助手。它不仅能回答这一刻的问题，还能 24/7 监听集群告警，像一名资深 SRE 工程师一样主动排查故障、查阅历史经验、生成诊断报告并记录解决方案。

---

## ✨ 核心特性 (Features)

### 🕵️‍♂️ 智能告警侦探 (Autonomous Alert Investigator)
- **主动响应**: 接收 Alertmanager Webhook，自动触发排查流程。
- **智能边界**: 自动锁定故障范围（Namespace/Pod），严禁跨界扫描，支持“向上溯源”（Pod -> Deployment）。
- **专家思维**: 基于 ReAct 框架，自主决定使用 `kubectl`、`PromQL` 还是 `Loki LogQL`。

### 🧠 进化型记忆系统 (Evolutionary Memory)
- **经验复用**: 从过去的排查中学习。Agent 会自动将成功的排障案例存入 `knowledge_base`。
- **秒级响应**: 遇到已知问题（如“OpenEBS 高 CPU 属正常现象”），Agent 会检索记忆并**直接给出结论**，跳过繁琐排查。
- **结构化存储**: 使用 YAML 数据库存储 Insights，支持按标签、症状精准检索。

### 💬 交互式运维 Copilot
- **自然语言运维**: "帮我查一下为什么 payment 服务起不来？" -> 自动翻译为 K8s 命令执行。
- **全栈可视化**: 现代化的 React 界面，集成 WebSocket 实时流式输出，支持 Markdown 图表渲染。
- **安全守门员**: 内置安全中间件，拦截 `delete/scale` 等高危命令（需人工确认）。

### 🔌 插件化架构
- **K8sGPT 集成**: 内置 K8sGPT 扫描能力，快速发现配置隐患。
- **多模态数据**: 同时处理 Metrics (Prometheus)、Logs (Loki) 和 K8s Events。

---

## 🛠️ 技术栈 (Tech Stack)

| 领域 | 技术组件 |
| :--- | :--- |
| **Backend** | Python 3.10, FastAPI, Uvicorn |
| **AI Kernel** | LangGraph, LangChain, OpenAI (Compatible API) |
| **Database** | SQLite (Session), YAML (Knowledge Base) |
| **Frontend** | React 18, TypeScript, TailwindCSS v4, Vite |
| **Infra** | Docker, Kubernetes, Prometheus, Loki |

---

## 🚀 快速开始 (Quick Start)

### 前置要求
- Python 3.10+
- Node.js 18+
- Kubernetes Cluster (Kubeconfig)
- OpenAI API Key (或兼容的 LLM 服务)

### 1. 启动后端 (Backend)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 LLM API Key 和 Kubeconfig 路径

# 启动服务
python -m uvicorn main:app --reload
```

### 2. 启动前端 (Frontend)

```bash
cd frontend
npm install
npm run dev
```

### 3. 使用系统
访问 `http://localhost:5173`。
- **普通对话**: 在聊天框输入 "检查集群健康状态"。
- **测试告警**: 运行 `cd backend && python test_alert.py` 模拟故障，观察 Agent 如何自动排查。

---

## 📂 项目结构 (Structure)

```text
k8s-aiops/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph 核心编排逻辑
│   │   ├── api/            # FastAPI 路由 (Chat, Webhook)
│   │   └── services/       # 业务逻辑 (AlertQueue, ChatHistory)
│   ├── knowledge_base/     # 记忆存储 (YAML/Markdown)
│   └── plugins/            # 工具插件 (K8s, Prom, Loki, Knowledge)
├── frontend/
│   ├── src/
│   │   ├── components/     # React 组件 (ChatArea, AlertsTopPanel)
│   │   └── features/       # 业务模块
└── PRD/                    # 产品需求文档
```

---

## 📚 知识库示例

我们的记忆系统存储在 `backend/knowledge_base/insights/insights_db.yaml`，格式如下：

```yaml
- topic: "Fix High CPU Usage for openebs"
  symptoms: "CPU usage > 400%"
  solution: "Known behavior for IO-intensive workloads..."
  tags: ["cpu", "openebs", "storage"]
  count: 5
```

---

## 🤝 贡献 (Contributing)

欢迎提交 PR 或 Issue！请确保遵循代码规范并更新相关测试。

## 📄 许可证 (License)

[MIT License](LICENSE)
