from abc import ABC, abstractmethod
from typing import List, Dict, Any, TypedDict, Optional

class PluginManifest(TypedDict):
    name: str
    version: str
    description: str
    author: Optional[str]

class BasePlugin(ABC):
    """
    Abstract Base Class for all K8s AIOps Agents Plugins.
    """

    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """
        Returns metadata about the plugin.
        """
        pass

    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Returns a list of tool definitions compatible with LangChain/OpenAI.
        Each tool should have: name, description, parameters, and handler.
        """
        pass

    def on_load(self) -> None:
        """
        Lifecycle hook: Called when the plugin is loaded.
        Use this to initialize resources (db connections, etc).
        """
        pass

    def on_unload(self) -> None:
        """
        Lifecycle hook: Called when the plugin is unloaded.
        Use this to clean up resources.
        """
        pass
