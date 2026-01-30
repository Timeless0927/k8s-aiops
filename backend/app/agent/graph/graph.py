from langgraph.graph import StateGraph, END
from app.agent.graph.state import AgentState
from app.agent.graph.nodes.agent import agent_node
from app.agent.graph.nodes.tools import tool_node

def should_continue(state: AgentState):
    """
    Determine whether to traverse to tools or end.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check if the last message has tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

# Set entry point
workflow.set_entry_point("agent")

# Add edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

workflow.add_edge("tools", "agent")

# Compile
graph = workflow.compile()
