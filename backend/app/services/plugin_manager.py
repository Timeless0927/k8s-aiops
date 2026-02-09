import os
import importlib.util
import sys
import logging
import shutil
import zipfile
from typing import Dict, List, Any

# DB Imports
from app.db.session import AsyncSessionLocal
from app.services.plugin_store import PluginStoreService

logger = logging.getLogger(__name__)

class PluginManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginManager, cls).__new__(cls)
            cls._instance.plugins = {}  # name -> module
            cls._instance.plugin_metadata = {} # name -> metadata dict
            cls._instance.tools_registry = {}  # tool_name -> handler
            cls._instance.tools_schema = []   # OpenAI Format Schemas
            # Default paths
            cls._instance.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../plugins"))
            cls._instance.builtins_path = os.path.join(cls._instance.base_path, "builtins")
            
            # User uploads path - Configurable for persistence
            default_user_path = os.path.join(cls._instance.base_path, "user_uploads")
            cls._instance.user_path = os.getenv("USER_PLUGIN_PATH", default_user_path)
            
            # Ensure directory exists if using custom path
            if not os.path.exists(cls._instance.user_path):
                try:
                    os.makedirs(cls._instance.user_path)
                except OSError:
                    pass # Might be read-only or handled later
        return cls._instance

    async def initialize(self):
        """Async Initialization: Sync DB state and load plugins."""
        await self.reload_all()

    async def reload_all(self):
        """Clear and reload all plugins."""
        self.plugins = {}
        self.plugin_metadata = {}
        self.tools_registry = {}
        self.tools_schema = []
        
        # Load builtins
        await self._load_from_directory(self.builtins_path, is_builtin=True)
        
        # Load user_uploads 
        if os.path.exists(self.user_path):
            await self._load_from_directory(self.user_path, is_builtin=False)
            
        logger.info(f"PluginManager reloaded. Plugins: {len(self.plugins)}, Tools: {len(self.tools_schema)}")

    async def _load_from_directory(self, directory: str, is_builtin: bool = False):
        if not os.path.isdir(directory):
            return

        for item in os.listdir(directory):
            plugin_path = os.path.join(directory, item)
            # Skip python cache or hidden files
            if item.startswith("__") or item.startswith("."):
                continue
                
            if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, "__init__.py")):
                await self.load_plugin(plugin_path, is_builtin)

    async def load_plugin(self, path: str, is_builtin: bool):
        """Dynamic load a python module from path."""
        name = os.path.basename(path)
        
        # Check DB Status
        async with AsyncSessionLocal() as session:
            plugin_state = await PluginStoreService.ensure_plugin_exists(session, name)
            is_enabled = plugin_state.enabled
            # Native builtins (like kubectl) might default to enabled if logic requires
            # But ensure_plugin_exists defaults new ones to False.
            # Maybe builtins should default to True?
            # For now, let's respect DB (first run will be False unless we logic it)
            # CHANGE: Make builtins default True if first time?
            # Implemented in ensure_plugin_exists? No.
            # Let's simple check: if builtin and not explicit disabled?
            # Current logic: DB source of truth.
        
        # Override for essential builtins if needed (e.g. kubectl_plugin should be active)
        # For this MVP, let's assume manual enablement or default False except core.
        
        try:
            # 1. Load Spec
            spec = importlib.util.spec_from_file_location(name, os.path.join(path, "__init__.py"))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                
            # 2. Check Protocol (Hybrid Support)
            manifest = None
            tools_list = []
            plugin_instance = None

            # A. Class-Based Plugin (New Standard)
            if hasattr(module, "Plugin") and isinstance(module.Plugin, type):
                # Instantiate the plugin
                plugin_instance = module.Plugin()
                if hasattr(plugin_instance, "manifest") and hasattr(plugin_instance, "get_tools"):
                     manifest = plugin_instance.manifest
                     tools_list = plugin_instance.get_tools()
                     # Call lifecycle hook
                     if is_enabled:
                         plugin_instance.on_load()
            
            # B. Functional Plugin (Legacy Support)
            elif hasattr(module, "get_tools") and hasattr(module, "get_manifest"):
                manifest = module.get_manifest()
                tools_list = module.get_tools()

            if manifest:
                manifest["id"] = name
                manifest["is_builtin"] = is_builtin
                manifest["status"] = "active" if is_enabled else "disabled"
                
                self.plugin_metadata[name] = manifest
                
                if is_enabled:
                    # Store instance or module? Let's store module for legacy, instance for new
                    self.plugins[name] = plugin_instance if plugin_instance else module
                    
                    # 3. Register Tools
                    self._register_tools(tools_list, plugin_name=name)
                    logger.info(f"Loaded plugin: {name} (Class-based: {bool(plugin_instance)})")
                else:
                    logger.info(f"Plugin {name} is disabled. Skipping tool registration.")
            else:
                logger.warning(f"Skipping {name}: Invalid plugin structure (Missing manifest/tools)")
        except Exception as e:
            logger.error(f"Failed to load plugin {path}: {e}")
            self.plugin_metadata[name] = {
                "id": name,
                "name": name,
                "status": "error",
                "error": str(e),
                "is_builtin": is_builtin
            }

    def _register_tools(self, tools_list: List[Dict], plugin_name: str):
        for tool in tools_list:
            name = tool["name"]
            # 1. Register Schema (OpenAI Format)
            schema = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            self.tools_schema.append(schema)
            
            # 2. Register Handler
            self.tools_registry[name] = tool["handler"]

    async def toggle_plugin(self, plugin_id: str, active: bool):
        """Enable or disable a plugin."""
        if plugin_id not in self.plugin_metadata:
            raise ValueError("Plugin not found")
        
        async with AsyncSessionLocal() as session:
            await PluginStoreService.set_plugin_enabled(session, plugin_id, active)
        
        # Reload to apply changes
        await self.reload_all() 

    def list_plugins(self) -> List[Dict]:
        """Return list of all plugins and their status."""
        return list(self.plugin_metadata.values())

    async def install_plugin(self, file_path: str):
        """Install a plugin from a zip file."""
        if not zipfile.is_zipfile(file_path):
            raise ValueError("Invalid zip file")
            
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            if not file_list:
                 raise ValueError("Empty zip file")
            
            root_folder = file_list[0].split('/')[0]
            if not root_folder or root_folder.startswith("__") or root_folder.startswith("."):
                 raise ValueError("Invalid plugin structure: Root folder not found")
            
            target_path = os.path.join(self.user_path, root_folder)
            
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
                
            zip_ref.extractall(self.user_path)
            
            if not os.path.exists(os.path.join(target_path, "__init__.py")):
                shutil.rmtree(target_path)
                raise ValueError("Invalid plugin: Missing __init__.py")
            
            await self.reload_all()
            return root_folder

    def delete_plugin(self, plugin_id: str):
        # Async deletion logic?
        # Actually file IO is sync here (shutil), maybe safe enough or wrap in loop.run_in_executor
        pass # TODO implementation if needed, stick to sync for now or upgrade later.
        # But wait, delete_plugin was reusing reload_all which is now async.
        # So this must be async too.
        raise NotImplementedError("Async delete not implemented yet")

    async def delete_plugin_async(self, plugin_id: str):
        """Delete a user plugin."""
        logger.info(f"Attempting to delete plugin: {plugin_id}")
        
        if plugin_id in self.plugin_metadata and self.plugin_metadata[plugin_id].get("is_builtin"):
            raise ValueError("Cannot delete builtin plugins")
            
        target_path = os.path.join(self.user_path, plugin_id)
        if os.path.exists(target_path):
            # 1. Try to unload from sys.modules
            if plugin_id in sys.modules:
                del sys.modules[plugin_id]
                logger.info(f"Unloaded {plugin_id} from sys.modules")
            
            # 2. Define robust error handler for Windows
            def on_rm_error(func, path, exc_info):
                import stat
                # Attempt to make writable
                try:
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                except Exception as e:
                    logger.warning(f"Failed to force delete {path}: {e}")

            # 3. Delete
            try:
                shutil.rmtree(target_path, onerror=on_rm_error)
                logger.info(f"Deleted directory: {target_path}")
            except Exception as e:
                logger.error(f"shutil.rmtree failed: {e}")
                raise ValueError(f"Failed to delete plugin files: {e}")

            await self.reload_all()
            return True
            
        logger.warning(f"Plugin path not found: {target_path}")
        return False

    def get_all_tools_schema(self):
        return self.tools_schema

    def get_tool_handler(self, name: str):
        return self.tools_registry.get(name)
        
    def get_active_plugins(self) -> Dict[str, Dict]:
        """Return metadata for all active/enabled plugins."""
        return {
            name: self.plugin_metadata.get(name, {})
            for name in self.plugins.keys()
        }

# Global Instance
plugin_manager = PluginManager()
