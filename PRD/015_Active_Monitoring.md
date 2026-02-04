# PRD-015: 主动监控与告警响应 (Active Monitoring)

> **状态**: Draft
> **目标**: 从"被动响应"进化为"主动守望" (The Watcher)。集成 Prometheus Alertmanager，实现故障的自动发现、分析与处置。

## 1. 核心目标 (Goals)

1.  **闭环响应**: 打通 `Alert -> Agent -> Diagnostics -> Fix/Notify` 的全链路。
2.  **智能分流**: 区分"自动修复" (Auto-Fix) 与 "人工介入" (Human-in-the-loop)。
3.  **安全可控**: 杜绝 AI 导致的风暴 (Alert Storm) 或误操作。

## 2. 架构设计 (Architecture)

采用 **"轻量级策略路由" (Lightweight Policy Router)** 模式。
> **设计变更**: 移除 Redis 强依赖，使用 Python `asyncio.Queue` 做内存缓冲，使用 `SQLite` 做持久化记录。

```mermaid
graph TD
    A[Prometheus Alertmanager] -->|Webhook JSON| B(Backend Endpoint)
    B -->|入队| C[Memory Queue (AsyncIO)]
    C -->|出队/聚合| D[Smart Worker]
    D -->|分析标签| E{策略路由 Policy}
    
    E -->|Severity=Critical| F[人工通知 (钉钉/飞书)]
    E -->|Alert=RestartLoop + Env=Dev| G[自动修复 Agent]
    E -->|Unknown| H[诊断 Agent]
    
    H -->|生成报告| F
    G -->|执行结果| F
```

## 3. 核心功能模块 (Key Features)

### 3.1 告警接入层 (Webhook Ingest)
- **功能**: 接收 Alertmanager 标准 Webhook。
- **特性**:
    - **验签**: 验证来源合法性。
    - **消噪**: 基于 `groupKey` 进行聚合。
    - **队列**: 使用 **Python 内部 `asyncio.Queue`** 实现非阻塞接收。

### 3.2 自主排查 (Agentic Investigation)
> **设计变更**: 移除预组装上下文，完全依赖 Agent 自主决策。
- **逻辑**: Agent 收到告警 Payload (如 `Pod OOM`) 后，像人类专家一样思考：
    1.  *思考*: "收到 OOM 告警，我需要查看该 Pod 的资源限制和日志。"
    2.  *行动*: 调用 `kubectl describe pod` 查看 Limits。
    3.  *行动*: 调用 `loki_query` 查看崩溃前的最后日志。
    4.  *行动*: 调用 `k8sgpt` 分析可能原因。
- **优势**: 更灵活，Agent 根据不同告警类型决定查什么，而不是死板地只查 Log/Event。

### 3.3 交互式通知 (ChatOps)
- **渠道**: 钉钉 (DingTalk) / 飞书 (Lark) / Slack。
- **形式**: **ActionCard (交互卡片)**。
- **样例**:
    > **🚨 告警**: payment-service OOM
    > **🤖 诊断**: 内存限制 512Mi，实际使用 510Mi。
    > **💡 建议**: 扩容至 1Gi?
    > `[✅ 同意扩容]`  `[❌ 忽略]`  `[🔍与之对话]`

### 3.4 安全熔断器 (Safety Gate)
- **持久化**: 使用 **SQLite** 记录操作历史，替代 Redis。
- **防抖 (Debounce)**: 查询 SQLite 近期记录，同一资源 1 小时内最多自动修复 3 次。
- **黑名单**: 禁止操作 `kube-system` 或带有 `protection=true` 的资源。

## 4. 实施阶段 (Implementation Plan)

### Phase 8.1: 基础接入 (MVP)
- [ ] 后端实现 `/api/v1/webhook/alertmanager` 接口。
- [ ] 定义 Alert Payload Pydantic 模型。
- [ ] 实现 `BackgroundTask` 消费者处理内存队列。
- [ ] 简单逻辑: 收到告警 -> 触发 Agent 诊断 -> 打印日志。

### Phase 8.2: 交互通知
- [ ] 封装 `Notifier` 插件接口 (支持 DingTalk/Feishu)。
- [ ] 实现 ActionCard 模板构造器。
- [ ] 联调 Alertmanager，配置 `receiver` 指向 Agent。

### Phase 8.3: 自动修复与安全
- [ ] 实现基于 SQLite 的 `RateLimiter` (防抖)。
- [ ] 实现 `Executor` 层面的策略引擎 (Policy Engine)。

## 5. 验收标准 (DoD)
1.  在 Prometheus 手动触发测试告警。
2.  Agent 后台收到请求，通过内存队列异步处理，分析 Pod 日志。
3.  钉钉群收到带有"诊断建议"的卡片。
4.  **无新中间件**: 确认无需部署 Redis 即可运行。
