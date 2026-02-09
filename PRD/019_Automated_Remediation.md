# PRD-019: Automated Remediation & Safety (Auto-Fix)

> **Status**: Draft
> **Pre-requisite**: [PRD-015: Active Monitoring](015_Active_Monitoring.md) (Released)
> **Goal**: 实现告警的“主动自愈” (Active Remediation)。在 PRD-015 的“侦探”基础上，增加“医生”的能力，同时确保操作安全。

## 1. 核心目标 (Goals)
1.  **自动修复**: 对特定的常见故障（如 RestartLoop, DiskFull temp files）执行自动修复操作。
2.  **安全熔断**: 防止 AI 误操作导致系统崩溃或告警风暴。
3.  **审计追踪**: 记录每一次自动操作的决策依据和结果。

## 2. 缺失功能详解 (Missing Features)

### 2.1 安全熔断器 (Safety Gate) - *High Priority*
- **防抖 (Debounce)**: 
    - 机制: 同一资源（如 `deployment/payment`）在 `1小时` 内最多允许自动修复 `3次`。
    - 实现: 使用 SQLite 记录 `(fingerprint, action, timestamp)`。
- **黑名单 (Blacklist)**:
    - 严禁操作 `kube-system`, `monitoring` 等关键 Namespace。
    - 支持 K8s Label `aiops.io/protection=true` 豁免自动修复。

### 2.2 策略引擎 (Policy Engine)
- **决策逻辑**:
    - `Severity != Critical` -> 仅通知 (Notify)。
    - `Alert == OOMKilled` && `Env == Dev` -> 尝试扩容 (Scale Up)。
    - `Alert == ImagePullBackOff` -> 仅通知 (需要人工检查凭证)。
- **配置**: 在 `Settings` 中提供简单的开关或规则配置。

### 2.3 执行器 (Executor)
- **动作库 (Action Library)**:
    - `restart_pod`: 删除 Pod 触发重建。
    - `scale_up`: 修改 Replicas 或 Resources Requests/Limits。
    - `clean_disk`: 清理 `/tmp` 或 Docker Prune (需慎重)。

## 3. 实施计划 (Implementation Plan)

### Phase 1: 基础设施
- [ ] **SQLite Schema**: 创建 `automation_history` 表。
- [ ] **RateLimiter Service**: 实现基于 DB 的限流逻辑。

### Phase 2: 自动修复逻辑
- [ ] **Action Plugins**: 封装标准的 K8s 修复操作工具。
- [ ] **Workflow Update**: 修改 `AlertQueue`，在 `Investigation` 后增加 `Remediation` 步骤。

### Phase 3: 界面集成
- [ ] **Audit Log UI**: 在前端展示“自动修复历史”。
- [ ] **Settings UI**: 允许用户开关“自动修复”功能。
