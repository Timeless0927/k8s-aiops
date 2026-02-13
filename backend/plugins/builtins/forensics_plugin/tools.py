import logging
from app.services.log_forensics import LogForensicsService

logger = logging.getLogger(__name__)

async def analyze_incident_logs(log_content: str) -> str:
    """
    Analyze logs using AI Forensics (LangExtract) to extract structured incidents.
    Returns a human-readable summary of the structured findings.
    """
    if not log_content or len(log_content) < 10:
        return "Error: Log content is too short to analyze."

    try:
        # Call the service
        # The service returns (structured_dict, html_viz)
        # We only need the structured dict for the Agent.
        structured, _ = LogForensicsService.analyze_logs(log_content)
        
        if not structured:
            return "AI Analysis failed to extract structured data. The logs might be unstructured or generic."

        # Format as string for the Agent
        output = f"""
✅ **Log Analysis Complete**
- **Incident Type**: {structured.get('incident_type', 'Unknown')}
- **Severity**: {structured.get('severity', 'Unknown')}
- **Root Cause**: {structured.get('root_cause', 'N/A')}
- **Suggestion**: {structured.get('suggestion', 'N/A')}
- **Evidence**: {structured.get('evidence_summary', 'N/A')}

(Source: google/langextract)
"""
        return output

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return f"Error executing log analysis: {str(e)}"
