from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.chat import Conversation, Message
import uuid

class ChatHistoryService:
    @staticmethod
    async def create_conversation(session: AsyncSession, title: str = None, id: str = None, type: str = "chat") -> Conversation:
        conversation = Conversation(
            id=id or str(uuid.uuid4()),
            title=title or "New Conversation",
            type=type
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

    @staticmethod
    async def get_conversation(session: AsyncSession, conversation_id: str) -> Conversation | None:
        result = await session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalars().first()

    @staticmethod
    async def add_message(session: AsyncSession, conversation_id: str, role: str, content: str, tool_call_id: str = None) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_call_id=tool_call_id
        )
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    @staticmethod
    async def get_recent_messages(session: AsyncSession, conversation_id: str, limit: int = 50) -> list[Message]:
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc()) # Get absolute history order
            # Note: For "Recent N", we might want desc limit then reverse? 
            # But usually we send full context. Let's just return all for now or optimize later.
            # If we want limit, we should do subquery or slice.
            # .limit(limit) 
        )
        return result.scalars().all()
    
    @staticmethod
    async def delete_conversation(session: AsyncSession, conversation_id: str) -> bool:
        """Delete a conversation and its messages."""
        # Check if exists
        conv = await ChatHistoryService.get_conversation(session, conversation_id)
        if not conv:
            return False
            
        await session.delete(conv)
        await session.commit()
        return True

    @staticmethod
    async def ensure_conversation(session: AsyncSession, conversation_id: str | None = None, type: str = "chat") -> Conversation:
        if conversation_id:
            conv = await ChatHistoryService.get_conversation(session, conversation_id)
            if conv:
                return conv
        
        # Create new if not exists or no ID provided
        return await ChatHistoryService.create_conversation(session, id=conversation_id, type=type)
