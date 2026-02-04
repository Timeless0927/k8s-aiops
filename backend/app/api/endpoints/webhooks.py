from fastapi import APIRouter, HTTPException, Depends
from app.schemas.alert import AlertmanagerPayload
from app.services.alert_queue import AlertQueueService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Singleton instance
alert_queue = AlertQueueService()

@router.post("/alertmanager", status_code=200)
async def receive_alert(payload: AlertmanagerPayload):
    """
    Receive webhook from Prometheus Alertmanager.
    """
    try:
        logger.info(f"Received webhook from Alertmanager: {len(payload.alerts)} alerts")
        await alert_queue.enqueue(payload)
        return {"status": "queued", "alert_count": len(payload.alerts)}
    except Exception as e:
        logger.error(f"Failed to process webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
