from app.agent.plugin_interface import BasePlugin, PluginManifest
from typing import List, Dict, Any
from .tools import search_knowledge, read_knowledge, save_insight

class KnowledgePlugin(BasePlugin):
    @property
    def manifest(self) -> PluginManifest:
        return {
            "name": "knowledge_plugin",
            "version": "1.0.0",
            "description": "Access to long-term memory (SOPs, Insights).",
            "author": "System"
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "search_knowledge",
                "description": "Search the knowledge base for existing solutions, SOPs, or past experiences. Use this BEFORE trying to solve complex errors.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Keywords to search for (e.g. 'kafka connection', 'error 500')."
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional filter: 'sops', 'insights', or 'all' (default)."
                        }
                    },
                    "required": ["query"]
                },
                "handler": search_knowledge
            },
            {
                "name": "read_knowledge",
                "description": "Read the full content of a specific knowledge document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The relative path of the file to read (returned by search_knowledge)."
                        }
                    },
                    "required": ["filename"]
                },
                "handler": read_knowledge
            },
            {
                "name": "save_insight",
                "description": "Save a new learned lesson or fix to long-term memory. Use this AFTER successfully solving a difficult problem.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Brief title of the insight (e.g. 'Fix for CrashLoopBackOff')."
                        },
                        "content": {
                            "type": "string",
                            "description": "Detailed description of the problem and resolution."
                        }
                    },
                    "required": ["topic", "content"]
                },
                "handler": save_insight
            }
        ]

Plugin = KnowledgePlugin
