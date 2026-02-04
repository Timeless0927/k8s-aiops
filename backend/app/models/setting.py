from sqlalchemy import Column, String
from app.db.base import Base

class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=True)
    category = Column(String, default="general")
    description = Column(String, nullable=True)
