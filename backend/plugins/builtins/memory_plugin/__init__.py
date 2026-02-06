from typing import List, Dict, Any
from app.services.memory_service import memory_service
from app.agent.plugin_interface import BasePlugin, PluginManifest

# Define Tools Handlers
async def create_task(title: str, description: str = "", priority: str = "1") -> str:
    """
    [Memory] Create a new tracking task in the Agent's working memory (Beads).
    """
    return memory_service.create_task(title=title, description=description, priority=priority)

async def get_my_tasks() -> str:
    """
    [Memory] Get a list of currently actionable tasks.
    """
    return memory_service.get_ready_tasks()

async def finish_task(task_id: str, resolution_summary: str = "") -> str:
    """
    [Memory] Complete a task and archive it.
    """
    # 1. Close in Beads
    res = memory_service.complete_task(task_id, resolution=resolution_summary)
    return f"Task closed. ({res})"

class MemoryPlugin(BasePlugin):
    @property
    def manifest(self) -> PluginManifest:
        return {
            "name": "memory_plugin",
            "version": "1.0.0",
            "description": "Agent's Short-Term Working Memory (Beads). Tracks active tasks.",
            "author": "AIOps Team"
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "create_task",
                "description": "Create a new task in working memory (Beads)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "description": {"type": "string", "description": "Details"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"], "default": "medium"}
                    },
                    "required": ["title"]
                },
                "handler": create_task
            },
            {
                "name": "get_my_tasks",
                "description": "List actionable tasks from working memory",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "handler": get_my_tasks
            },
            {
                "name": "finish_task",
                "description": "Mark a task as completed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "The ID of the task to close"},
                        "resolution_summary": {"type": "string", "description": "Summary of how it was solved"}
                    },
                    "required": ["task_id"]
                },
                "handler": finish_task
            }
        ]

Plugin = MemoryPlugin
