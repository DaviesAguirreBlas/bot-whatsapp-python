from typing import List, Dict, Any
from langchain.memory import RedisChatMessageHistory
from langchain.schema import AIMessage, HumanMessage, SystemMessage, BaseMessage

from ..config import get_settings

settings = get_settings()

class RedisMemory:
    def __init__(self, session_id: str):
        self.history = RedisChatMessageHistory(
            session_id=session_id,
            url=settings.REDIS_URL
        )
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to the history."""
        self.history.add_message(HumanMessage(content=message))
    
    def add_ai_message(self, message: str) -> None:
        """Add an AI message to the history."""
        self.history.add_message(AIMessage(content=message))
    
    def add_system_message(self, message: str) -> None:
        """Add a system message to the history."""
        self.history.add_message(SystemMessage(content=message))
    
    def get_messages(self) -> List[BaseMessage]:
        """Get all messages from history."""
        return self.history.messages
    
    def clear(self) -> None:
        """Clear the message history."""
        self.history.clear()
    
    @staticmethod
    def format_message(message: BaseMessage) -> Dict[str, Any]:
        """Format a message for API response."""
        return {
            "role": message.type,
            "content": message.content
        } 