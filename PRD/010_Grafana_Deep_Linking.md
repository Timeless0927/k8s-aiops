# PRD-010: Grafana Deep Linking (Phase 7)

> **目标**: 弃用自研的前端图表组件，改为在 Agent 回复中生成 **Grafana Explore Deep Links**。利用 Grafana 强大的原生能力进行可视化分析。

## 1. 背景 (Context)
- **现状**: Agent 目前返回纯文本的指标 (Prometheus) 和日志 (Loki)。
- **痛点**: 文本无法展示趋势 (Trend) 和分布 (Distribution)。
- **决策**: 放弃 Phase 7 原计划的 "Frontend Charts"，转向 "Deep Integration Strategy"。
- **优势**: 开发成本低 (Zero UI Code)，分析能力强 (Grafana Native)，维护简单。

## 2. 核心设计 (Core Design)

### 2.1 用户体验
1.  **User**: "查看过去 1 小时 API 的错误率。"
2.  **Agent**: "过去 1 小时 API 错误率平均为 0.5%，最高峰值 2.3%。"
3.  **Agent**: `[🔍 Open in Grafana](http://grafana.../explore?left=...)`
4.  **User**: 点击链接 -> 跳转 Grafana Explore -> 看到折线图。

### 2.2 URL 构造逻辑
Grafana Explore 的 URL 结构如下：
`{GRAFANA_URL}/explore?orgId=1&left={URL_ENCODED_JSON}`

JSON 结构 (Simplified):
```json
{
  "datasource": "Prometheus",
  "queries": [
    {
      "refId": "A",
      "expr": "sum(rate(http_requests_total[5m]))"
    }
  ],
  "range": {
    "from": "now-1h",
    "to": "now"
  }
}
```

### 2.3 配置需求 (`backend/app/core/config.py`)
需要新增以下配置项：
- `GRAFANA_URL`: Grafana 的访问地址 (e.g., `http://localhost:3000`).
- `GRAFANA_DATASOURCE_UID_PROM`: Prometheus 数据源的名称或 UID (default: `prometheus` or `Prometheus`).
- `GRAFANA_DATASOURCE_UID_LOKI`: Loki 数据源的名称或 UID (default: `loki` or `Loki`).

## 3. 详细任务 (Tasks)

### 3.1 基础设施 (Infrastructure)
- [ ] **Config**: 在 `Settings` 类中添加 Grafana 相关配置。
- [ ] **Env**: 在 `.env` 中设置默认值 (需与本地 Kind 集群或 Docker Compose 匹配)。

### 3.2 插件增强 (Plugin Enhancement)

#### A. Prometheus Plugin
- [ ] **Helper**: 实现 `_build_grafana_link(query, start, end)` 函数。
- [ ] **Update**: 修改 `run_prometheus_query`，在返回的文本末尾追加 `\n\n🔗 [View Graph in Grafana](...)`。

#### B. Loki Plugin
- [ ] **Helper**: 实现 `_build_grafana_link(query, start, end)` 函数。
- [ ] **Update**: 修改 `run_loki_query`，在返回的日志末尾追加 `\n\n🔗 [View Logs in Grafana](...)`。

### 3.3 验证 (Verification)
- [x] **Click Test**: 点击生成的链接，确认能正确打开 Grafana Explore 页面。
- [x] **Query Check**: 确认 Grafana 中的 PromQL/LogQL 与 Agent 生成的一致。
- [x] **Time Range**: 确认时间范围 (last 1h) 传递正确。

## 6. Status
- **Date**: 2026-02-02
- **State**: Completed ✅

## 4. 风险与缓解
- **URL 长度**: 极其复杂的查询可能导致 URL 过长。-> 缓解：现代浏览器支持长 URL，或仅截取核心部分。
- **数据源名称不匹配**: 用户 Grafana 数据源可能叫 "Prometheus-Prod"。-> 缓解：提供 ENV 配置 `GRAFANA_DATASOURCE_NAME`。

## 5. Definition of Done
- Agent 的每一次 Metrics/Logs 查询都附带一个有效的 Grafana 链接。
- 点击链接能直接看到图表。
