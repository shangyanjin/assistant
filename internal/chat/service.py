"""
Chat service - business logic
"""
from typing import List, Generator
from internal.model.chat import ChatHistory, ChatMessage
from pkg.api.ollama import OllamaClient


class ChatService:
    """Chat business logic service"""
    
    def __init__(self, api_client: OllamaClient):
        """
        Initialize chat service
        
        Args:
            api_client: Ollama API client instance
        """
        self.api = api_client
        self.history = ChatHistory(messages=[])

    def send_message(self, content: str, model: str) -> Generator[str, None, None]:
        """
        Send message and get streaming response
        
        Args:
            content: User message content
            model: Model name to use
            
        Yields:
            Response content chunks
        """
        # Add user message to history
        user_msg = ChatMessage(role="user", content=content)
        self.history.add_message(user_msg)

        # Stream response from API
        for chunk in self.api.chat_stream(model, self.history.to_api_format()):
            yield chunk

    def add_assistant_message(self, content: str):
        """
        Add assistant response to history
        
        Args:
            content: Assistant response content
        """
        ai_msg = ChatMessage(role="assistant", content=content)
        self.history.add_message(ai_msg)

    def clear_history(self):
        """Clear chat history"""
        self.history.clear()

    def get_history(self) -> List[ChatMessage]:
        """Get chat history"""
        return self.history.messages

