from app.services.plugin_manager import plugin_manager
import logging

# Note: plugin_manager must be initialized asynchronously in main.py startup event.
# These will be populated after initialization.

# Helper to get current tools (dynamic)
def get_tools_schema():
    return plugin_manager.get_all_tools_schema()

def get_tool_handler(name):
    return plugin_manager.get_tool_handler(name)

# Deprecated: Static access (might be empty before init)
TOOLS_SCHEMA = plugin_manager.tools_schema
AVAILABLE_TOOLS = plugin_manager.tools_registry
