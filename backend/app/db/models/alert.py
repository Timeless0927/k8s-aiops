from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime
from app.db.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True) # UUID
    fingerprint = Column(String, index=True, nullable=True) 
    title = Column(String)
    severity = Column(String)
    status = Column(String, default="active") # active, resolved
    source = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    conversation_id = Column(String, nullable=True) # Deep link to chat
    created_at = Column(DateTime, default=datetime.utcnow)
