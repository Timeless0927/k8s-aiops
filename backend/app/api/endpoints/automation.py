from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy import desc
from app.db.session import get_db, AsyncSession
from app.db.models.automation import AutomationHistory

router = APIRouter()

@router.get("/logs", response_model=List[dict])
async def get_automation_logs(
    skip: int = 0, 
    limit: int = 50, 
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Retrieve automation execution logs.
    """
    try:
        # Async query
        result = await db.execute(
            select(AutomationHistory)
            .order_by(desc(AutomationHistory.timestamp))
            .offset(skip)
            .limit(limit)
        )
        logs = result.scalars().all()
        return [log.to_dict() for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
