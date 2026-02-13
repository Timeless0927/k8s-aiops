import logging
import json
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
import langextract as lx
from app.core.llm_config import LLMConfigManager

logger = logging.getLogger(__name__)

# --- Schemas ---
class Evidence(BaseModel):
    summary: str = Field(description="Summary of the evidence found in logs")
    raw_text: str = Field(description="Exact quote from the log")

class Incident(BaseModel):
    incident_type: str = Field(description="Type of the incident e.g., OOM, Timeout, Crash")
    severity: str = Field(description="Severity level: High, Medium, Low")
    root_cause: str = Field(description="The underlying cause of the issue")
    suggestion: str = Field(description="Actionable fix suggestion")
    evidences: List[Evidence] = Field(description="List of supporting evidences from logs")

# --- Service ---
class LogForensicsService:
    @staticmethod
    def analyze_logs(log_text: str) -> Tuple[Optional[dict], Optional[str]]:
        """
        Analyze logs using LangExtract.
        Returns: (Structured Data Dict, HTML Visualization Code)
        """
        config = LLMConfigManager.get_config()
        api_key = config.api_key
        
        # Fallback to system env if config manager fails (consistent with LangChain)
        if not api_key:
            import os
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logger.error("LLM API Key missing")
            return None, None

        try:
            # Initialize Extractor
            # Note: LangExtract might need specific provider config. 
            # Assuming it supports OpenAI via standard env vars or explicit init.
            # For now, we use the default generic setup which usually auto-detects.
            # Real implementation might need specific 'provider="openai"' args.
            
            # Define Examples (Required by langextract)
            from langextract.data import ExampleData, Extraction
            from langextract import factory
            
            # Create a 1-shot example using Extraction objects
            # note: extraction_class should match what we want the model to produce
            example = ExampleData(
                text="2024-01-01 12:00:00 [error] java.lang.OutOfMemoryError: Java heap space",
                extractions=[Extraction(
                    extraction_class="Incident",
                    extraction_text="java.lang.OutOfMemoryError: Java heap space",
                    attributes={
                        "incident_type": "OOM",
                        "severity": "High",
                        "root_cause": "Java Heap Space Exhausted",
                        "suggestion": "Increase Heap Size",
                        "evidence_summary": "OOM Error"
                    }
                )]
            )

            # Configure Model explicitly to avoid Ollama fallback
            # defaulting to openai provider
            
            provider_kwargs = {
                "api_key": api_key
            }
            if config.base_url:
                provider_kwargs["base_url"] = config.base_url
                
            model_config = factory.ModelConfig(
                provider="openai",
                model_id=config.model_name or "gpt-4-turbo",
                provider_kwargs=provider_kwargs
            )

            # Run Extraction
            extracted_docs = lx.extract(
                text_or_documents=log_text,
                prompt_description="You are a K8s Expert. Extract incident details (Incident) from these logs.",
                examples=[example],
                config=model_config,
                format_type="json",
                use_schema_constraints=False
            )

            # Generate Visualization
            html_viz = lx.visualize(extracted_docs)
            
            # Convert objects to dict for return
            result_dict = {}
            if extracted_docs:
                if isinstance(extracted_docs, list):
                    doc = extracted_docs[0]
                else:
                    doc = extracted_docs

                if doc.extractions:
                    # Take the first extraction
                    ext = doc.extractions[0]
                    # Map back to simple dict
                    result_dict = ext.attributes or {}
                    result_dict['incident_type'] = result_dict.get('incident_type', ext.extraction_class)
            
            return result_dict, html_viz

        except Exception as e:
            logger.error(f"Log Forensics Failed: {e}")
            return None, f"Error: {str(e)}"
