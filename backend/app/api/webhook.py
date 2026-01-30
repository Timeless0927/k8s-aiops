from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from app.models.alert import AlertGroup
from app.agent.orchestrator import orchestrator
import logging

# 创建路由
router = APIRouter()

from app.services.store import alert_store

@router.post("/webhook/alerts", status_code=status.HTTP_200_OK)
async def receive_alert(payload: AlertGroup, background_tasks: BackgroundTasks):
    """
    接收来自 Alertmanager 的 Webhook 请求
    """
    logger = logging.getLogger(__name__)
    logger.info(f"[Alert Received] GroupKey: {payload.groupKey}, Status: {payload.status}, Count: {len(payload.alerts)}")
    
    # store raw data to DB
    from app.db.session import AsyncSessionLocal
    from app.db.models.alert import Alert
    
    async with AsyncSessionLocal() as session:
        alert_record = Alert(
            fingerprint=payload.commonLabels.get("alertname", "unknown"), # Use alertname as temporary fingerprint or generate hashing?
            # Alertmanager sends a list. We store the whole group payload as raw?
            # Or split? PRD says Alerts table.
            # Simplified: Store Group Payload as raw_data.
            raw_data=payload.model_dump(),
            analysis=None
        )
        session.add(alert_record)
        await session.commit()
        
    # 异步触发分析任务
    if payload.status == "firing":
        background_tasks.add_task(orchestrator.analyze_alert_group, payload)
    
    return {"status": "received", "processed_count": len(payload.alerts)}

@router.get("/webhook/alerts")
async def get_alerts():
    from app.db.session import AsyncSessionLocal
    from app.db.models.alert import Alert
    from sqlalchemy import select, desc
    
    async with AsyncSessionLocal() as session:
        # Return last 20 alerts
        result = await session.execute(select(Alert).order_by(desc(Alert.created_at)).limit(20))
        alerts = result.scalars().all()
        # Format similar to before? Or just list of records?
        # Frontend expects model? 
        return alerts
