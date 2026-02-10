# PLAN-automated-remediation: 自动修复与安全熔断 (Auto-Fix & Safety Gate)

> **来源**: [PRD-019: 自动修复 (Automated Remediation)](../PRD/019_Automated_Remediation.md)
> **目标**: 在坚实的“安全熔断 (Safety Gate)”基础上，实现“主动医生 (Active Doctor)”的自动修复能力。

## 1. 背景与目标 (Context & Objectives)
- **问题**: Agent 目前只能诊断 (侦探)。它需要安全地执行修复 (医生)。
- **核心要求**: **安全第一 (Safety First)**。必须通过安全熔断器 (限流 + 黑名单) 防止“告警风暴”和“破坏性操作”。
- **范围**: 后端逻辑 (Python), 数据库 (SQLite), 和 前端 (审计日志)。

## 2. 第一阶段: 基础设施 (安全网)
*基础先行。没有安全机制，不能开启自动修复。*

### 2.1 数据库设计 (SQLite Schema)
- [x] **创建表**: `automation_history`
    - `id` (主键)
    - `fingerprint` (目标资源标识, 如 `deployment/payment`)
    - `action` (如 `restart_pod`)
    - `status` (success/failed/throttled)
    - `timestamp`

### 2.2 安全熔断服务 (Safety Gate Service)
- [x] **实现 `SafetyGate` 类**:
    - `check_allow(fingerprint, action)` -> Boolean
    - **逻辑 1 (防抖/Debounce)**: 检查 DB。如果 1 小时内执行超过 3 次，返回 `False`。
    - **逻辑 2 (黑名单/Blacklist)**: 如果 namespace 是 `kube-system` 或有标签 `aiops.io/protection=true`，返回 `False`。

## 3. 第二阶段: 机制 (医生)
*决策和执行修复的核心逻辑。*

### 3.1 策略引擎 (Policy Engine)
- [x] **实现 `PolicyEngine`**:
    - 输入: `AlertPayload`
    - 输出: `Action | None`
    - **规则 (MVP 硬编码)**:
        - `RestartLoop` + `Dev` -> `restart_pod`
        - `DiskPressure` + `Tmp` -> `clean_disk`
        - 其他 -> `None` (仅通知)

### 3.2 动作执行器 (Action Executor)
- [x] **实现 `ActionExecutor`**:
    - `execute(action, target)`
    - 封装 `kubectl` 命令。
    - **关键**: 执行前必须调用 `SafetyGate.check_allow()`。
    - **审计**: 执行后必须写入 `automation_history`。

### 3.3 工作流集成
- [x] **修改 `alert_queue.py`**:
    - 在 `Investigation` 后插入 `PolicyEngine` 检查。
    - 如果推荐 `Action` -> 调用 `ActionExecutor`。

## 4. 第三阶段: 界面与可见性
*透明度是信任的关键。*

### 4.1 审计日志 API
- [x] `GET /api/automation/logs`: 列出最近的自动修复操作。

### 4.2 前端集成
- [x] **新页面**: `自动修复 (Automated Remediation)` (或设置页中的 Tab)。
    - 显示“最近操作”列表 (时间, 目标, 动作, 结果)。
    - 显示“安全拦截”事件 (如 "已拦截 nginx 的重启操作 (频率限制)")。

## 5. 验证计划 (Verification Plan)
- **单元测试**:
    - 测试 `SafetyGate` 限流逻辑 (mock DB)。
    - 测试 `PolicyEngine` 规则。
- **集成测试**:
    1. 部署一个 "CrashLoop" 测试 Pod。
    2. 模拟 Alertmanager webhook。
    3. 验证 `SafetyGate` 允许第 1 次重启。
    4. 快速触发 5 次以上告警。
    5. 验证 `SafetyGate` 拦截后续重启。
    6. 验证仪表盘显示历史记录。
