from app.agent.plugin_interface import BasePlugin, PluginManifest
from typing import List, Dict, Any
from .tools import run_loki_query

class LokiPlugin(BasePlugin):
    @property
    def manifest(self) -> PluginManifest:
        return {
            "name": "loki_plugin",
            "version": "0.1.0",
            "description": "Query logs from Loki for troubleshooting.",
            "author": "System"
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "run_loki_query",
                "description": "Execute a LogQL query to search logs. Use this to find error messages, exceptions, or trace events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string", 
                            "description": "Valid LogQL query (e.g. '{app=\"foo\"} |= \"error\"')."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max number of log lines to return (default 10). Keep this small to save tokens."
                        },
                        "mode": {
                             "type": "string",
                             "enum": ["logs", "stats"],
                             "description": "Output mode. Use 'stats' first to get an overview. Use 'logs' to see actual content."
                        }
                    },
                    "required": ["query"]
                },
                "handler": run_loki_query
            }
        ]

Plugin = LokiPlugin
