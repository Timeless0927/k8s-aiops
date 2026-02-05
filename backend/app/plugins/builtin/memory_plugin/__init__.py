from typing import List, Dict, Any
from app.services.memory_service import memory_service
from app.services.knowledge_service import knowledge_service

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

async def search_knowledge(query: str) -> str:
    """
    [Knowledge] Semantic search in the long-term knowledge base.
    """
    results = knowledge_service.query_similar(query_text=query, n_results=3)
    if not results:
        return "No relevant knowledge found."
    formatted = "Found relevant insights:\n"
    for r in results:
        formatted += f"- {r['content']} (Score: relevant)\n"
    return formatted

async def add_insight(content: str, category: str = "general") -> str:
    """
    [Knowledge] Save a valuable insight or solution.
    """
    success = knowledge_service.add_insight(content=content, metadata={"category": category})
    return "Insight saved." if success else "Failed to save."


# Plugin Definition
class Plugin:
    def __init__(self):
        self.manifest = {
            "name": "Memory & Knowledge",
            "version": "1.0.0",
            "description": "Agent's dual-layer memory system (Beads + ChromaDB)",
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
                "name": "search_knowledge",
                "description": "Search long-term knowledge base (ChromaDB)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                },
                "handler": search_knowledge
            },
            {
                "name": "add_insight",
                "description": "Save insight to long-term memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "The insight content"},
                        "category": {"type": "string", "description": "Category"}
                    },
                    "required": ["content"]
                },
                "handler": add_insight
            },
            {
                "name": "finish_task",
                "description": "Mark a task as completed and optionally archive learnings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "The ID of the task to close"},
                        "resolution_summary": {"type": "string", "description": "Summary of how it was solved (for long-term memory)"}
                    },
                    "required": ["task_id"]
                },
                "handler": finish_task
            }
        ]

async def finish_task(task_id: str, resolution_summary: str = "") -> str:
    """
    [Memory] Complete a task and archive it.
    """
    # 1. Close in Beads
    res = memory_service.complete_task(task_id, resolution=resolution_summary)
    
    # 2. Archive to ChromaDB if there's a resolution
    if resolution_summary:
        # Fetch task details for context
        task_details = memory_service.get_task_details(task_id)
        # Construct a full insight document
        insight_text = f"Task: {task_id}\nDetails: {task_details}\nResolution: {resolution_summary}"
        
        # Save to Knowledge
        knowledge_service.add_insight(content=insight_text, metadata={"source": "beads_archive", "task_id": task_id})
        return f"Task closed and resolution archived. ({res})"
    
    return f"Task closed. ({res})"

    def on_load(self):
        pass
