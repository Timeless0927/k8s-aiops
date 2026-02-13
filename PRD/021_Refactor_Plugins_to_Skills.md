# PRD-021: Refactor Plugins to Skills (v0.6)

> **Status**: DRAFT
> **Goal**: 将 "Plugin" 系统升级为 **"Skill" (技能)** 系统。
> **Core Value**: Skill 是 **完备的能力单元** (Self-Contained Capability)。
> **Design Choice**: 仅携带 **二进制工具 (Binaries)**，不携带 Python 库。Python 依赖 (kubernetes, requests, etc.) 必须预装在 Agent 的 Docker 镜像中。

## 1. 核心愿景 (Vision)
- **能力由技能定义**: 镜像 (Image) 保持轻量但预装 Python 环境，具体的 Linux 工具 (kubectl, helm, trivy) 由 Skill 包携带。
- **即插即用**: 上传 ZIP 包，系统自动配置 `PATH`，Agent 即可调用新工具。
- **统一术语**: 全栈统一使用 "Skill" 代替 "Plugin"。

## 2. 变更范围 (Scope of Changes)

1.  **Architecture**: 引入 **Skill Package Specification** (SPS)，仅支持 `bin/` 目录。
2.  **Backend Services**: 
    - `SkillManager`: 负责解压、路径注入、加载。
    - `EnvManager`: 动态修改 `PATH` 环境变量。
3.  **Database**: `skills` 表增加 `metadata` 字段。
4.  **No Python Deps**: 
    - 明确 **不包含** `lib/` 或 `venv`。
    - Skill 必须使用 Docker 镜像中已有的 Python 库。

## 3. 详细设计 (Detailed Design)

### 3.1 Skill 包结构 (Skill Package Structure)

一个合法的 Skill (`.zip`) 结构如下 (精简版)：

```text
my-kubectl-skill/
├── skill.yaml          # [NEW] 技能描述文件 (Manifest)
├── __init__.py         # Python 逻辑接口 (Entrypoint)
└── bin/                # [NEW] 二进制工具目录
    ├── linux/
    │   └── kubectl     # Linux binary (必选)
    └── windows/
        └── kubectl.exe # Windows binary (可选, 开发用)
```

#### skill.yaml 示例
```yaml
name: kubectl-skill
version: 1.28.0
description: "Provides kubectl binary"
author: "OpsTeam"
# 声明该 Skill 依赖的 Python 库 (仅作文档/校验用，不安装)
python_dependencies:
  - kubernetes >= 28.0
  - requests
binaries:
  - name: kubectl
    path: bin/  # Relative path to add to PATH
```

### 3.2 运行时加载机制 (Runtime Loading)

`SkillManager.load_skill(path)` 的流程升级：

1.  **解压 (Extract)**: 解压到 `backend/skills/{skill_name}`。
2.  **赋权 (Permission Grant) [CRITICAL]**:
    - 遍历 `backend/skills/{skill_name}/bin/{os}/` 目录。
    - 对所有文件执行 `os.chmod(path, 0o755)`。
    - **Reason**: Zip 解压可能丢失 +x 权限，必须显式授予。
3.  **环境注入 (Env Injection)**:
    - 将 `backend/skills/{skill_name}/bin/{os}/` 拼接到 `os.environ["PATH"]`。
    - **Result**: `subprocess.run("kubectl")` 可直接执行。
4.  **模块加载 (Import)**: 加载 `__init__.py`。

### 3.3 冲突解决与清理 (Conflict & Cleanup)

- **PATH 注入策略**: **Prepend** (前置)。后加载的生效。
- **清理机制**: Unload 时必须从 `os.environ["PATH"]` 中移除该目录。

### 3.4 内置技能迁移 (Built-in Migration)

将现有 `backend/plugins/builtins/` 迁移至 `backend/skills/builtins/`：

- `kubectl_skill/`: 包含静态编译的 `kubectl` 二进制 (Linux amd64)。
- `k8sgpt_skill/`: 包含 `k8sgpt` 二进制。

### 3.5 后端重构 (Backend Refactor)

#### A. 目录与文件映射
| 新路径 (New) | 职责 |
| :--- | :--- |
| `backend/skills/` | 技能根目录 |
| `backend/app/services/skill_manager.py` | 核心管理器 |

#### B. 数据库迁移
- 重命名表 `plugins` -> `skills`。
- 增加字段 `version`, `manifest`。

### 3.6 前端适配 (Frontend)
- **上传组件**: 校验 Zip 包是否包含 `skill.yaml`。

## 4. 实施计划 (Implementation Plan)

### Phase 1: 基础重构 (Rename & DB)
- [ ] 数据库表重命名 (plugins -> skills)。
- [ ] 后端服务类名替换。

### Phase 2: 增强型加载器 (Enhanced Loader)
- [ ] 实现 `SkillPackage` 解析与 PATH 注入。
- [ ] **Action Item**: 实现 `os.chmod` 逻辑。
- [ ] **Action Item**: 打包 Built-in Skills (kubectl, k8sgpt)。

### Phase 3: 前端与集成 (Frontend & Verify)
- [ ] 更新 UI。
- [ ] 验证上传与运行 (Permission Denied 错误应消除)。

## 5. 风险 (Risks)
- **镜像膨胀**: 如果每个 Skill 都带二进制，磁盘占用会增加。
- **依赖冲突**: 如果 Skill A 需要 `requests==1.0` 而镜像里只有 `2.0`，会报错。
    - *Mitigation*: 严格控制镜像预装列表，保持向后兼容。

