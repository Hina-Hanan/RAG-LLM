"""
Memory Management for Conversation Context

This module implements conversation memory to retain context across interactions.
"""

from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel

# LangChain 1.0+ compatibility - memory moved to langchain-classic
try:
    from langchain_classic.memory import ConversationBufferMemory
except ImportError:
    # Fallback for older versions
    from langchain.memory import ConversationBufferMemory


class ConversationMemory:
    """Manages conversation history for context retention."""
    
    def __init__(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """
        Add a message to conversation history.
        
        Args:
            role: "user" or "assistant"
            content: Message content
        """
        self.conversation_history.append({"role": role, "content": content})
        
        if role == "user":
            self.memory.chat_memory.add_user_message(content)
        elif role == "assistant":
            self.memory.chat_memory.add_ai_message(content)
    
    def get_chat_history(self) -> List[BaseMessage]:
        """Get conversation history as LangChain messages."""
        return self.memory.chat_memory.messages
    
    def get_history_dict(self) -> List[Dict[str, str]]:
        """Get conversation history as dictionary."""
        return self.conversation_history.copy()
    
    def clear(self):
        """Clear conversation history."""
        self.memory.clear()
        self.conversation_history = []
    
    def get_context_string(self) -> str:
        """Get conversation context as a formatted string."""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        for msg in self.conversation_history[-5:]:  # Last 5 messages for context
            role = msg["role"].upper()
            content = msg["content"]
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)


# Global memory storage (in production, use Redis or database)
conversation_memories: Dict[str, ConversationMemory] = {}


def get_memory(session_id: str = "default") -> ConversationMemory:
    """Get or create conversation memory for a session."""
    if session_id not in conversation_memories:
        conversation_memories[session_id] = ConversationMemory()
    return conversation_memories[session_id]


def clear_memory(session_id: str = "default"):
    """Clear conversation memory for a session."""
    if session_id in conversation_memories:
        conversation_memories[session_id].clear()

