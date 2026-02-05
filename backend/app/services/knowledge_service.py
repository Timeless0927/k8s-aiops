import os
import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid

# Try to import OpenAI for embedding, fallback to None or simple default if not configured
try:
    from app.core.config import settings
    OPENAI_API_KEY = settings.OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = None

logger = logging.getLogger(__name__)

class KnowledgeService:
    """
    Long-term Memory Service utilizing ChromaDB for semantic search.
    Stores insights, solutions, and historical context.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KnowledgeService, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        """Initialize ChromaDB client and collection."""
        try:
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "knowledge_base", 
                "chroma_db"
            )
            
            if not os.path.exists(self.db_path):
                os.makedirs(self.db_path)

            logger.info(f"Initializing ChromaDB at {self.db_path}")
            
            # Persistent Client
            self.client = chromadb.PersistentClient(path=self.db_path)
            
            # Get or Create Collection
            # We use distinct collections for different types of knowledge if needed.
            # For now, a single "insights" collection.
            # Note: We rely on default embedding function (all-MiniLM-L6-v2) built-in to Chroma
            # or we can pass an OpenAI function if we want better quality.
            
            # Using default for simplicity & offline capability first. 
            # If OpenAI key is present, we could switch.
            self.collection = self.client.get_or_create_collection(name="aiops_insights")
            
        except Exception as e:
            logger.error(f"Failed to init ChromaDB: {e}")
            self.client = None
            self.collection = None

    def add_insight(self, content: str, metadata: Dict[str, str] = None) -> bool:
        """
        Add a piece of knowledge to the DB.
        """
        if not self.collection:
            logger.warning("ChromaDB collection not available.")
            return False
            
        try:
            doc_id = str(uuid.uuid4())
            if metadata is None:
                metadata = {}
            
            # Add timestamp
            import datetime
            metadata["created_at"] = datetime.datetime.now().isoformat()
            
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.info(f"Added insight to ChromaDB: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding insight: {e}")
            return False

    def query_similar(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """
        Semantic search for insights.
        """
        if not self.collection:
            return []
            
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Transform results to friendly format
            # Chroma returns: {'ids': [['id1']], 'documents': [['text1']], ...}
            formatted_results = []
            
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "id": results['ids'][0][i]
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying insights: {e}")
            return []

# Global Instance
knowledge_service = KnowledgeService()
