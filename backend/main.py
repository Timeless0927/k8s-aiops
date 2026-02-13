from fastapi import FastAPI
from app.api import webhook, chat, plugins, chat_ws

# 初始化 FastAPI 应用
app = FastAPI(
    title="K8s AIOps Agent",
    description="SRE Copilot Agent capable of diagnosing and fixing K8s issues.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
from fastapi.middleware.cors import CORSMiddleware
import os

# Get allowed origins from env (default to * for dev, but production must specify)
origins_str = os.getenv("BACKEND_CORS_ORIGINS", "*")
origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(webhook.router, prefix="/api", tags=["Webhooks"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(plugins.router, prefix="/api/plugins", tags=["Plugins"])
app.include_router(chat_ws.router, prefix="/api", tags=["Chat (WebSocket)"])

@app.on_event("startup")
async def startup_event():
    # 1. 确保数据库表存在
    from app.db.base import Base
    from app.db.session import engine
    # 确保所有模型都被导入，以便 Base.metadata 能够通过 create_all 创建表
    from app.db import models
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # 1.5 初始化默认设置
    from app.services.settings_service import SettingsService
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await SettingsService.initialize_defaults(db)
        # Initialize LLM Config
        from app.core.llm_config import LLMConfigManager
        await LLMConfigManager.reload_config(db)
        
        # Initialize Monitoring Config
        from app.core.monitoring_config import MonitoringConfigManager
        await MonitoringConfigManager.reload_config(db)
        
    # 2. 初始化插件系统
    from app.services.plugin_manager import plugin_manager
    await plugin_manager.initialize()

    # 3. 启动 AlertQueue Worker (Active Monitoring)
    from app.services.alert_queue import AlertQueueService
    import asyncio
    asyncio.create_task(AlertQueueService().process_queue())

# 注册 Active Monitoring Webhook
from app.api.endpoints import webhooks, alerts, system, settings

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(webhooks.router, prefix="/api/v1/webhook", tags=["webhooks"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(plugins.router, prefix="/api/v1/plugins", tags=["plugins"])

from app.api.endpoints import patrol
app.include_router(patrol.router, prefix="/api/v1/patrol", tags=["Patrol"])

from app.api.endpoints import knowledge
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["Knowledge"])

@app.get("/health", tags=["System"])
async def health_check():
    """
    健康检查接口 (Health Check)
    """
    return {"status": "ok", "component": "backend"}

if __name__ == "__main__":
    import uvicorn
    # 仅用于本地开发调试
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
