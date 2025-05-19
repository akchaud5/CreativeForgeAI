import json
import os
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Set

# Memory entry structure
class MemoryEntry:
    """
    Represents a single memory entry containing all data related to a creation process.
    
    Attributes:
        id (str): Unique identifier for the memory entry
        timestamp (float): Unix timestamp when entry was created
        original_prompt (str): The user's original prompt
        enhanced_prompt (str): The LLM-enhanced prompt
        image_path (str): Path to the generated image
        model_path (str): Path to the generated 3D model
        metadata (Dict): Additional metadata (tags, description, etc.)
    """
    
    def __init__(self, 
                 original_prompt: str, 
                 enhanced_prompt: Optional[str] = None,
                 image_path: Optional[str] = None,
                 model_path: Optional[str] = None,
                 metadata: Optional[Dict] = None):
        self.id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.date = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.original_prompt = original_prompt
        self.enhanced_prompt = enhanced_prompt
        self.image_path = image_path
        self.model_path = model_path
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        """Convert memory entry to a dictionary for storage"""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'date': self.date,
            'original_prompt': self.original_prompt,
            'enhanced_prompt': self.enhanced_prompt,
            'image_path': self.image_path,
            'model_path': self.model_path,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEntry':
        """Create a memory entry from a dictionary"""
        entry = cls(
            original_prompt=data['original_prompt'],
            enhanced_prompt=data.get('enhanced_prompt'),
            image_path=data.get('image_path'),
            model_path=data.get('model_path'),
            metadata=data.get('metadata', {})
        )
        entry.id = data['id']
        entry.timestamp = data['timestamp']
        entry.date = data.get('date', datetime.fromtimestamp(entry.timestamp).strftime('%Y-%m-%d %H:%M:%S'))
        return entry


