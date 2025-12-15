"""
Chat Manager for KR-CLI
Professional chat session management with persistent storage.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ChatSession:
    """Represents a single chat session."""
    
    def __init__(self, chat_id: str = None, title: str = "New Chat"):
        self.chat_id = chat_id or str(uuid.uuid4())
        self.title = title
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.messages: List[Dict[str, str]] = []
        
    def add_message(self, role: str, content: str):
        """Add a message to the chat history."""
        self.messages.append({
            "role": role,  # 'user' or 'assistant'
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now().isoformat()
        
    def to_dict(self) -> dict:
        """Convert session to dictionary for JSON serialization."""
        return {
            "chat_id": self.chat_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "message_count": len(self.messages),
            "messages": self.messages
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChatSession':
        """Create ChatSession from dictionary."""
        session = cls(chat_id=data["chat_id"], title=data["title"])
        session.created_at = data["created_at"]
        session.updated_at = data["updated_at"]
        session.messages = data.get("messages", [])
        return session


class ChatManager:
    """
    Professional chat session manager.
    Handles storage, retrieval, and management of chat sessions.
    """
    
    def __init__(self, username: str):
        """
        Initialize ChatManager for a specific user.
        
        Args:
            username: Current logged-in username
        """
        self.username = username
        self.base_dir = Path.home() / "krcli_chats" / username
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def create_chat(self, title: str = None) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            title: Optional chat title (auto-generated if None)
            
        Returns:
            New ChatSession instance
        """
        if not title:
            title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        session = ChatSession(title=title)
        self.save_chat(session)
        return session
    
    def save_chat(self, session: ChatSession):
        """Save a chat session to disk."""
        file_path = self.base_dir / f"chat_{session.chat_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_chat(self, chat_id: str) -> Optional[ChatSession]:
        """
        Load a chat session from disk.
        
        Args:
            chat_id: ID of the chat to load
            
        Returns:
            ChatSession if found, None otherwise
        """
        file_path = self.base_dir / f"chat_{chat_id}.json"
        
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ChatSession.from_dict(data)
        except Exception:
            return None
    
    def list_chats(self) -> List[Dict[str, str]]:
        """
        List all chat sessions for this user.
        
        Returns:
            List of chat metadata dictionaries sorted by update time (newest first)
        """
        chats = []
        
        for file_path in self.base_dir.glob("chat_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chats.append({
                        "chat_id": data["chat_id"],
                        "title": data["title"],
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                        "message_count": data.get("message_count", len(data.get("messages", [])))
                    })
            except Exception:
                continue
        
        # Sort by updated_at descending (newest first)
        chats.sort(key=lambda x: x["updated_at"], reverse=True)
        return chats
    
    def delete_chat(self, chat_id: str) -> bool:
        """
        Delete a chat session.
        
        Args:
            chat_id: ID of the chat to delete
            
        Returns:
            True if deleted successfully
        """
        file_path = self.base_dir / f"chat_{chat_id}.json"
        
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception:
                return False
        return False
    
    def get_chat_context(self, session: ChatSession, max_messages: int = 10) -> str:
        """
        Get recent chat context for AI prompt.
        
        Args:
            session: ChatSession to extract context from
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Formatted context string
        """
        if not session.messages:
            return ""
        
        recent = session.messages[-max_messages:]
        context_lines = []
        
        for msg in recent:
            role_label = "Usuario" if msg["role"] == "user" else "Asistente"
            context_lines.append(f"{role_label}: {msg['content']}")
        
        return "\n".join(context_lines)
