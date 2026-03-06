"""Memory management using AgentCore Memory service."""
from typing import Dict, Any, List, Optional
import boto3
from src.config import settings


class MemoryManager:
    """Manages short-term and long-term memory."""
    
    def __init__(self):
        """Initialize memory manager."""
        self.memory_id = getattr(settings, 'MEMORY_ID', None)
        self.mock_mode = not self.memory_id
        
        # In-memory storage for mock mode
        self._mock_preferences: Dict[str, Dict[str, Any]] = {}
        self._mock_conversations: Dict[str, List[Dict[str, str]]] = {}
        
        if not self.mock_mode:
            self.client = boto3.client(
                'bedrock-agentcore-memory',
                region_name=settings.AWS_REGION
            )
    
    def store_user_preference(
        self,
        session_id: str,
        preference_type: str,
        value: str,
    ) -> None:
        """
        Store user preference in long-term memory.
        
        Args:
            session_id: User session identifier
            preference_type: Type of preference (dietary, price, location, etc.)
            value: Preference value
        """
        if self.mock_mode:
            if session_id not in self._mock_preferences:
                self._mock_preferences[session_id] = {}
            self._mock_preferences[session_id][preference_type] = value
            return
        
    
    def get_user_preferences(
        self,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve user preferences from long-term memory.
        
        Args:
            session_id: User session identifier
            
        Returns:
            Dictionary of user preferences
        """
        if self.mock_mode:
            return self._mock_preferences.get(session_id, {})
        
        return {}
    
    def store_conversation_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None:
        """
        Store conversation turn for short-term memory.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            assistant_message: Assistant's response
        """
        if self.mock_mode:
            if session_id not in self._mock_conversations:
                self._mock_conversations[session_id] = []
            
            self._mock_conversations[session_id].append({
                "user": user_message,
                "assistant": assistant_message,
            })
            return



# Global instance
memory_manager = MemoryManager()