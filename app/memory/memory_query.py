import logging
from typing import Dict, List, Any, Optional

from memory.memory_manager import MemoryManager

class MemoryQuery:
    """
    Utility for querying and retrieving data from memory
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the memory query utility
        
        Args:
            memory_manager: The memory manager instance
        """
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(__name__)
    
    def get_memory_by_id(self, memory_id: str, use_persistent: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory entry by ID
        
        Args:
            memory_id: The memory ID to retrieve
            use_persistent: Whether to check persistent storage if not found in session
            
        Returns:
            The memory data or None if not found
        """
        return self.memory_manager.get(memory_id, use_persistent)
    
    def get_user_memories(self, user_id: str, use_persistent: bool = True) -> List[Dict[str, Any]]:
        """
        Get all memory entries for a specific user
        
        Args:
            user_id: The user ID to filter by
            use_persistent: Whether to include entries from persistent storage
            
        Returns:
            List of memory entries
        """
        return self.memory_manager.get_all_for_user(user_id, use_persistent)
    
    def search_by_prompt(self, query: str, user_id: Optional[str] = None, use_persistent: bool = True) -> List[Dict[str, Any]]:
        """
        Search for memories by prompt content
        
        Args:
            query: The search term to look for in prompts
            user_id: Optional user ID to filter by
            use_persistent: Whether to include entries from persistent storage
            
        Returns:
            List of matching memory entries
        """
        # In a real implementation, this would use a more sophisticated search
        # For now, we'll just do a simple contains search
        
        # Get all memories for the user if specified, otherwise all memories
        if user_id:
            memories = self.memory_manager.get_all_for_user(user_id, use_persistent)
        else:
            # Since we don't have a get_all method, we'll just use get_all_for_user with 'super-user'
            # In a real implementation, you would have a get_all method
            memories = self.memory_manager.get_all_for_user('super-user', use_persistent)
        
        # Filter memories by the query
        query = query.lower()
        return [
            memory for memory in memories
            if query in memory.get("original_prompt", "").lower() or
               query in memory.get("enhanced_prompt", "").lower()
        ]
    
    def get_last_n_memories(self, user_id: str, n: int = 5, use_persistent: bool = True) -> List[Dict[str, Any]]:
        """
        Get the N most recent memories for a user
        
        Args:
            user_id: The user ID to filter by
            n: Number of memories to retrieve
            use_persistent: Whether to include entries from persistent storage
            
        Returns:
            List of the most recent memory entries
        """
        memories = self.memory_manager.get_all_for_user(user_id, use_persistent)
        
        # Sort by timestamp (descending)
        sorted_memories = sorted(
            memories, 
            key=lambda x: x.get("timestamp", ""), 
            reverse=True
        )
        
        # Return only the last N
        return sorted_memories[:n]