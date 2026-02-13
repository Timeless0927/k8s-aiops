import asyncio
from app.services.log_forensics import LogForensicsService
from app.core.llm_config import LLMConfigManager

# Mock Log
MOCK_LOG = """
2024-05-20 10:00:01 [main] OPS-SERVICE STARTED
2024-05-20 10:00:02 [main] Connecting to DB...
2024-05-20 10:00:05 [pool-1-thread-1] ERROR com.example.payment.PaymentService - Transaction failed
java.sql.SQLTimeoutException: ORA-01013: user requested cancel of current operation
    at oracle.jdbc.driver.T4CPreparedStatement.executeForRows(T4CPreparedStatement.java:1041)
    at oracle.jdbc.driver.OracleStatement.executeMaybeDescribe(OracleStatement.java:1193)
    at com.example.payment.dao.PaymentDAO.process(PaymentDAO.java:45)
    ... 25 more
2024-05-20 10:00:06 [pool-1-thread-1] WARN Retrying transaction (1/3)...
"""

async def test():
    print("Testing LogForensicsService...")
    # Initialize Config (mock or load real)
    # Using real config requires DB, we can manually set LLMConfigManager._instance for test
    from app.core.config import settings
    
    # Just print what we would send
    if not settings.OPENAI_API_KEY:
        print("Skipping: No API Key")
        return

    # Use the static method directly
    struct, html = LogForensicsService.analyze_logs(MOCK_LOG)
    
    print("\n--- Structured Data ---")
    print(struct)
    
    print("\n--- HTML ---")
    print(html[:200] + "...") # Print first 200 chars

if __name__ == "__main__":
    asyncio.run(test())
