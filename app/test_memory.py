import unittest
import json
import os
import shutil
import uuid
from typing import Dict, List

from core.memory_manager import MemoryEntry, get_memory_manager
from core.file_manager import get_file_manager
from core.llm_enhancer import get_llm_enhancer

class TestMemorySystem(unittest.TestCase):
    """Test the memory system functionality"""
    
    def setUp(self):
        """Set up test environment with a separate test datastore"""
        # Use a separate test directory
        self.test_dir = os.path.join('datastore', 'test_' + str(uuid.uuid4()))
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create test instance with the test directory
        self.memory_manager = get_memory_manager()
        # Override the storage path for testing
        self.memory_manager._storage_path = self.test_dir
        self.memory_manager._memory_file = os.path.join(self.test_dir, 'memory.json')
        
        # Create empty memory file
        with open(self.memory_manager._memory_file, 'w') as f:
            json.dump({}, f)
        
        # Get other components
        self.file_manager = get_file_manager()
        self.llm_enhancer = get_llm_enhancer()
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test directory and all its contents
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_memory_entry_creation(self):
        """Test creating a memory entry"""
        # Create a test entry
        entry = MemoryEntry(
            original_prompt="Test prompt",
            enhanced_prompt="Enhanced test prompt with details",
            image_path="/path/to/image.png",
            model_path="/path/to/model.glb"
        )
        
        # Check basic properties
        self.assertEqual(entry.original_prompt, "Test prompt")
        self.assertEqual(entry.enhanced_prompt, "Enhanced test prompt with details")
        self.assertEqual(entry.image_path, "/path/to/image.png")
        self.assertEqual(entry.model_path, "/path/to/model.glb")
        self.assertIsInstance(entry.id, str)
        
    def test_memory_storage_and_retrieval(self):
        """Test storing and retrieving memory entries"""
        # Create and store an entry
        entry = MemoryEntry(
            original_prompt="Test storage prompt",
            enhanced_prompt="Enhanced test storage prompt"
        )
        memory_id = self.memory_manager.store(entry)
        
        # Retrieve the entry
        retrieved_entry = self.memory_manager.retrieve(memory_id)
        
        # Check properties
        self.assertIsNotNone(retrieved_entry)
        self.assertEqual(retrieved_entry.original_prompt, "Test storage prompt")
        self.assertEqual(retrieved_entry.enhanced_prompt, "Enhanced test storage prompt")
        self.assertEqual(retrieved_entry.id, memory_id)
    
    def test_llm_enhancement(self):
        """Test LLM prompt enhancement"""
        # Test various prompt types
        prompts = [
            "Create a dragon",
            "Make a landscape with mountains",
            "Design a futuristic robot",
            "Draw a portrait of a woman"
        ]
        
        for prompt in prompts:
            enhanced = self.llm_enhancer.enhance_prompt(prompt)
            
            # Check that enhancement adds content
            self.assertGreater(len(enhanced), len(prompt))
            # Check that original prompt is preserved
            self.assertTrue(prompt in enhanced)
    
    def test_memory_search(self):
        """Test searching memory entries"""
        # Create and store multiple entries
        entries = [
            MemoryEntry(original_prompt="Red dragon breathing fire"),
            MemoryEntry(original_prompt="Blue robot with laser eyes"),
            MemoryEntry(original_prompt="Green forest with waterfalls"),
            MemoryEntry(original_prompt="Purple dragon in the sky")
        ]
        
        for entry in entries:
            self.memory_manager.store(entry)
        
        # Search for dragons
        dragon_results = self.memory_manager.search("dragon")
        self.assertEqual(len(dragon_results), 2)
        
        # Search for robot
        robot_results = self.memory_manager.search("robot")
        self.assertEqual(len(robot_results), 1)
        
        # Get recent entries
        recent_results = self.memory_manager.list_recent(limit=3)
        self.assertEqual(len(recent_results), 3)
    
    def test_memory_query_detection(self):
        """Test detecting memory-related queries"""
        # Memory queries
        memory_queries = [
            "Show me my recent dragons",
            "Find the robot I created yesterday",
            "Get my last 3 creations",
            "Retrieve all landscapes"
        ]
        
        # Creation queries (not memory)
        creation_queries = [
            "Create a red dragon",
            "Make a beautiful landscape",
            "Generate a futuristic city",
            "Design a new character"
        ]
        
        # Test memory queries
        for query in memory_queries:
            self.assertTrue(self.llm_enhancer.is_memory_query(query))
        
        # Test creation queries
        for query in creation_queries:
            self.assertFalse(self.llm_enhancer.is_memory_query(query))


if __name__ == '__main__':
    unittest.main()