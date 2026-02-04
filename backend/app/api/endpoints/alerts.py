from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from sqlalchemy import select, delete, update
from datetime import datetime, timedelta

from app.db.session import AsyncSessionLocal
from app.db.models.alert import Alert

router = APIRouter()

@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_alerts():
    """Get all alerts ordered by time desc."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Alert).order_by(Alert.created_at.desc()))
        alerts = result.scalars().all()
        return [
            {
                "id": a.id,
                "title": a.title,
                "severity": a.severity,
                "status": a.status,
                "source": a.source,
                "summary": a.summary,
                "conversation_id": a.conversation_id,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in alerts
        ]

@router.put("/alerts/{alert_id}")
async def update_alert(alert_id: str, status: str = Query(..., regex="^(active|resolved)$")):
    """Update alert status."""
    async with AsyncSessionLocal() as db:
        stmt = update(Alert).where(Alert.id == alert_id).values(status=status)
        result = await db.execute(stmt)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"status": "success"}

@router.delete("/alerts/prune")
async def prune_alerts(
    mode: str = Query("resolved", regex="^(resolved|expired)$"), 
    days: int = Query(30, ge=1)
):
    """
    Prune alerts.
    - mode=resolved: Delete all 'resolved' alerts.
    - mode=expired: Delete all alerts older than 'days' (default 30).
    """
    async with AsyncSessionLocal() as db:
        if mode == "resolved":
            stmt = delete(Alert).where(Alert.status == "resolved")
        else:
             cutoff = datetime.utcnow() - timedelta(days=days)
             stmt = delete(Alert).where(Alert.created_at < cutoff)
             
        result = await db.execute(stmt)
        await db.commit()
        return {"deleted_count": result.rowcount}

@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete a single alert."""
    async with AsyncSessionLocal() as db:
        stmt = delete(Alert).where(Alert.id == alert_id)
        result = await db.execute(stmt)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"status": "success"}
