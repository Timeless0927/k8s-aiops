import os
import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Tuple
import uuid
import langextract as lx
from langextract.data import ExampleData, Extraction
from langextract import factory
from app.core.llm_config import LLMConfigManager

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
            # Allow override via ENV, else use default relative path
            default_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "knowledge_base", 
                "chroma_db"
            )
            self.db_path = os.getenv("KNOWLEDGE_BASE_PATH", default_path)
            
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
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying insights: {e}")
            return []

    def ingest_fault_report(self, report_text: str, source: str = "user_upload") -> Tuple[Dict[str, str], str]:
        """
        Structure a raw fault report using LangExtract and store it in ChromaDB.
        Returns: (Structured Data Dict, Error Message)
        """
        config = LLMConfigManager.get_config()
        if not config.api_key:
            return {}, "OpenAI API Key is missing in configuration."

        try:
            # 1. Define Schema via Example (One-Shot)
            example = ExampleData(
                text="Yesterday 10pm payment service down due to connection pool saturation. We restarted pods and added circuit breaker. Recovered at 11pm.",
                extractions=[Extraction(
                    extraction_class="FaultReport",
                    extraction_text="payment service down due to connection pool saturation",
                    attributes={
                        "symptom": "Payment service down, connection pool saturated",
                        "action": "Restarted pods, added circuit breaker",
                        "outcome": "Recovered at 11pm"
                    }
                )]
            )
            
            # 2. Configure Model
            # We use OpenAI for reasoning capability, but support custom BaseURL/Model
            model_config = factory.ModelConfig(
                provider="openai",
                model_id=config.model_name or "gpt-4-turbo",
                provider_kwargs={
                    "api_key": config.api_key,
                    "base_url": config.base_url
                }
            )

            # 3. Extract
            extracted_docs = lx.extract(
                text_or_documents=report_text,
                prompt_description="Extract fault details (Symptom, Action, Outcome) from this post-mortem report.",
                examples=[example],
                config=model_config,
                format_type="json",
                use_schema_constraints=False
            )

            # 4. Process Result
            structured_data = {}
            if extracted_docs:
                if isinstance(extracted_docs, list):
                    doc = extracted_docs[0]
                else:
                    doc = extracted_docs

                if doc.extractions:
                    ext = doc.extractions[0]
                    structured_data = ext.attributes or {}

            if not structured_data:
                logger.warning("No structure extracted from report.")
                return {}, "No structure extracted from report (LLM returned empty)."

            # 5. Format for Knowledge Base
            # We store a clean, semantic string for embedding search
            kb_content = (
                f"Symptom: {structured_data.get('symptom', 'N/A')}\n"
                f"Action: {structured_data.get('action', 'N/A')}\n"
                f"Outcome: {structured_data.get('outcome', 'N/A')}"
            )
            
            metadata = {
                "type": "fault_report",
                "source": source,
                "original_length": str(len(report_text))
            }

            success = self.add_insight(kb_content, metadata)
            
            if success:
                return structured_data, None
            else:
                return {}, "Failed to store insight in ChromaDB."

        except Exception as e:
            error_msg = f"Ingestion failed: {e}"
            logger.error(error_msg)
            return {}, error_msg

# Global Instance
knowledge_service = KnowledgeService()
