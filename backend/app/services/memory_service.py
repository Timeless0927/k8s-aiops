import os
import subprocess
import logging
import json
from typing import List, Dict, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class BeadsMemoryService:
    """
    Wrapper for Steve Yegge's Beads (Graph-based Memory)
    Maintains a local, isolated Git repository to store Agent tasks and memories.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BeadsMemoryService, cls).__new__(cls)
            # 存储在 knowledge_base/memory_store 下，避免污染主仓库
            cls._instance.repo_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "knowledge_base", 
                "memory_store"
            )
            cls._instance._ensure_repo_initialized()
        return cls._instance

    def _ensure_repo_initialized(self):
        """Ensure the local git repo for beads exists."""
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)
        
        # Check if it has .git
        if not os.path.exists(os.path.join(self.repo_path, ".git")):
            logger.info(f"Initializing Beads Memory Repo at {self.repo_path}")
            try:
                subprocess.run(["git", "init"], cwd=self.repo_path, check=True, capture_output=True)
                # Config User for this local repo (required for commits)
                subprocess.run(["git", "config", "user.email", "agent@aiops.local"], cwd=self.repo_path, check=True)
                subprocess.run(["git", "config", "user.name", "AIOps Agent"], cwd=self.repo_path, check=True)
                
                # Create initial structure
                with open(os.path.join(self.repo_path, "README.md"), "w", encoding='utf-8') as f:
                    f.write("# AIOps Agent Memory Store\n\nManaged by Beads.")
                
                self._git_commit("Initial Commit")
            except Exception as e:
                logger.error(f"Failed to init beads repo: {e}")

    def _run_cli(self, args: List[str]) -> str:
        """Execute a bd CLI command in the repo directory."""
        try:
            # Command is 'bd' (from beads-project)
            cmd = ["bd"] + args
            logger.info(f"Executing Beads CLI: {' '.join(cmd)}")
            
            # 必须设置 CWD 到仓库目录
            result = subprocess.run(
                cmd, 
                cwd=self.repo_path, 
                capture_output=True, 
                text=True, 
                check=True,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"}
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Beads CLI Error: {e.stderr}")
            # Don't raise immediately, log and return empty so Agent doesn't crash
            return f"Error: {e.stderr}"
        except FileNotFoundError:
            logger.error("'bd' executable not found. Ensure 'beads-project' is installed.")
            return "Error: Command 'bd' not found."

    def _ensure_repo_initialized(self):
        """Ensure the local git repo for beads exists and is initialized."""
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)
            
        # Check if .beads directory exists (Beads structure)
        if not os.path.exists(os.path.join(self.repo_path, ".beads")):
            logger.info(f"Initializing Beads Memory Repo at {self.repo_path}")
            try:
                # 使用 bd init
                # 注意: 我们是在 memory_store 目录下 init，所以它是独立的
                self._run_cli(["init"])
                
                # 配置 User (Beads 可能依赖 git config)
                subprocess.run(["git", "config", "user.email", "agent@aiops.local"], cwd=self.repo_path, check=False)
                subprocess.run(["git", "config", "user.name", "AIOps Agent"], cwd=self.repo_path, check=False)
            except Exception as e:
                logger.error(f"Failed to init beads repo: {e}")

    def create_task(self, title: str, description: str = "", priority: str = "1") -> str:
        """
        Create a task: bd create "Title" -p <P> -d "Desc"
        """
        args = ["create", title]
        
        # Priority map (0=High, 1=Medium, 2=Low etc.)
        # Agent might pass "high", "medium", so we map it.
        p_map = {"high": "0", "medium": "1", "low": "2"}
        p_val = p_map.get(priority.lower(), priority) # Default to passing raw if not mapped
        args.extend(["-p", p_val])
        
        if description:
            args.extend(["-d", description])
            
        output = self._run_cli(args)
        # Parse Output to find ID. E.g. "Created task bd-1a2b"
        task_id = self._extract_id_from_output(output)
            
        return task_id or output

    def get_ready_tasks(self) -> str:
        """
        List actionable tasks: bd ready
        """
        return self._run_cli(["ready"])

    def complete_task(self, task_id: str, resolution: str = "") -> str:
        """
        Mark a task as done: bd close <id>
        """
        # Close the task
        output = self._run_cli(["close", task_id])
        
        # Optionally add resolution description if supported by beads or just log it
        # Beads tasks are just jsonl, so 'close' might just switch status.
        # We assume the user might want to record HOW it was solved.
        # We can append a comment or just return success.
        
        return output

    def get_task_details(self, task_id: str) -> str:
        """
        View task: bd show <id>
        """
        return self._run_cli(["show", task_id])

    def _extract_id_from_output(self, output: str) -> Optional[str]:
        # Simple parser for "bd-xxxx"
        import re
        match = re.search(r"(bd-[a-zA-Z0-9\.]+)", output)
        if match:
            return match.group(1)
        return None

# Global Instance
memory_service = BeadsMemoryService()
