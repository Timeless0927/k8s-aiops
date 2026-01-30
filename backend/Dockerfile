# -----------------------------------------------------------------------------
# Dockerfile Backend
# Optimization: Multi-stage build, Non-root user, Cache mounting
# -----------------------------------------------------------------------------

# Stage 1: Builder (安装依赖)
FROM python:3.11-slim as builder

WORKDIR /app

# 设置环境变量，防止 Python 生成 .pyc 文件，并禁用 pip 缓存（我们手动 mount）
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安装构建工具（如果有些库需要编译 C 扩展，可能需要 build-essential）
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential

COPY requirements.txt .

# 使用缓存挂载加速 pip 安装，安装到 /app/venv
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r requirements.txt

# Stage 2: Runtime (最终镜像)
FROM python:3.11-slim as runtime

# 创建非 root 用户 (UID 1001)
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash appuser

WORKDIR /app

# 从 builder 阶段复制虚拟环境
COPY --from=builder /app/venv /app/venv

# 复制应用代码 (注意权限)
COPY --chown=appuser:appgroup ./app ./app
COPY --chown=appuser:appgroup main.py .

# 设置 PATH，优先使用虚拟环境
ENV PATH="/app/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# 切换到非 root 用户
USER 1001

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
