from typing import List, Dict
import asyncio

class AlertStore:
    def __init__(self):
        self._alerts: List[Dict] = []
        self._lock = asyncio.Lock()

    async def add_alert_group(self, alert_group: dict):
        async with self._lock:
            # Simple append for MVP
            # In production, de-duplicate by groupKey
            self._alerts.insert(0, alert_group) # Newest first
            if len(self._alerts) > 50:
                self._alerts.pop()
    
    async def update_analysis(self, group_key: str, analysis: dict):
        async with self._lock:
            for alert in self._alerts:
                if alert.get("groupKey") == group_key:
                    alert["analysis"] = analysis
                    break

    async def get_alerts(self) -> List[Dict]:
        return self._alerts

alert_store = AlertStore()
