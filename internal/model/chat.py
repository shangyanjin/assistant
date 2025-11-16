"""
Chat data models
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChatMessage:
    """Chat message model"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to API format"""
        return {
            "role": self.role,
            "content": self.content
        }


@dataclass
class ChatHistory:
    """Chat history model"""
    messages: List[ChatMessage]

    def to_api_format(self) -> List[dict]:
        """Convert to API format"""
        return [msg.to_dict() for msg in self.messages]

    def add_message(self, message: ChatMessage):
        """Add message to history"""
        self.messages.append(message)

    def clear(self):
        """Clear all messages"""
        self.messages.clear()

