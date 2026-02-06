from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.services.plugin_manager import plugin_manager
from app.agent.graph.state import AgentState
from langchain_core.messages import SystemMessage

from app.core.llm_config import LLMConfigManager
import logging

logger = logging.getLogger(__name__)

async def agent_node(state: AgentState):
    """
    Invokes the LLM with the current state messages and bound tools.
    """
    config = LLMConfigManager.get_config()
    
    if not config.api_key:
        return {"messages": [SystemMessage(content="❌ **Error**: OpenAI API Key is missing. Please configure it in System Settings.")]}
        
    llm = ChatOpenAI(
        model=config.model_name or "gpt-4-turbo", 
        api_key=config.api_key, 
        base_url=config.base_url,
        temperature=0.1
    )

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
    try:
        response = await model_with_tools.ainvoke(messages)
    except Exception as e:
        logger.error(f"LLM Invocation Failed: {e}")
        return {"messages": [SystemMessage(content=f"❌ **LLM Error**: {str(e)}")]}
    
    # Return the new message to be appended to state
    return {"messages": [response]}
