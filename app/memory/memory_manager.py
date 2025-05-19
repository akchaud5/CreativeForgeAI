import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class SessionMemory:
    """
    Short-term memory storage for the current session.
    Retains data in memory during the application's runtime.
    """
    
    def __init__(self):
        self.memory: Dict[str, Dict[str, Any]] = {}
    
    def add(self, 
            user_id: str,
            original_prompt: str,
            enhanced_prompt: str,
            image_path: Optional[str] = None,
            model_3d_path: Optional[str] = None) -> str:
        """
        Add a new memory entry
        
        Args:
            user_id: The user ID
            original_prompt: The original user prompt
            enhanced_prompt: The enhanced prompt sent to the text-to-image model
            image_path: Path to the generated image (optional)
            model_3d_path: Path to the generated 3D model (optional)
            
        Returns:
            The memory ID
        """
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        self.memory[memory_id] = {
            "user_id": user_id,
            "timestamp": timestamp,
            "original_prompt": original_prompt,
            "enhanced_prompt": enhanced_prompt,
            "image_path": image_path,
            "model_3d_path": model_3d_path
        }
        
        return memory_id
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory entry by ID"""
        return self.memory.get(memory_id)
    
    def get_all_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all memory entries for a specific user"""
        return [
            {"id": mem_id, **memory}
            for mem_id, memory in self.memory.items()
            if memory["user_id"] == user_id
        ]


class PersistentMemory:
    """
    Long-term memory storage using JSON files.
    Retains data across application restarts.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the persistent memory
        
        Args:
            storage_dir: Directory to store memory files
        """
        if storage_dir is None:
            # Default to a directory in the application path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            storage_dir = os.path.join(base_dir, "datastore", "memory")
            
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Index file to map memory IDs to filenames
        self.index_file = os.path.join(self.storage_dir, "memory_index.json")
        self.memory_index = self._load_index()
    
    def _load_index(self) -> Dict[str, str]:
        """Load the memory index from the index file"""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_index(self) -> None:
        """Save the memory index to the index file"""
        with open(self.index_file, 'w') as f:
            json.dump(self.memory_index, f)
    
    def add(self, 
            user_id: str,
            original_prompt: str,
            enhanced_prompt: str,
            image_path: Optional[str] = None,
            model_3d_path: Optional[str] = None) -> str:
        """
        Add a new memory entry to persistent storage
        
        Args:
            user_id: The user ID
            original_prompt: The original user prompt
            enhanced_prompt: The enhanced prompt sent to the text-to-image model
            image_path: Path to the generated image
            model_3d_path: Path to the generated 3D model
            
        Returns:
            The memory ID
        """
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        memory_data = {
            "user_id": user_id,
            "timestamp": timestamp,
            "original_prompt": original_prompt,
            "enhanced_prompt": enhanced_prompt,
            "image_path": image_path,
            "model_3d_path": model_3d_path
        }
        
        # Save to a file using the memory ID
        filename = f"{memory_id}.json"
        file_path = os.path.join(self.storage_dir, filename)
        
        with open(file_path, 'w') as f:
            json.dump(memory_data, f)
        
        # Update the index
        self.memory_index[memory_id] = filename
        self._save_index()
        
        return memory_id
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory entry by ID"""
        if memory_id not in self.memory_index:
            return None
        
        filename = self.memory_index[memory_id]
        file_path = os.path.join(self.storage_dir, filename)
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            memory_data = json.load(f)
            return {"id": memory_id, **memory_data}
    
    def get_all_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all memory entries for a specific user"""
        result = []
        
        for memory_id, filename in self.memory_index.items():
            file_path = os.path.join(self.storage_dir, filename)
            
            if not os.path.exists(file_path):
                continue
            
            with open(file_path, 'r') as f:
                memory_data = json.load(f)
                
                if memory_data["user_id"] == user_id:
                    result.append({"id": memory_id, **memory_data})
        
        return result


class MemoryManager:
    """
    Unified interface for managing memory across both 
    short-term (session) and long-term (persistent) storage.
    """
    
    def __init__(self):
        """Initialize both short-term and long-term memory systems"""
        self.session_memory = SessionMemory()
        self.persistent_memory = PersistentMemory()
    
    def add(self, 
            user_id: str,
            original_prompt: str,
            enhanced_prompt: str,
            image_path: Optional[str] = None,
            model_3d_path: Optional[str] = None,
            persist: bool = True) -> str:
        """
        Add a memory entry to both short-term and (optionally) long-term storage
        
        Args:
            user_id: The user ID
            original_prompt: The original user prompt
            enhanced_prompt: The enhanced prompt sent to the text-to-image model
            image_path: Path to the generated image
            model_3d_path: Path to the generated 3D model
            persist: Whether to also save to persistent storage
            
        Returns:
            The memory ID
        """
        # Always add to session memory
        memory_id = self.session_memory.add(
            user_id=user_id,
            original_prompt=original_prompt,
            enhanced_prompt=enhanced_prompt,
            image_path=image_path,
            model_3d_path=model_3d_path
        )
        
        # Optionally add to persistent memory
        if persist:
            self.persistent_memory.add(
                user_id=user_id,
                original_prompt=original_prompt,
                enhanced_prompt=enhanced_prompt,
                image_path=image_path,
                model_3d_path=model_3d_path
            )
        
        return memory_id
    
    def get(self, memory_id: str, use_persistent: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a memory entry by ID
        
        Args:
            memory_id: The memory ID to retrieve
            use_persistent: Whether to check persistent storage if not found in session
            
        Returns:
            The memory data or None if not found
        """
        # Try session memory first
        memory = self.session_memory.get(memory_id)
        
        # If not found and use_persistent is True, try persistent memory
        if memory is None and use_persistent:
            memory = self.persistent_memory.get(memory_id)
        
        return memory
    
    def get_all_for_user(self, user_id: str, use_persistent: bool = False) -> List[Dict[str, Any]]:
        """
        Get all memory entries for a specific user
        
        Args:
            user_id: The user ID to filter by
            use_persistent: Whether to include entries from persistent storage
            
        Returns:
            List of memory entries
        """
        # Get entries from session memory
        session_entries = self.session_memory.get_all_for_user(user_id)
        
        if not use_persistent:
            return session_entries
        
        # Get entries from persistent memory as well
        persistent_entries = self.persistent_memory.get_all_for_user(user_id)
        
        # Merge the entries, giving preference to session entries for duplicates
        session_ids = {entry["id"] for entry in session_entries}
        filtered_persistent = [entry for entry in persistent_entries if entry["id"] not in session_ids]
        
        return session_entries + filtered_persistent