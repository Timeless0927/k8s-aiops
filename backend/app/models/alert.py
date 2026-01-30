from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# -----------------------------------------------------------------------------
# Alertmanager 数据模型 w/ Chinese Comments
# 参考: https://prometheus.io/docs/alerting/latest/configuration/#webhook_config
# -----------------------------------------------------------------------------

class Alert(BaseModel):
    """
    单个告警对象包含的详细信息
    """
    status: str = Field(..., description="告警状态: firing 或 resolved")
    labels: Dict[str, str] = Field(default_factory=dict, description="告警标签集合 (e.g., alertname, severity)")
    annotations: Dict[str, str] = Field(default_factory=dict, description="告警注解 (e.g., summary, description)")
    startsAt: datetime = Field(..., description="告警开始时间")
    endsAt: Optional[datetime] = Field(None, description="告警结束时间")
    generatorURL: Optional[str] = Field(None, description="触发此告警的 Prometheus 链接")
    fingerprint: Optional[str] = Field(None, description="告警指纹，用于去重")

class AlertGroup(BaseModel):
    """
    Alertmanager 发送的 Webhook 顶层结构 (告警组)
    """
    version: str = Field(..., description="协议版本，通常是 '4'")
    groupKey: str = Field(..., description="用于分组的 Key")
    truncatedAlerts: int = Field(0, description="如果告警太多被截断的数量")
    status: str = Field(..., description="整体状态: firing 或 resolved")
    receiver: str = Field(..., description="Alertmanager 配置的接收者名称")
    groupLabels: Dict[str, str] = Field(default_factory=dict, description="分组标签")
    commonLabels: Dict[str, str] = Field(default_factory=dict, description="该组所有告警共有的标签")
    commonAnnotations: Dict[str, str] = Field(default_factory=dict, description="该组所有告警共有的注解")
    externalURL: str = Field(..., description="Alertmanager 的外部访问链接")
    alerts: List[Alert] = Field(..., description="具体的告警列表")

    class Config:
        json_schema_extra = {
            "example": {
                "version": "4",
                "groupKey": "{}:{alertname=\"HighMemory\"}",
                "status": "firing",
                "receiver": "aiops-agent",
                "groupLabels": {"alertname": "HighMemory"},
                "commonLabels": {"alertname": "HighMemory", "severity": "critical"},
                "commonAnnotations": {"summary": "Instance high memory usage"},
                "externalURL": "http://alertmanager:9093",
                "alerts": [
                    {
                        "status": "firing",
                        "labels": {"alertname": "HighMemory", "instance": "localhost:9090", "severity": "critical"},
                        "annotations": {"summary": "Instance high memory usage", "description": "Memory usage > 90%"},
                        "startsAt": "2024-01-01T10:00:00Z",
                        "endsAt": "0001-01-01T00:00:00Z",
                        "generatorURL": "http://prometheus:9090"
                    }
                ]
            }
        }
