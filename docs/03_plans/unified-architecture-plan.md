# Unified Investigation Architecture Plan

## Promblem

Currently, the system has two parallel logic paths for solving K8s issues:

1. **Passive Investigation (AlertQueue)**: Uses the **Agent** (Smart, uses Tools, now enforces `langextract`).
2. **Active Patrol (PatrolService)**: Uses **Hardcoded Logic** (Iterate Pods -> Get Logs -> Call `analyze_logs` manually).

**New Concern**: The "Agent Rule" approach causes **Double Token Consumption**.

- Agent fetches logs -> Logs enter LLM Context (Cost 1).
- Agent sends logs to `analyze_incident_logs` -> Logs sent to LLM again (Cost 2).

## Solution

**"Everything is an Agent Task" + "Smart Tools"**

We will refactor `Active Patrol` to be a Trigger, AND we will upgrade Log Tools to be "Smart".

### 1. Smart Tools Pattern (Optimization)

Instead of Agent manually orchestrating `fetch` -> `analyze`, the **Tools** themselves will encapsulate this logic.

- **Old Flow**: `Agent` -> `run_loki_query` -> (Logs) -> `Agent` -> `analyze_logs` -> (Analysis).
- **New Flow**: `Agent` -> `run_loki_query(auto_analyze=True)` -> **Tool Internal** (Fetch + LangExtract) -> Returns `(Logs Preview + Structured Analysis)`.

### 2. Unified Workflow

1. **Trigger**: User clicks "Run Patrol" (or Cron).
2. **Dispatch**: PatrolService spawns an Agent Task.
3. **Execution**:
    - Agent calls `run_kubectl("logs ...")`.
    - Tool internally calls `forensics_plugin.analyze()`.
    - Tool returns:

        ```text
        [Logs Preview]
        Error: OOMKilled ...
        
        [AI Analysis]
        Root Cause: Memory Limit Exceeded
        Suggestion: Increase requests.memory
        ```

    - Agent consumes the *Result* directly, saving context window and rounds.

## Changes

1. **Modify `PatrolService.py`**:
    - Deprecate `_diagnose_logs`.
    - Dispatch Agent Task.

2. **Upgrade `kubectl_plugin` & `loki_plugin`**:
    - Import `forensics_plugin` internally.
    - Add `auto_analyze` parameter (default: True for error logs).
    - Return composite output.

3. **Benefit**:
    - **Efficiency**: Logs sent to LLM Analysis *behind the scenes*, Agent only sees the *Result*.
    - **Consistency**: Unified logic.
