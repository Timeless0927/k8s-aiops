from typing import TypedDict, Annotated, List, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The state of the agent graph.
    """
    # Messages list that supports appending via add_messages reducer
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Extract K8s context (e.g. namespace, pod name)
    k8s_context: Dict[str, Any]
    
    # Error tracking for self-correction
    error_count: int
    
    # Current active tool output (optional, mostly handled by messages but can be explicit if needed)
    # tool_output: str | None
