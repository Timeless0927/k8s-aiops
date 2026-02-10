from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from app.db.base import Base

class AutomationHistory(Base):
    __tablename__ = "automation_history"

    id = Column(Integer, primary_key=True, index=True)
    fingerprint = Column(String, index=True, nullable=False)  # Target resource identifier
    action = Column(String, nullable=False)  # Action name e.g., restart_pod
    namespace = Column(String, nullable=True)  # Target namespace
    status = Column(String, nullable=False)  # success, failed, throttled
    message = Column(Text, nullable=True)  # Detailed message or output
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "fingerprint": self.fingerprint,
            "action": self.action,
            "namespace": self.namespace,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
