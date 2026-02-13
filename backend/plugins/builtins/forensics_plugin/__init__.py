from app.agent.plugin_interface import BasePlugin, PluginManifest
from typing import List, Dict, Any
from .tools import analyze_incident_logs

class ForensicsPlugin(BasePlugin):
    @property
    def manifest(self) -> PluginManifest:
        return {
            "name": "forensics_plugin",
            "version": "1.0.0",
            "description": "AI-powered log forensics and incident analysis.",
            "author": "System"
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "analyze_incident_logs",
                "description": "Analyze raw logs (from kubectl or Loki) to extract structured incident details (Root Cause, Fix). MUST be used after fetching logs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "log_content": {
                            "type": "string",
                            "description": "The raw log text to analyze."
                        }
                    },
                    "required": ["log_content"]
                },
                "handler": analyze_incident_logs
            }
        ]

Plugin = ForensicsPlugin
