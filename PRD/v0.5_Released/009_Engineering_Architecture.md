# PRD-009: Engineering Architecture (Testing & CI/CD)

> **Status**: Released
> **Goal**: 在引入更多复杂功能（Observability, Memory）之前，偿还技术债务，夯实工程基础，确保项目可维护性和扩展性。

## 1. 仓库治理 (Repository Hygiene)
**现状**: 
- Git 提交历史中包含了 `backend/k8sgpt.exe` (80MB+) 和 `frontend/node_modules`。
- 导致 `git clone` 缓慢，且 GitHub 推送报警告。

**方案**:
1.  **立即修正**:
    - 更新 `.gitignore` 排除所有二进制和依赖目录。
    - 使用 `git filter-repo` 或 `BFG` 清洗历史提交中的大文件（需谨慎操作，全员需重新 Clone）。
2.  **依赖管理**:
    - 后端使用 `poetry` 或 `pip-tools` 锁定依赖，而非仅 `requirements.txt`。
    - 前端确保 `package-lock.json` 提交，但 `node_modules` 严格排除。

## 2. 插件系统重构 (Plugin System 2.0)
**现状**:
- 插件仅是文件约定 (`__init__.py` 返回 dict)。
- 缺乏类型约束，工具定义随意，错误处理分散在各个 tools.py 中。

**方案**:
引入面向对象的插件基类 `BasePlugin`：
```python
class BasePlugin(ABC):
    @property
    @abstractmethod
    def manifest(self) -> PluginManifest: ...
    
    @abstractmethod
    def get_tools(self) -> List[BaseTool]: ...
    
    def on_load(self): ...  # 初始化资源 (e.g. 建立 DB 连接)
    def on_unload(self): ... # 清理资源
```
**价值**:
- **统一拦截**: 可以在基类层面统一实现 "工具执行前的鉴权" (Safety Guard)，不用每个工具自己写。
- **配置隔离**: 每个插件有独立的 Config 对象。

## 3. 配置管理 (Configuration)
**现状**:
- 所有配置堆在 `backend/app/core/config.py` 和扁平的 `.env` 中。
- 插件配置（如 Prometheus URL）与核心配置混杂。

**方案**:
- 拆分配置：`PluginSettings` 继承自 `BaseSettings`。
- 动态加载：插件初始化时只读取自己相关的 ENV 前缀（e.g., `PLUGIN_PROMETHEUS_URL`）。

## 4. Execution Plan (Architecture Sprint)
- [ ] **Repo**: 修复 `.gitignore` 并尝试清洗 Git 历史（或仅做一次 squash）。
- [ ] **Backend**: 定义 `BasePlugin` 接口并在 `k8sgpt_plugin` 中试运行。
- [ ] **Config**: 重构 `Settings` 类，支持插件独立配置。
