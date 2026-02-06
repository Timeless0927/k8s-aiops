from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.setting import SettingResponse, SettingUpdate
from app.services.settings_service import SettingsService

router = APIRouter()

@router.get("/", response_model=List[SettingResponse])
async def get_settings(db: AsyncSession = Depends(get_db)):
    """List all system settings."""
    return await SettingsService.get_all_settings(db)

@router.put("/{key}", response_model=SettingResponse)
@router.put("/{key}", response_model=SettingResponse)
async def update_setting(key: str, payload: SettingUpdate, db: AsyncSession = Depends(get_db)):
    """Update a specific setting."""
    setting = await SettingsService.set_setting(db, key, payload)
    
    # Reload LLM Config if relevant keys changed
    if key.startswith("openai_"):
        from app.core.llm_config import LLMConfigManager
        await LLMConfigManager.reload_config(db)
    
    if key in ["prometheus_url", "loki_url", "grafana_url"]:
        from app.core.monitoring_config import MonitoringConfigManager
        await MonitoringConfigManager.reload_config(db)
        
    return setting

from app.schemas.setting import LLMTestRequest, LLMTestResponse
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

@router.post("/test-llm", response_model=LLMTestResponse)
async def test_llm_connection(payload: LLMTestRequest):
    """Test LLM connection with provided credentials."""
    try:
        if not payload.api_key:
             return LLMTestResponse(success=False, message="API Key is missing")
        
        llm = ChatOpenAI(
            api_key=payload.api_key,
            base_url=payload.base_url,
            model=payload.model_name,
            temperature=0.1,
            max_tokens=10
        )
        
        # Simple invocation
        resp = await llm.ainvoke([HumanMessage(content="Hello")])
        
        return LLMTestResponse(success=True, message=f"Success! Response: {resp.content}")
    except Exception as e:
        return LLMTestResponse(success=False, message=str(e))
