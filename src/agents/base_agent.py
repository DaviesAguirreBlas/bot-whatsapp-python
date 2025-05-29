from typing import List, Dict, Any
from langchain.agents import Tool
from langchain.schema import BaseMessage
from abc import ABC, abstractmethod

from ..memory.redis_memory import RedisMemory


class BaseAgent(ABC):
    def __init__(self, customer_phone: str):
        self.customer_phone = customer_phone
        self.memory = RedisMemory(f"chat:{customer_phone}")
        self.tools: List[Tool] = []
    
    @abstractmethod
    async def process_message(self, message: str) -> str:
        """Process an incoming message and return a response."""
        pass
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get formatted chat history."""
        messages = self.memory.get_messages()
        return [self.memory.format_message(msg) for msg in messages]
    
    def clear_history(self) -> None:
        """Clear chat history."""
        self.memory.clear()
    
    def _add_message_to_history(self, message: str, is_user: bool = True) -> None:
        """Add a message to chat history."""
        if is_user:
            self.memory.add_user_message(message)
        else:
            self.memory.add_ai_message(message) 