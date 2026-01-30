from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from app.db.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    fingerprint = Column(String, index=True, nullable=True) # Alertmanager fingerprint
    raw_data = Column(JSON, nullable=False) # Full valid webhook payload
    analysis = Column(JSON, nullable=True) # Orchestrator analysis result
    created_at = Column(DateTime, default=datetime.utcnow)
