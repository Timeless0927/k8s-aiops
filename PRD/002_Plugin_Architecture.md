# PRD-002: Backend Plugin Architecture & Implementation Plan

> **Goal**: Refactor the current hardcoded Agent Tool system into a dynamic Plugin Architecture.
> **Scope**: Backend-only logic + Web UI for management.
> **Key Feature**: Dynamic Upload (.zip/.py), Hot-swapping (Enable/Disable), Agent Tool Extension.

## 1. Architecture Overview (架构设计)

### 1.1 核心概念 (Core Concepts)
*   **Plugin (插件)**: 一个独立的 Python 模块/包，包含特定的元数据和 `get_tools()` 入口函数。
*   **PluginManager (管理器)**: 单例服务，负责插件的发现、加载、卸载、状态管理。
*   **Registry (注册表)**: 内存中维护的 `tool_name -> execution_function` 映射表。

### 1.2 目录结构规范
```text
backend/
├── plugins/                 # [NEW] 插件存储根目录
│   ├── builtins/            # 系统内置插件 (kubectl_plugin, k8sgpt_plugin)
│   ├── user_uploads/        # 用户上传的插件 (动态加载)
│   └── plugin_status.json   # 插件启用/禁用状态持久化
└── app/
    └── services/
        └── plugin_manager.py # [NEW] 核心管理器
```

### 1.3 插件标准接口 (Protocol)
每个插件必须是一个符合以下规范的 Python 包/模块：

```python
# 示例: plugins/my_plugin/__init__.py

def get_manifest():
    return {
        "name": "network_diagnostics",
        "version": "1.0.0",
        "description": "Network related tools",
        "author": "SRE Team"
    }

def get_tools():
    """
    返回符合 OpenAI Function Calling 格式的工具列表
    """
    return [
        {
            "schema": {...},   # JSON Schema
            "handler": func_ref # 实执行函数
        }
    ]
```

## 2. 功能详细设计 (Detailed Design)

### 2.1 Backend Implementation
1.  **PluginManager Service**:
    *   `load_plugin(path)`: 使用 `importlib` 动态加载模块。
    *   `valid_plugin(module)`: 检查是否存在 `get_tools` 接口。
    *   `reload_all()`: 刷新 `TOOLS_SCHEMA` 和 `AVAILABLE_TOOLS`。
2.  **State Management**:
    *   使用 `plugin_status.json` 记录开启/关闭状态。
    *   应用启动时读取该文件，决定加载哪些插件。

### 2.2 API Endpoints
*   `GET /api/plugins`: 列出所有插件及其详细信息、当前状态。
*   `POST /api/plugins/upload`: 接收 `.zip` 文件。
    *   解压 -> 校验结构 -> 存入 `plugins/user_uploads/`。
*   `POST /api/plugins/{name}/toggle`: 启用/禁用插件。
    *   持久化状态到 `plugin_status.json` -> 触发 `reload_all`。
*   `DELETE /api/plugins/{name}`: 删除插件文件。

### 2.3 Frontend Implementation
*   **Plugin Management Page**:
    *   展示插件卡片列表。
    *   **Toggle Switch**: 控制插件启用/禁用。
    *   **Upload**: 支持 Zip 上传。
*   **Integration**:
    *   App.tsx 增加 View 切换逻辑。

## 3. Security Considerations (安全风险与对策)
*   **Risk**: RCE (Remote Code Execution)。用户上传恶意 Python 代码可完全控制服务器。
*   **Mitigation (Phase 1)**:
    *   **Auth**: 目前仅用于内网受信任环境。(未来需接入 Auth)
    *   **Sandbox (TODO)**: 暂不实现沙箱。

## 4. Implementation Plan (执行计划)

### Phase 1: Core Framework (Backend)
- [x] 创建 `backend/plugins` 目录和 `backend/app/services/plugin_manager.py`。
- [x] 重构 `backend/app/agent/tools.py`，将硬编码工具移入 `plugins/builtins/`。
- [x] 让 `PluginManager` 负责构建 `AVAILABLE_TOOLS`。

### Phase 2: API & Dynamic Loading
- [x] 实现 Upload API (`/api/plugins/upload`)，包含解压逻辑。
- [x] 实现 Toggle/List API (`/api/plugins/toggle`).
- [x] 实现 `importlib` 动态加载逻辑与错误捕获。

### Phase 3: Frontend Management UI
- [x] 新增页面 `/web/plugins` (`PluginManager.tsx`)。
- [x] 实现上传组件与列表管理交互。
- [x] 实现启用/禁用开关 (Toggle Switch)。

### Phase 4: Verification
- [x] 编写一个简单的 "Hello World" 插件进行上传测试。
- [x] 验证 Agent 是否能动态调用新插件的工具。
- [x] 修复 `chat` 接口缓存导致 Toggle 不生效的问题。

## 5. Verification Checklist
- [x] 现有功能 (`run_kubectl`) 重构后仍可正常工作。
- [x] 上传非法 Zip 包应返回错误。
- [x] 禁用插件后，Agent 无法再调用该工具。
- [x] 重启服务后，插件状态应保持（持久化验证）。
