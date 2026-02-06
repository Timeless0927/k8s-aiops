# PRD: 双层记忆系统架构 (Dual-Layer Memory Architecture)

## 1. 愿景 (Vision)
构建一个类人的记忆系统，结合 **短期工作记忆 (Working Memory)** 和 **长期语义记忆 (Long-term Bio)**。
*   **Beads**: 负责 "当下" (Now) —— 任务追踪、步骤管理、状态维护。
*   **ChromaDB**: 负责 "过往" (Past) —— 经验沉淀、语义检索、RAG 增强。

## 2. Beads 项目分析 (Analysis)
### 2.1 核心特性
- **Git-Backed**: 所有数据存储在 Git 仓库中，天然支持版本控制、分支和回滚。
- **Graph Structure**: 任务（Issues）以图的形式存在，支持 `blocked_by` 等依赖关系。
- **Structured Memory**: 替代非结构化的 Markdown 计划，提供机器可读的 JSON-L 格式。
- **Context Management**: 能够帮助 Agent 区分 "Active", "Recent", "Blocked" 等状态，防止上下文丢失。

### 2.2 适用性评估
- **技术栈**: Beads 是 Python 项目 (需确认)，与我们当前 Backend (Python/FastAPI) 高度兼容。
- **优势**: 能显著提升 Agent 处理长链路复杂任务（如：诊断 -> 修复 -> 验证）的能力，防止“遗忘”之前的步骤。
- **集成成本**: 需要将其作为依赖引入，并替换或增强现有的 `MemoryService`。

## 3. 目标 (Goals)
1.  **引入 Beads**: 将 Beads 集成到 Backend 中。
2.  **增强记忆 (Enhanced Memory)**: 使用 Beads 来跟踪 Agent 的思考过程、执行步骤和各种 Insight。
3.  **持久化 (Persistence)**: 确保记忆在重启后依然存在（通过 Git/Filesystem）。

## 4. 架构设计 (Architecture)

### 4.1 双脑协作模型
1.  **Thinking Loop (思考环)**:
    *   Agent 接到任务 -> `Beads.create_task` (P0)
    *   Agent 需要知识 -> `ChromaDB.query` ("如何排查 CrashLoopBackOff")
    *   Agent 执行步骤 -> `Beads.create_task` (Child Task)
    *   Agent 解决问题 -> `Beads.close_task`

2.  **Memory Consolidation (记忆固化)**:
    *   当一个 Root Task (如 "Alert #123") 被标记为 `Done` 时，触发 **"归档流程"**。
    *   将 Beads 中的整个 Issue 链条 (Task + Steps + Resolution) 提取文本。
    *   调用 Embedding 模型 (OpenAI/Local) 生成向量。
    *   存入 `ChromaDB`，作为一条新的 "Insight"。
    *   *效果*: 今天修好的 Bug，明天再遇到，Agent 能直接从 ChromaDB 搜到昨天的解决方案。

### 4.2 实施方案 (Implementation Plan)

#### Phase 1: Beads (Working Memory) - 已开始
- [x] 引入 `beads-project`。
- [x] 实现 `MemoryService` (封装 `bd` CLI)。
- [√] 开发 `TaskTools` (Agent Interface)。

#### Phase 2: ChromaDB (Long-term Memory) - 已完成
- [√] 引入 `chromadb` & `sentence-transformers` (或使用 OpenAI Embedding)。
- [√] 创建 `KnowledgeService`:
    - `add_document(text, metadata)`
    - `query_similar(text, n_results)`
- [√] 迁移旧 YAML 数据到 ChromaDB。

#### Phase 3: 记忆联结 (The Bridge)
- [√] 实现 `archive_task_to_knowledge(task_id)` 函数。
- [√] 在 `MemoryService` 中监听任务完成事件，自动触发归档。

## 5. 技术栈选择
- **Short-term**: Beads (Git-based JSONL)
- **Long-term**: ChromaDB (Local Vector Store)
- **Embedding**: OpenAI `text-embedding-3-small` (推荐) 或 HuggingFace 本地模型。

## 5. 验证计划 (Verification)
- [√] **Unit Test**: 测试 Beads 的增删改查接口。
- [√] **Integration Test**: 模拟一个 Alert 处理流程，检查是否生成了对应的 Issue Graph。
- [√] **Persistence Test**: 重启服务，确认记忆是否丢失。

## 6. 风险 (Risks)
- Beads 尚处于早期阶段，可能存在 Bug 或文档缺失。
- 需要确保 Git 操作不会与用户的代码仓库冲突 (建议 store 在 `.gemini/beads` 或独立目录)。
