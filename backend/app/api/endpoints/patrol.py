from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.features.patrol.patrol_service import patrol_service

router = APIRouter()

@router.post("/run")
async def run_patrol():
    """
    Trigger immediate patrol (Patrol 2.0)
    """
    return await patrol_service.run_patrol()

@router.get("/visualize/{report_id}", response_class=HTMLResponse)
async def get_visualization(report_id: str):
    """
    Get the interactive HTML visualization for a specific report
    """
    html = patrol_service.report_cache.get(report_id)
    if not html:
        return "<h1>Report not found or expired</h1>"
    return html
