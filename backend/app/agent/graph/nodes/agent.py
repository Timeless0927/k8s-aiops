from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.services.plugin_manager import plugin_manager
from app.agent.graph.state import AgentState
from langchain_core.messages import SystemMessage

# Initialize Model
# We use a factory or global instance. For now global is fine as it's stateless request-wise.
llm = ChatOpenAI(
    model=settings.MODEL_NAME, 
    api_key=settings.OPENAI_API_KEY, 
    base_url=settings.OPENAI_BASE_URL,
    temperature=0.1
)

async def agent_node(state: AgentState):
    """
    Invokes the LLM with the current state messages and bound tools.
    """
    messages = state["messages"]
    
    # Get tools from enabled plugins
    tools_schema = plugin_manager.get_all_tools_schema()
    
    # Bind tools to the model
    # If no tools are available, we don't bind any.
    if tools_schema:
        model_with_tools = llm.bind_tools(tools_schema)
    else:
        model_with_tools = llm
    
    # Invoke the model asynchronously
    response = await model_with_tools.ainvoke(messages)
    
    # Return the new message to be appended to state
    return {"messages": [response]}
