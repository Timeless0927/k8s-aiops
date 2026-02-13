from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from app.services.knowledge_service import knowledge_service

router = APIRouter()

class IngestRequest(BaseModel):
    text: str = Field(..., description="The raw text content of the fault report or post-mortem.")
    source: str = Field("user_upload", description="Source of the report (e.g., user_upload, slack, jira).")

class IngestResponse(BaseModel):
    status: str
    structured_data: Dict[str, Any]

@router.post("/ingest", response_model=IngestResponse)
async def ingest_fault_report(request: IngestRequest):
    """
    Ingest a raw fault report, structure it using AI, and store it in the Knowledge Base.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Report text cannot be empty.")

    result, error_msg = knowledge_service.ingest_fault_report(request.text, request.source)
    
    if error_msg:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {error_msg}")
    
    return {
        "status": "success",
        "structured_data": result
    }
