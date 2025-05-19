import logging
from typing import Dict, List, Optional, Tuple, Union

from core.memory_manager import MemoryEntry, get_memory_manager
from core.file_manager import get_file_manager
from core.llm_enhancer import get_llm_enhancer

class MemoryQueryHandler:
    """
    Handles memory-related queries and operations.
    Processes user requests for previous creations and handles memory search.
    """
    
    def __init__(self):
        """Initialize the memory query handler."""
        self.memory_manager = get_memory_manager()
        self.file_manager = get_file_manager()
        self.llm_enhancer = get_llm_enhancer()
    
    def process_query(self, prompt: str) -> Tuple[List[Dict], str]:
        """
        Process a memory-related query and return relevant memory entries.
        
        Args:
            prompt: The user's memory query
            
        Returns:
            Tuple[List[Dict], str]: (memory entries as dicts, summary message)
        """
        # Parse the query to extract parameters
        query_params = self.llm_enhancer.parse_memory_query(prompt)
        
        # Extract search terms
        search_terms = query_params.get("search_terms", [])
        
        # Log the search terms
        logging.info(f"Search terms: {search_terms}")
        
        # For city/cities, add both forms
        for i, term in enumerate(search_terms):
            if term == "city":
                if "cities" not in search_terms:
                    search_terms.append("cities")
            elif term == "cities":
                if "city" not in search_terms:
                    search_terms.append("city")
                    
        # Create the search query
        search_query = " ".join(set(search_terms)) if search_terms else ""
        
        # Get limit and sort parameters
        limit = query_params.get("limit", 5)
        reverse = query_params.get("reverse", True)
        
        # Search memory with the combined terms
        memory_entries = self.memory_manager.search(
            query=search_query,
            limit=limit,
            sort_by="timestamp",
            reverse=reverse
        )
        
        # Convert entries to dictionaries and add convenience fields
        result_entries = []
        for entry in memory_entries:
            entry_dict = entry.to_dict()
            
            # Add convenience fields for the frontend
            if entry.image_path:
                exists, size, _ = self.file_manager.get_file_info(entry.image_path)
                entry_dict["image_exists"] = exists
                entry_dict["image_size"] = size
                
            if entry.model_path:
                exists, size, _ = self.file_manager.get_file_info(entry.model_path)
                entry_dict["model_exists"] = exists
                entry_dict["model_size"] = size
                
            result_entries.append(entry_dict)
        
        # Create a summary message
        if result_entries:
            if search_query:
                summary = f"Found {len(result_entries)} creations matching '{', '.join(search_terms)}'"
            else:
                summary = f"Retrieved {len(result_entries)} recent creations"
        else:
            if search_query:
                summary = f"No creations found matching '{', '.join(search_terms)}'"
            else:
                summary = "No previous creations found"
        
        return result_entries, summary
    
    def get_memory_content(self, memory_id: str) -> Optional[Dict]:
        """
        Get full content for a specific memory entry, including binary data.
        
        Args:
            memory_id: ID of the memory entry
            
        Returns:
            Optional[Dict]: Full memory entry with binary data if found
        """
        entry = self.memory_manager.retrieve(memory_id)
        if not entry:
            return None
            
        result = entry.to_dict()
        
        # Add binary content if available
        if entry.image_path:
            image_data = self.file_manager.load_file(entry.image_path)
            if image_data:
                result["image_data"] = self.file_manager.encode_to_base64(image_data)
                
        if entry.model_path:
            model_data = self.file_manager.load_file(entry.model_path)
            if model_data:
                result["model_data"] = self.file_manager.encode_to_base64(model_data)
                
        return result
    
    def add_tags(self, memory_id: str, tags: List[str]) -> Optional[Dict]:
        """
        Add tags to a memory entry.
        
        Args:
            memory_id: ID of the memory entry
            tags: List of tags to add
            
        Returns:
            Optional[Dict]: Updated memory entry if found
        """
        entry = self.memory_manager.retrieve(memory_id)
        if not entry:
            return None
            
        # Get existing tags or create new list
        existing_tags = entry.metadata.get("tags", [])
        
        # Add new tags (avoid duplicates)
        for tag in tags:
            if tag not in existing_tags:
                existing_tags.append(tag)
                
        # Update metadata
        if "metadata" not in entry.metadata:
            entry.metadata = {}
        entry.metadata["tags"] = existing_tags
        
        # Save the updated entry
        self.memory_manager.store(entry)
        
        return entry.to_dict()


# Singleton instance for global access
_memory_query_handler = None

def get_memory_query_handler() -> MemoryQueryHandler:
    """Get or create the singleton memory query handler instance"""
    global _memory_query_handler
    if _memory_query_handler is None:
        _memory_query_handler = MemoryQueryHandler()
    return _memory_query_handler