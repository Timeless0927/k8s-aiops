import os
import glob
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Base path for knowledge base
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../knowledge_base"))

def _get_file_path(filename: str) -> str:
    """Securely resolve file path."""
    # Simple security check to prevent directory traversal
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        raise ValueError("Invalid filename")
    return os.path.join(BASE_PATH, filename)

def search_knowledge(query: str, category: str = "all") -> str:
    """
    Search markdown files in knowledge_base for the query string.
    """
    results = []
    
    # Define search paths
    search_pattern = f"{BASE_PATH}/**/*.md"
    files = glob.glob(search_pattern, recursive=True)
    
    query_lower = query.lower()
    
    for file_path in files:
        if category != "all" and category not in file_path:
            continue
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if query_lower in content.lower() or query_lower in os.path.basename(file_path).lower():
                # Get snippet
                idx = content.lower().find(query_lower)
                start = max(0, idx - 50)
                end = min(len(content), idx + 150)
                snippet = content[start:end].replace("\n", " ")
                
                rel_path = os.path.relpath(file_path, BASE_PATH)
                results.append(f"- [{rel_path}]: ...{snippet}...")
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            
    if not results:
        return "No matching knowledge found."
    
    return "\n".join(results[:5]) # Limit to 5 results

def read_knowledge(filename: str) -> str:
    """
    Read full content of a knowledge file.
    """
    try:
        path = _get_file_path(filename)
        if not os.path.exists(path):
            return f"Error: File '{filename}' not found."
            
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def save_insight(topic: str, content: str) -> str:
    """
    Append a learned insight to the insights directory.
    """
    try:
        filename = "insights/learned_fixes.md"
        path = _get_file_path(filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Check if file exists to add header
        is_new = not os.path.exists(path)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(path, "a", encoding="utf-8") as f:
            if is_new:
                f.write(f"# Learned Insights\n\n")
            
            f.write(f"## [{timestamp}] {topic}\n{content}\n\n")
            
        return f"Successfully saved insight to {filename}"
    except Exception as e:
        return f"Error saving insight: {str(e)}"
