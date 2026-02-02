# PRD-008: Intelligent Architecture (File-Based Memory)

> **目标**: 借鉴 OpenClaw 架构，为 Agent 实现一套轻量级、透明、易于维护的**文件系统记忆 (File-Based Memory)**，替代重型的 VectorDB。

## 1. 核心理念 (Philosophy)

- **Plain Text is King**: 记忆应存储为人类可读的 Markdown 文件。用户可以直接用 VS Code 编辑 Agent 的记忆。
- **Explicit Retrieval**: Agent 通过工具主动搜索和读取记忆，而不是依赖黑盒的 Embedding 检索。
- **GitOps**: 记忆即代码，可以通过 Git 进行版本控制和回滚。

## 2. 目录结构 (Directory Structure)

在 `backend/` 下新增 `knowledge_base/` 目录：

```text
backend/knowledge_base/
├── sops/                 # 标准作业程序 (Read-Only for Agent, Human Edited)
│   ├── kafka_guide.md    # Kafka 排障手册
│   ├── network_faq.md    # 网络问题 FAQ
│   └── architecture.md   # 系统架构文档
│
├── daily_logs/           # 每日流水账 (Agent Auto-generated)
│   ├── 2026-02-02.md
│   └── 2026-02-03.md
│
└── insights/             # 长期洞察/经验总结 (Agent Auto-generated)
    ├── learned_fixes.md  # "学到的修复方法"
    └── environment.md    # 环境偏好 (如: "集群 Ingress 使用 Nginx")
```

## 3. 新增工具 (New Capabilities)

Agent 将获得一个新的插件 `knowledge_plugin`，包含以下工具：

### 3.1 `search_knowledge`
- **功能**: 基于关键词 (Keywords) 搜索知识库文件名和内容摘要。
- **场景**: "Unknown error found" -> 搜索 "error code"。
- **实现**: 简单的 `grep` 或 Python 文本匹配，返回匹配的文件列表及片段。

### 3.2 `read_knowledge`
- **功能**: 读取指定 Markdown 文件的完整内容。
- **场景**: 搜索发现 `kafka_guide.md` 相关 -> 读取内容获取排障步骤。

### 3.3 `save_insight` (Optional/Advanced)
- **功能**: 将本次对话的总结追加到 `insights/learned_fixes.md`。
- **场景**: 成功解决了一个难题后，自我总结并记录，供下次参考。

## 4. 工作流示例 (Workflow)

1.  **User**: "Kafka 连接不上了。"
2.  **Agent**: 
    - 思考: "我需要检查 Kafka，先看看有没有排障文档。"
    - 调用: `search_knowledge(query="kafka connection")`
3.  **Tool**: 返回 "Found `sops/kafka_guide.md`: Contains connection troubleshooting steps..."
4.  **Agent**:
    - 调用: `read_knowledge(file="sops/kafka_guide.md")`
5.  **Tool**: 返回 Markdown 内容。
6.  **Agent**: 
    - 思考: "文档说先检查 Service Endpoint。"
    - 调用: `run_kubectl(...)`

## 5. 优势 (Benefits)
1.  **极轻**: 零依赖，不需要安装 Docker 容器或 VectorDB。
2.  **透明**: 您随时可以打开 `knowledge_base/` 文件夹查看 Agent 到底记住了什么，甚至手动修正它的错误记忆。
3.  **可迁移**: 整个知识库就是一个文件夹，拷贝带走即可。

## 6. Implementation Plan
- [x] **Create Directory**: 建立 `backend/knowledge_base` 及子目录。
- [x] **Seed Data**: 创建一个简单的示例 SOP (e.g., `sops/demo.md`).
- [x] **Develop Plugin**: 开发 `knowledge_plugin` (Search/Read).
- [x] **Update Prompt**: 告知 Agent "遇到不懂的问题，先查知识库"。

## 7. Status
- **Date**: 2026-02-02
- **State**: Completed ✅
