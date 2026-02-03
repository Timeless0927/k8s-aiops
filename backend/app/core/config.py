import os
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    系统配置 (Settings)
    读取环境变量，如果不设置则使用默认值。
    """
    # 基础配置
    APP_NAME: str = "K8s AIOps Agent"
    ENV: str = Field("dev", env="ENV")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    
    # Prometheus & Loki
    PROMETHEUS_URL: str = Field("http://prometheus-k8s.monitoring:9090", env="PROMETHEUS_URL")
    LOKI_URL: str = Field("http://loki.monitoring:3100", env="LOKI_URL")
    GRAFANA_URL: str = Field("http://grafana.monitoring:3000", env="GRAFANA_URL")
    
    # Kubernetes
    # 如果在集群内运行，通常不需要配置 KUBECONFIG，使用 ServiceAccount
    KUBE_IN_CLUSTER: bool = Field(True, env="KUBE_IN_CLUSTER")
    KUBECONFIG: str | None = Field(None, env="KUBECONFIG")

    # Database
    DATABASE_URL: str = Field("sqlite+aiosqlite:///./app.db", env="DATABASE_URL")
    
    # LLM (External API)
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_BASE_URL: str = Field("https://api.openai.com/v1", env="OPENAI_BASE_URL")
    MODEL_NAME: str = Field("gpt-4-1106-preview", env="MODEL_NAME")

    class Config:
        # Prioritize root .env, then backend/.env
        env_file = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env"), # Root
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env") # Backend
        ]
        extra = "ignore"

# 单例配置对象
settings = Settings()
