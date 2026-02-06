import os
import glob
import logging
from typing import List, Dict, Any
from datetime import datetime
from app.services.knowledge_service import knowledge_service

logger = logging.getLogger(__name__)

# Base path for knowledge base (for static markdown docs search only)
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../knowledge_base"))

def search_knowledge(query: str, category: str = "all") -> str:
    """
    Search structured insights (ChromaDB) and static docs (Markdown).
    """
    results = []
    
    # 1. Search ChromaDB (Structured Insights)
    if category in ["all", "insights"]:
        try:
            chroma_results = knowledge_service.query_similar(query, n_results=5)
            for r in chroma_results:
                # Format: [Insight] <Content> (Meta: ...)
                # Content in Chroma is usually the full text.
                # We try to extract topic from content or metadata if possible, but for now just show content.
                # If metadata has 'topic', use it.
                meta = r.get("metadata", {})
                topic = meta.get("topic", "Insight")
                content_preview = r.get("content", "")[:200]
                
                results.append(f"[Insight] {topic}\n{content_preview}...")
        except Exception as e:
            logger.error(f"Chroma search failed: {e}")

    # 2. Search Static Docs (Markdown) - e.g. SOPs
    if category in ["all", "sops"]:
        search_pattern = f"{BASE_PATH}/**/*.md"
        files = glob.glob(search_pattern, recursive=True)
        for file_path in files:
            # Skip db/legacy files
            if "insights_db.yaml" in file_path or "learned_fixes.md" in file_path:
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if query.lower() in content.lower():
                    rel_path = os.path.relpath(file_path, BASE_PATH)
                    results.append(f"[File] {rel_path}")
            except Exception:
                pass
            
    if not results:
        return "No matching knowledge found."
    
    return "\n---\n".join(results[:5])

def read_knowledge(filename: str) -> str:
    """Read full content of a file."""
    try:
        # Secure path check
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            return "Error: Invalid filename"
            
        path = os.path.join(BASE_PATH, filename)
        if not os.path.exists(path):
            return f"Error: File '{filename}' not found."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading: {e}"

def save_insight(topic: str, content: str, symptoms: str = "", root_cause: str = "", tags: List[str] = []) -> str:
    """
    Save a structured insight to ChromaDB.
    """
    # Construct a rich text representation for embedding
    full_text = f"""Topic: {topic}
Symptoms: {symptoms}
Root Cause: {root_cause}
Solution/Content: {content}
Tags: {', '.join(tags)}
"""
    
    # Metadata for filtering/retrieval
    metadata = {
        "topic": topic,
        "symptoms": symptoms[:100], # Limit length for metadata
        "root_cause": root_cause[:100],
        "tags": ",".join(tags),
        "source": "auto_save_insight"
    }
    
    success = knowledge_service.add_insight(content=full_text, metadata=metadata)
    
    if success:
        return f"Successfully saved insight to ChromaDB: {topic}"
    else:
        return "Failed to save insight to ChromaDB."
