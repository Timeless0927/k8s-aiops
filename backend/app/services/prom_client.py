import httpx
import logging
from app.core.monitoring_config import MonitoringConfigManager

logger = logging.getLogger(__name__)

class PrometheusClient:
    """
    Prometheus 查询客户端
    """
    def __init__(self, base_url: str = None):
        self._base_url = base_url

    @property
    def base_url(self):
        if self._base_url:
            return self._base_url
        return MonitoringConfigManager.get_config().prometheus_url.rstrip('/')

    async def query(self, query: str) -> dict:
        """
        执行 PromQL 查询 (instant query)
        """
        url = f"{self.base_url}/api/v1/query"
        params = {"query": query}
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params, timeout=10.0)
                resp.raise_for_status()
                data = resp.json()
                if data["status"] == "success":
                    return data["data"]
                else:
                    logger.error(f"Prometheus 查询错误: {data.get('error')}")
                    return {}
            except Exception as e:
                logger.error(f"连接 Prometheus 失败: {e}")
                return {"error": str(e)}

# 全局单例
prom_client = PrometheusClient()
