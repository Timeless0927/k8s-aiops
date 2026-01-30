import asyncio
import logging
from app.db.session import AsyncSessionLocal
from app.services.chat_history import ChatHistoryService
import uuid

async def test_persistence():
    print("Testing Persistence...")
    conv_id = str(uuid.uuid4())
    print(f"Test Conv ID: {conv_id}")
    
    async with AsyncSessionLocal() as session:
        # Create Conv
        conv = await ChatHistoryService.create_conversation(session, title="Test Persistence Script")
        real_id = conv.id
        print(f"Created Conversation ID: {real_id}")
        
        # Add Message
        msg = await ChatHistoryService.add_message(session, real_id, "assistant", "Test Content")
        print(f"Added Message ID: {msg.id}")
        
    # Verify in NEW session
    async with AsyncSessionLocal() as session:
        messages = await ChatHistoryService.get_recent_messages(session, real_id)
        print(f"Messages found: {len(messages)}")
        for m in messages:
            print(f" - {m.role}: {m.content}")
            
        if len(messages) >= 1 and messages[0].content == "Test Content":
            print("SUCCESS: Persistence working.")
        else:
            print("FAILURE: Message not found.")

if __name__ == "__main__":
    asyncio.run(test_persistence())
