from sqlalchemy import Column, String, Boolean, JSON
from app.db.base import Base

class PluginState(Base):
    __tablename__ = "plugins"

    name = Column(String, primary_key=True)
    enabled = Column(Boolean, default=False)
    config = Column(JSON, nullable=True) # Store plugin-specific config if needed
