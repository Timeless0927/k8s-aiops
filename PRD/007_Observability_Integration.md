# PRD-007: Observability Integration (Prometheus & Loki)

> **目标**: 为 Agent 赋予 "视力"，使其能够实时查询 Prometheus 指标和 Loki 日志，从而支持更深层次的故障排查（不仅仅是静态配置错误）。

## 1. 现状与问题
当前 Agent 主要依赖 `kubectl` 和 `k8sgpt`。
- **局限性**: 只能看到 "Pod CrashLoopBackOff" 这种**结果**，看不到 "CPU 飙升" 或 "500 错误率激增" 这种**过程**。
- **缺失能力**: 无法回答 "为什么昨天晚上服务挂了？" (需要查历史日志) 或 "现在的流量是否正常？" (需要查 QPS 指标)。

## 2. 解决方案 (Solution)

引入两个新的内置插件：
1.  **`prometheus_plugin`**: 查询监控指标。
2.  **`loki_plugin`**: 查询日志流。

### 2.1 Prometheus Plugin
- **Tool Name**: `run_prometheus_query`
- **Args**: `query` (PromQL), `time_range` (optional)
- **Use Cases**:
    - "检查 CPU/内存使用率"
    - "查看 5xx 错误率"
    - "P99 延迟是多少"

### 2.2 Loki Plugin
- **Tool Name**: `run_loki_query`
- **Args**: `query` (LogQL), `limit` (default 50)
- **Use Cases**:
    - "查看包含 'error' 的最近日志"
    - "根据 TraceID 查找日志"
    - "统计特定时间段的异常数量"

## 3. 技术设计 (Technical Design)

### 3.1配置 (Configuration)
复用 `backend/app/core/config.py` 中的现有配置：
- `PROMETHEUS_URL`: default `http://prometheus-k8s.monitoring:9090`
- `LOKI_URL`: default `http://loki.monitoring:3100`

> **注意**: 本地开发时，需要通过 `kubectl port-forward` 将这些服务暴露到 localhost，并在 `.env` 中覆盖上述 URL。

### 3.2 插件实现
在 `backend/plugins/builtins/` 下创建目录：
- `prometheus_plugin/`
- `loki_plugin/`

#### 3.2.1 Prometheus Tool Schema
```python
{
    "name": "run_prometheus_query",
    "description": "Execute a PromQL query to retrieve metrics. Use for performance issues, resource usage, or error rates.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "Valid PromQL query (e.g., 'sum(rate(container_cpu_usage_seconds_total[5m])) by (pod)')"
            },
            "step": { "type": "string", "description": "Step interval (e.g. '1m')" }
        },
        "required": ["query"]
    }
}
```

#### 3.2.2 Loki Tool Schema
```python
{
    "name": "run_loki_query",
    "description": "Execute a LogQL query to search logs. Use for finding error messages, exceptions, or specific events in logs.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "Valid LogQL query (e.g., '{app=\"foo\"} |= \"error\"')"
            },
            "limit": { "type": "integer", "description": "Max lines to return (default 50)" }
        },
        "required": ["query"]
    }
}
```

### 3.3 Prompt Strategy (System Prompt)
为了让 LLM 写出正确的查询语句，我们需要提供 few-shot examples：

**Prometheus Rules**:
- "METRICS: Use `run_prometheus_query` for performance/health."
- "SYNTAX: Use `sum(rate(...[5m]))` for rates. Check `node_memory_MemAvailable_bytes` for nodes."

**Loki Rules**:
- "LOGS: Use `run_loki_query` to trace errors."
- "SYNTAX: LogQL uses `{label=\"value\"}` selector. Use `|= \"error\"` for substring match."

### 3.4 Error Handling
- **Connection Refused**: 返回友好的提示 "Cannot connect to Prometheus/Loki. Please check if port-forward is running or URL is correct."
- **Invalid Query**: 返回 Prometheus/Loki 的原始报错 (400 Bad Request)，通常包含语法错误信息，让 LLM 自动修正。
- **Empty Result**: 明确返回 "No metrics/logs found for this query."，引导 LLM 扩大时间范围或放宽过滤条件。

## 4. Execution Plan
- [ ] **Infrastructure**: 确认本地可以通过 nodeport 访问 Prometheus/Loki (或者使用 Mock 数据)。
- [ ] **Impl Prometheus**: 开发 `prometheus_plugin`.
- [ ] **Impl Loki**: 开发 `loki_plugin`.
- [ ] **Integration**: 注册插件并更新 `executor.py`.
- [ ] **Verification**: 
    - 询问 "查询 node_load1"。
    - 询问 "查询 pod 日志"。