class MemoryManager:
    """
    Manages both short-term (session) and long-term (persistent) memory for the application.
    
    Attributes:
        _short_term_memory (Dict[str, MemoryEntry]): Session memory (lost on restart)
        _storage_path (str): Path to persistent storage file
        _memory_file (str): Filename for persistent storage
    """
    
    def __init__(self, storage_path: str = None, memory_file: str = 'memory.json'):
        """
        Initialize the memory manager with storage paths.
        
        Args:
            storage_path: Directory where memory and files are stored
            memory_file: Name of the memory database file
        """
        self._short_term_memory: Dict[str, MemoryEntry] = {}
        
        # Determine the absolute path for storage
        if storage_path is None:
            # Get directory of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the app directory
            app_dir = os.path.dirname(current_dir)
            # Then to the datastore
            self._storage_path = os.path.join(app_dir, 'datastore')
        else:
            self._storage_path = storage_path
            
        self._memory_file = os.path.join(self._storage_path, memory_file)
        
        logging.info(f"Memory manager initialized with file: {self._memory_file}")
        
        # Create storage directory if it doesn't exist
        os.makedirs(self._storage_path, exist_ok=True)
        
        # Initialize long-term memory if it doesn't exist
        if not os.path.exists(self._memory_file):
            with open(self._memory_file, 'w') as f:
                json.dump({}, f)
            logging.info(f"Created new memory file at: {self._memory_file}")
    
    def store(self, memory_entry: MemoryEntry, persist: bool = True) -> str:
        """
        Store a memory entry in both short-term and optionally long-term memory.
        
        Args:
            memory_entry: The memory entry to store
            persist: Whether to save to persistent storage
            
        Returns:
            str: The ID of the stored memory entry
        """
        # Store in short-term memory
        self._short_term_memory[memory_entry.id] = memory_entry
        
        # Store in long-term memory if requested
        if persist:
            self._persist_to_storage(memory_entry)
        
        return memory_entry.id
    
    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a memory entry by ID, checking short-term memory first, then long-term.
        
        Args:
            entry_id: The ID of the memory entry to retrieve
            
        Returns:
            Optional[MemoryEntry]: The retrieved memory entry, or None if not found
        """
        # Check short-term memory first
        if entry_id in self._short_term_memory:
            return self._short_term_memory[entry_id]
        
        # Then check long-term memory
        try:
            with open(self._memory_file, 'r') as f:
                memory_data = json.load(f)
                
            if entry_id in memory_data:
                entry = MemoryEntry.from_dict(memory_data[entry_id])
                # Cache in short-term for future access
                self._short_term_memory[entry_id] = entry
                return entry
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.error(f"Error retrieving from memory: {e}")
            
        return None
    
    def search(self, 
               query: str = None, 
               limit: int = 10, 
               sort_by: str = 'timestamp', 
               reverse: bool = True) -> List[MemoryEntry]:
        """
        Search memory entries by keyword, returning the most relevant ones.
        
        Args:
            query: Optional search string to filter entries by prompt content
            limit: Maximum number of entries to return
            sort_by: Field to sort results by (timestamp, id)
            reverse: Whether to reverse the sort order (newest first if True)
            
        Returns:
            List[MemoryEntry]: List of matching memory entries
        """
        logging.info(f"Searching memory for: '{query}', limit={limit}")
        
        # Load all entries from persistent storage
        try:
            with open(self._memory_file, 'r') as f:
                memory_data = json.load(f)
                
            # Convert to memory entries
            entries = []
            for entry_id, entry_data in memory_data.items():
                # Also include short-term entries that might have updated data
                if entry_id in self._short_term_memory:
                    entries.append(self._short_term_memory[entry_id])
                else:
                    entries.append(MemoryEntry.from_dict(entry_data))
            
            logging.info(f"Loaded {len(entries)} entries from memory")
                    
            # Filter by query if provided
            if query:
                # Split query into individual search terms
                search_terms = query.lower().split()
                
                # Prepare a set to track which entries match
                matched_entries = []
                
                for entry in entries:
                    # Check if any search term is in the prompt or metadata
                    entry_text = entry.original_prompt.lower()
                    if entry.enhanced_prompt:
                        entry_text += " " + entry.enhanced_prompt.lower()
                        
                    # Add tags to searchable text
                    tags = entry.metadata.get("tags", [])
                    if tags:
                        entry_text += " " + " ".join(tags).lower()
                        
                    # Check if any search term is in the entry text
                    for term in search_terms:
                        if term in entry_text:
                            matched_entries.append(entry)
                            break
                
                entries = matched_entries
                logging.info(f"Filtered to {len(entries)} entries matching '{query}'")
                
            # Sort entries
            if sort_by == 'timestamp':
                entries.sort(key=lambda x: x.timestamp, reverse=reverse)
            elif sort_by == 'id':
                entries.sort(key=lambda x: x.id, reverse=reverse)
                
            # Limit results
            return entries[:limit]
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.error(f"Error searching memory: {e}")
            return []
    
    def list_recent(self, limit: int = 5) -> List[MemoryEntry]:
        """
        List the most recent memory entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List[MemoryEntry]: List of recent memory entries
        """
        return self.search(limit=limit)
    
    def update(self, entry_id: str, updates: Dict) -> Optional[MemoryEntry]:
        """
        Update a memory entry with new data.
        
        Args:
            entry_id: The ID of the memory entry to update
            updates: Dictionary of fields to update
            
        Returns:
            Optional[MemoryEntry]: The updated memory entry, or None if not found
        """
        entry = self.retrieve(entry_id)
        if not entry:
            return None
            
        # Update fields
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
                
        # Store the updated entry
        self.store(entry)
        return entry
    
    def _persist_to_storage(self, memory_entry: MemoryEntry) -> None:
        """
        Persist a memory entry to long-term storage.
        
        Args:
            memory_entry: The memory entry to persist
        """
        try:
            # Load existing data
            try:
                with open(self._memory_file, 'r') as f:
                    memory_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                memory_data = {}
                
            # Add or update the entry
            memory_data[memory_entry.id] = memory_entry.to_dict()
            
            # Save back to file
            with open(self._memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
                
            logging.info(f"Saved memory entry {memory_entry.id} to {self._memory_file}")
                
        except Exception as e:
            logging.error(f"Error persisting memory: {e}")
    
    def clear_short_term(self) -> None:
        """Clear short-term memory"""
        self._short_term_memory = {}
    
    def clear_all(self) -> None:
        """Clear both short-term and long-term memory"""
        self.clear_short_term()
        with open(self._memory_file, 'w') as f:
            json.dump({}, f)
        logging.info(f"Cleared all memory in {self._memory_file}")


# Singleton instance for global access
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get or create the singleton memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager