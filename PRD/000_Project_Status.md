# 📊 项目状态与文档索引 (Project Status & Documentation Index)

> **最后更新**: 2026-02-09
> **当前版本**: v0.5.0 (Pro Max UI + Active Monitoring Alpha)

## 🚀 模块状态概览 (Module Status Overview)

| 模块 (Module) | 文档 (PRD) | 状态 (Status) | 描述 (Description) |
| :--- | :--- | :--- | :--- |
| **基础架构 (Foundation)** |
| 插件架构 (Plugin Architecture) | [002](v0.5_Released/002_Plugin_Architecture.md) | ✅ 已上线 (Released) | 动态插件加载、Python/K8s 接口封装。 |
| 数据持久化 (DB Persistence) | [004](v0.5_Released/004_Database_Persistence.md) | ✅ 已上线 (Released) | SQLite/SQLAlchemy 用于存储对话、告警和设置。 |
| 设置与本地化 (Settings) | [018](v0.5_Released/018_Settings_and_Localization.md) | ✅ 已上线 (Released) | 动态配置、敏感信息脱敏、全中文界面。 |
| **智能核心 (Intelligence)** |
| 流式对话 (Streaming Chat) | [003](v0.5_Released/003_Streaming_Chat.md) | ✅ 已上线 (Released) | WebSocket 实时对话，工具调用可视化。 |
| Agent 核心 (Agent Core) | [006](v0.5_Released/006_LangGraph_Agent.md) | ✅ 已上线 (Released) | LangGraph 框架，ReAct 循环，记忆集成。 |
| 双层记忆 (Smart Memory) | [Memory](v0.5_Released/memory_optimization_beads.md) | ✅ 已上线 (Released) | 双层记忆系统 (Beads 工作记忆 + ChromaDB 长期记忆)。 |
| **监控体系 (Monitoring)** |
| 可观测性 (Observability) | [007](v0.5_Released/007_Observability_Integration.md) | ✅ 已上线 (Released) | Prometheus 指标与 Loki 日志集成。 |
| 主动监控 (Active Monitoring) | [015](v0.5_Released/015_Active_Monitoring.md) | ✅ 已上线 (Released) | 自动诊断、Webhook 接入、通知集成。 |
| 告警管理 (Alert Management) | [017](v0.5_Released/017_Alert_Management.md) | ✅ 已上线 (Released) | 告警历史记录、状态管理、AI 调查关联。 |
| 自动修复 (Automated Remediation) | [019](019_Automated_Remediation.md) | 📅 计划中 (Planned) | 自动修复、安全熔断器 (Policy Engine)。 |
| **用户界面 (User Interface)** |
| UI Pro Max | [014](v0.5_Released/014_UI_Pro_Max.md) | ✅ 已上线 (Released) | 高端 SaaS 风格设计，Tailwind v4，告警侧边栏。 |
| 交互式管家 (Interactive Steward) | [020](020_Interactive_Stewardship.md) | 📅 计划中 (Planned) | 行动卡片 (Action Cards)、简易门禁 (Auth)、审计日志。 |
| 视觉刷新 (Visual Refresh) | [013](Archive/013_Visual_Refresh.md) | 📦 已归档 (Archived) | *已被 PRD-014 取代* |

## 📂 已归档文档 (Archived Documents)
> `PRD/Archive/` 目录下的文档已过时或被取代，仅供参考。

- **001 Baseline Status**: 早期项目审计报告。
- **011/012/013 UI Series**: 中间设计过程文档，均已被 **014** 取代。
- **016 Brainstorm**: 头脑风暴草稿，已被 **015** 取代。

## 📝 待办事项 (Next Steps)
1.  **安全熔断器 (Safety Gate)**: 在 `015_Active_Monitoring.md` 中实现速率限制 (`RateLimiter`) 和策略引擎 (`PolicyEngine`)。
2.  **自动修复 (Auto-Fix)**: 启用简单告警的自动修复功能（例如：重启 Pod）。
