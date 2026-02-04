import os
import glob
import logging
import yaml
import uuid
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Base path for knowledge base
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../knowledge_base"))
INSIGHTS_DB_PATH = os.path.join(BASE_PATH, "insights/insights_db.yaml")

def _get_file_path(filename: str) -> str:
    """Securely resolve file path."""
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        raise ValueError("Invalid filename")
    return os.path.join(BASE_PATH, filename)

def _load_insights() -> List[Dict]:
    """Load insights from YAML db."""
    if not os.path.exists(INSIGHTS_DB_PATH):
        return []
    try:
        with open(INSIGHTS_DB_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            return data.get('insights', [])
    except Exception as e:
        logger.error(f"Failed to load insights db: {e}")
        return []

def _save_insights_db(insights: List[Dict]):
    """Save insights to YAML db."""
    try:
        os.makedirs(os.path.dirname(INSIGHTS_DB_PATH), exist_ok=True)
        with open(INSIGHTS_DB_PATH, 'w', encoding='utf-8') as f:
            yaml.dump({'insights': insights}, f, allow_unicode=True, sort_keys=False)
    except Exception as e:
        logger.error(f"Failed to save insights db: {e}")

def search_knowledge(query: str, category: str = "all") -> str:
    """
    Search structured insights (YAML) and static docs (Markdown).
    """
    results = []
    query_lower = query.lower()

    # 1. Search Structured Insights (YAML)
    if category in ["all", "insights"]:
        insights = _load_insights()
        for item in insights:
            # Prepare search blob
            text_blob = f"{item.get('topic','')} {item.get('symptoms','')} {item.get('root_cause','')} {','.join(item.get('tags',[]))}".lower()
            
            # A. Exact Phase Match
            if query_lower in text_blob:
                results.append(f"[Insight] {item.get('topic')} (Matches: {item.get('symptoms', '')[:50]}...)\n  Solution: {item.get('solution')}")
                continue

            # B. Keyword Match (Fallback) - if query has spaces
            keywords = query_lower.split()
            if len(keywords) > 1:
                # Count matches
                matches = sum(1 for k in keywords if k in text_blob)
                # If > 50% keywords match (or at least 2), consider it a hit
                if matches >= len(keywords) * 0.5 or matches >= 2:
                     results.append(f"[Insight] {item.get('topic')} (Keyword Match: {matches}/{len(keywords)})\n  Solution: {item.get('solution')}")

    # 2. Search Static Docs (Markdown) - e.g. SOPs
    if category in ["all", "sops"]:
        search_pattern = f"{BASE_PATH}/**/*.md"
        files = glob.glob(search_pattern, recursive=True)
        for file_path in files:
            # Skip if it's the DB itself or learned_fixes legacy
            if "insights_db.yaml" in file_path or "learned_fixes.md" in file_path:
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if query_lower in content.lower() or query_lower in os.path.basename(file_path).lower():
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
        path = _get_file_path(filename)
        if not os.path.exists(path):
            return f"Error: File '{filename}' not found."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading: {e}"

def save_insight(topic: str, content: str, symptoms: str = "", root_cause: str = "", tags: List[str] = []) -> str:
    """
    Save a structured insight with deduplication.
    """
    insights = _load_insights()
    
    # Simple Deduplication: Check if topic is very similar
    topic_lower = topic.lower().strip()
    existing = next((i for i in insights if i.get('topic', '').lower().strip() == topic_lower), None)
    
    if existing:
        # Update existing
        existing['count'] = existing.get('count', 1) + 1
        existing['last_seen'] = datetime.now().isoformat()
        # Merge tags
        existing_tags = set(existing.get('tags', []))
        existing_tags.update(tags)
        existing['tags'] = list(existing_tags)
        
        _save_insights_db(insights)
        return f"Insight '{topic}' already exists. Updated occurrence count to {existing['count']}."
    else:
        # Create new
        new_entry = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "topic": topic,
            "content": content, # Legacy field, maybe keep for solution details
            "symptoms": symptoms,
            "root_cause": root_cause,
            "solution": content, # Mapping content to solution for clarity
            "tags": tags,
            "count": 1
        }
        insights.append(new_entry)
        _save_insights_db(insights)
        return f"Successfully saved new insight: {topic}"
