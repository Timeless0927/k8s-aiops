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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
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
        
    # 2. 初始化插件系统
    from app.services.plugin_manager import plugin_manager
    await plugin_manager.initialize()

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
