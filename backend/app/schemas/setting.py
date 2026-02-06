from pydantic import BaseModel
from typing import Optional

class SettingBase(BaseModel):
    value: str
    category: Optional[str] = "general"
    description: Optional[str] = None

class SettingCreate(SettingBase):
    key: str

class SettingUpdate(BaseModel):
    value: str

class SettingResponse(SettingBase):
    key: str

    class Config:
        from_attributes = True

class LLMTestRequest(BaseModel):
    api_key: str
    base_url: str
    model_name: str = "gpt-4-turbo"

class LLMTestResponse(BaseModel):
    success: bool
    message: str
