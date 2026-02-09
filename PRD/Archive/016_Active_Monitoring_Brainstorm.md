# 🧠 Brainstorm: Active Monitoring & Anomaly Detection
> **Status**: Archived.
> **Note**: This brainstorm document has been superseded by **[PRD-015: Active Monitoring](file:///e:/git/k8s-aiops/PRD/015_Active_Monitoring.md)**. Please refer to PRD-015 for the actual implementation details.

## Context
我们已经完成了被动告警响应。现在的目标是实现 **主动巡检 ("Active Monitoring")**，让 Agent 定期检查集群健康，并预测潜在问题。

---

## Option A: Python 调度器 (The "Cron" Approach)
在后端引入 `APScheduler`，定期触发巡检脚本。

**机制**:
1.  **调度**: 每小时运行 `run_health_check()`。
2.  **实现**:
    - 获取当前通过 `kubectl top` 的资源使用率。
    - 查 Prometheus 过去 7 天通过 PromQL 的历史数据。
    - **算法**: 使用 Python (NumPy/SciPy) 计算 Z-Score 或简单的线性回归。
    - **判定**: 如果 `current > predicted + threshold`，触发告警。

✅ **Pros:**
- **稳定低成本**: 为了确定性的数学计算，不需要每次都问 LLM。
- **完全可控**: 代码逻辑透明。

❌ **Cons:**
- **上下文缺失**: 虽然知道 CPU 高了，但不知道是哪个具体业务导致的（除非写很复杂的逻辑）。

📊 **Effort:** Medium

---

## Option B: AI 自主巡逻 (The "Autonomous" Approach)
Agent 进入一个 Long-running Loop，自主决定何时检查。

**机制**:
1.  **调度**: Agent System Prompt 中植入 `WaitNode`。
2.  **实现**:
    - Agent 自主决定 "我现在该查查 Log 了"。
    - 将获取到的 Metrics JSON 完整喂给 LLM。
3.  **判定**: LLM 根据“直觉”和知识库判断曲线是否异常。

✅ **Pros:**
- **深度分析**: 能发现逻辑错误（即便资源占用不高）。
- **灵活**: 可以根据之前的故障历史调整巡检重点。

❌ **Cons:**
- **高成本**: 持续消耗 Token。
- **不可靠**: 可能会幻觉，或者对简单的数值计算出错。

📊 **Effort:** High

---

## Option C: Prometheus Native (The "Infra" Approach)
利用 Prometheus 的 `predict_linear` 函数直接产生告警。

**机制**:
1.  **配置**: 编写复杂的 `PrometheusRule` YAML。
    - `alert: DiskWillFillIn4Hours`
    - `expr: predict_linear(node_filesystem_free_bytes[1h], 4*3600) < 0`
2.  **Agent**: 只作为接收方 (Webhook)，收到预测告警后进行解释。

✅ **Pros:**
- **性能最强**: 下沉到基础设施层。
- **零 Token**: 只有出事才调用 AI。

❌ **Cons:**
- **配置黑盒**: 无法在 Chat 界面调整逻辑。
- **无法定制**: 很难做复杂的跨数据源关联分析。

📊 **Effort:** Medium

---

## 💡 Recommendation

**推荐: Option A (Python Scheduler) + AI Analysis**

**理由**:
1.  **可靠性**: 监控的基础必须是可靠的数学（Option A/C）。
2.  **易用性**: 我们希望 Agent 能控制巡检逻辑（Option A），而不是去改底层的 Prometheus YAML (Option C)。
3.  **成本**: 平时用 Python 算，算出来异常了再叫 AI (Option A)，比一直让 AI 盯着强 (Option B)。

**下一步建议**:
- 安装 `APScheduler`。
- 创建 `MonitorService`。
- 实现一个简单的 `CPU Anomaly Detector`。
