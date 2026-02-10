from datetime import datetime, timedelta
from sqlalchemy import func, select
from app.db.session import AsyncSessionLocal
from app.db.models.automation import AutomationHistory
import logging

logger = logging.getLogger(__name__)

class SafetyGate:
    async def check_allow(self, fingerprint: str, action: str, namespace: str = None) -> bool:
        """
        Check if an action is allowed based on safety rules.
        """
        # 1. Blacklist Check
        if self._is_blacklisted(namespace):
            logger.warning(f"SafetyGate: Action {action} on {fingerprint} blocked by blacklist (ns={namespace})")
            return False

        # 2. Rate Limit (Debounce)
        if await self._is_rate_limited(fingerprint, action):
            logger.warning(f"SafetyGate: Action {action} on {fingerprint} blocked by rate limit")
            return False

        return True

    def _is_blacklisted(self, namespace: str) -> bool:
        if not namespace:
            return False
        
        # Hardcoded blacklist for MVP
        BLACKLIST_NAMESPACES = ["kube-system", "monitoring", "sofa-system"]
        if namespace in BLACKLIST_NAMESPACES:
            return True
        return False

    async def _is_rate_limited(self, fingerprint: str, action: str) -> bool:
        """
        Allow max 3 executions per hour for the same fingerprint & action.
        """
        async with AsyncSessionLocal() as db:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            # Count successful executions in the last hour
            result = await db.execute(
                select(func.count()).select_from(AutomationHistory).filter(
                    AutomationHistory.fingerprint == fingerprint,
                    AutomationHistory.action == action,
                    AutomationHistory.timestamp >= one_hour_ago,
                    AutomationHistory.status == "success"
                )
            )
            count = result.scalar()

            if count >= 3:
                return True
            return False

    async def record_action(self, fingerprint: str, action: str, namespace: str, status: str, message: str = None):
        """
        Record the action attempt in the audit log.
        """
        async with AsyncSessionLocal() as db:
            try:
                record = AutomationHistory(
                    fingerprint=fingerprint,
                    action=action,
                    namespace=namespace,
                    status=status,
                    message=message,
                    timestamp=datetime.utcnow()
                )
                db.add(record)
                await db.commit()
            except Exception as e:
                logger.error(f"SafetyGate: Failed to record action: {e}")
