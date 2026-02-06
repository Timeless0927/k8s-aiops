# ☸️ Kubernetes AIOps Agent

> **下一代智能 K8s 运维专家 | 基于 LLM 的全自动故障排查与自愈平台**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**K8s AIOps Agent** 是一个集成了 **大语言模型 (LLM)** 、**图编排 (LangGraph)** 与 **双层记忆系统 (RAG)** 的智能运维助手。它不仅能回答这一刻的问题，还能 24/7 监听集群告警，像一名资深 SRE 工程师一样主动排查故障、查阅历史经验、生成诊断报告并记录解决方案。

---

## ✨ 核心特性 (Features)

### ⚙️ 动态系统设置 (New!)
- **全界面配置**: 内置 **系统设置 (System Settings)** 页面，支持在 Web UI 中直接修改 LLM 模型/密钥、Prometheus/Loki/Grafana 地址等核心配置。
- **免重启热更新**: 修改配置后**立即生效**，无需重启后端服务。
- **安全脱敏**: 敏感信息（API Key, Secret）自动脱敏显示，支持一键测试连接性。
- **全面汉化**: 界面已完成 100% 中文本地化适配。

### 🕵️‍♂️ 智能告警侦探 (Autonomous Alert Investigator)
- **主动响应**: 接收 Alertmanager Webhook，自动触发排查流程。
- **智能边界**: 自动锁定故障范围（Namespace/Pod），严禁跨界扫描，支持“向上溯源”（Pod -> Deployment）。
- **专家思维**: 基于 ReAct 框架，自主决定使用 `kubectl`、`PromQL` 还是 `Loki LogQL`。
- **自动修复**: 可配置的自动修复开关，针对已知问题执行预定义修复动作。

### 🧠 双层进化记忆 (Dual-Layer Memory)
- **Beads (短期工作记忆)**: 跟踪当前对话上下文与临时状态。
- **ChromaDB (长期语义记忆)**: 自动向量化存储历史排障经验 (Insights)。遇到的每个问题都会转化为“黄金案例”，Agent 下次遇到相似症状时会**优先检索记忆**，秒级给出结论。
- **经验复用**: 从过去的排查中学习，越用越聪明。

### 🔌 插件化架构 (Plugin Architecture)
- **插件市场**: 内置 **插件管理 (Plugin Dashboard)**，可视化管理所有能力组件。
- **动态扩展**: 支持上传 `.zip` 格式的自定义插件，即插即用。
- **内置能力**: 
  - `Prometheus/Loki/Grafana`: 监控数据查询。
  - `K8sGPT`: 集群健康及配置隐患扫描。
  - `Mock Scenario`: 故障模拟工具（CPU 飙高、OOM 等）。

### 💬 交互式运维 Copilot
- **自然语言运维**: "帮我查一下为什么 payment 服务起不来？" -> 自动翻译为 K8s 命令执行。
- **全栈可视化**: 现代化的 React 界面，集成 WebSocket 实时流式输出，支持 Markdown 图表渲染。
- **安全守门员**: 内置安全中间件，拦截 `delete/scale` 等高危命令（需人工确认）。

---

## 🛠️ 技术栈 (Tech Stack)

| 领域 | 技术组件 |
| :--- | :--- |
| **Backend** | Python 3.10, FastAPI, Uvicorn |
| **AI Kernel** | LangGraph, LangChain, OpenAI (Compatible API) |
| **Memory** | ChromaDB (Vector), Beads (State) |
| **Frontend** | React 18, TypeScript, TailwindCSS v4, Vite, Lucide Icons |
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
- **系统设置**: 首次进入建议先去 **Settings** 页面配置 LLM 和监控地址。
- **普通对话**: 在聊天框输入 "检查集群健康状态"。
- **测试告警**: 运行 `cd backend && python test_alert.py` 模拟故障，观察 Agent 如何自动排查。

---

## 📂 项目结构 (Structure)

```text
k8s-aiops/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph 核心编排逻辑
│   │   ├── api/            # FastAPI 路由 (Chat, Webhook, Settings)
│   │   ├── core/           # 核心配置 (Config Manager)
│   │   └── services/       # 业务逻辑 (AlertQueue, PluginManager)
│   ├── knowledge_base/     # 记忆存储 (ChromaDB Vector Store)
│   └── plugins/            # 工具插件 (Built-in & User Uploads)
├── frontend/
│   ├── src/
│   │   ├── components/     # React 组件 (Chat, Settings, Plugins)
│   │   └── features/       # 业务模块
│   └── public/
└── PRD/                    # 产品需求文档
```

---

## 🤝 贡献 (Contributing)

欢迎提交 PR 或 Issue！请确保遵循代码规范并更新相关测试。

## 📄 许可证 (License)

[MIT License](LICENSE)
