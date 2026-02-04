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
