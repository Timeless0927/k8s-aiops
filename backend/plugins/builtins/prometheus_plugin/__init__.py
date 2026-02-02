from app.agent.plugin_interface import BasePlugin, PluginManifest
from typing import List, Dict, Any
from .tools import run_prometheus_query

class PrometheusPlugin(BasePlugin):
    @property
    def manifest(self) -> PluginManifest:
        return {
            "name": "prometheus_plugin",
            "version": "0.1.0",
            "description": "Query metrics from Prometheus for performance analysis.",
            "author": "System"
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "run_prometheus_query",
                "description": "Execute a PromQL query to retrieve metrics. Returns JSON list of metric values. Use this to check CPU, Memory, or Application specific metrics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Valid PromQL query (e.g. 'sum(rate(container_cpu_usage_seconds_total[5m]))')."
                        }
                    },
                    "required": ["query"]
                },
                "handler": run_prometheus_query
            }
        ]

Plugin = PrometheusPlugin
