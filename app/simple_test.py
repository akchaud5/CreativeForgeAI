#!/usr/bin/env python3
"""
Simple test script for the Creative AI Pipeline components.
This script tests individual components without requiring the full Openfabric SDK.
"""

import json
import logging
import os
import sys
import uuid
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our components
from core.memory_manager import MemoryEntry, get_memory_manager
from core.file_manager import get_file_manager
from core.llm_enhancer import get_llm_enhancer
from core.memory_query import get_memory_query_handler

def create_test_directories():
    """Create test directories if they don't exist"""
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datastore', 'images'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datastore', 'models'), exist_ok=True)

def test_llm_enhancer():
    """Test the LLM enhancer component"""
    llm_enhancer = get_llm_enhancer()
    
    # Test prompt enhancement
    prompts = [
        "Create a magical castle on a floating island with waterfalls",
        "Design a cyberpunk city skyline at night",
        "Make a glowing dragon standing on a cliff at sunset",
        "Generate a futuristic space station orbiting Mars"
    ]
    
    print("\n=== Testing LLM Enhancer ===")
    for prompt in prompts:
        enhanced = llm_enhancer.enhance_prompt(prompt)
        print(f"Original: {prompt}")
        print(f"Enhanced: {enhanced}")
        print("-" * 50)
    
    # Test memory query detection
    memory_queries = [
        "Show me my recent dragons",
        "Find the castle I created yesterday",
        "Get my last 3 creations"
    ]
    
    print("\n=== Testing Memory Query Detection ===")
    for query in memory_queries:
        is_memory = llm_enhancer.is_memory_query(query)
        print(f"Query: {query}")
        print(f"Is memory query: {is_memory}")
        if is_memory:
            params = llm_enhancer.parse_memory_query(query)
            print(f"Parsed parameters: {params}")
        print("-" * 50)

def test_memory_system():
    """Test the memory system components"""
    memory_manager = get_memory_manager()
    
    # Clear existing memory for clean test
    memory_manager.clear_all()
    
    print("\n=== Testing Memory System ===")
    
    # Create some test entries
    entries = [
        MemoryEntry(
            original_prompt="Create a magical castle",
            enhanced_prompt="Create a magical castle, with intricate design details, floating in clouds, hyperdetailed, 8k resolution",
            image_path="datastore/images/sample_castle.png",
            model_path="datastore/models/sample_castle.glb"
        ),
        MemoryEntry(
            original_prompt="Make a dragon",
            enhanced_prompt="Make a dragon, with intricate skin texture, with otherworldly lighting effects, photorealistic",
            image_path="datastore/images/sample_dragon.png",
            model_path="datastore/models/sample_dragon.glb"
        ),
        MemoryEntry(
            original_prompt="Design a robot",
            enhanced_prompt="Design a robot, with fine mechanical details, showing accurate surface reflections, professional photography",
            image_path="datastore/images/sample_robot.png",
            model_path="datastore/models/sample_robot.glb"
        )
    ]
    
    # Store entries
    for entry in entries:
        entry_id = memory_manager.store(entry)
        print(f"Stored entry with ID: {entry_id}")
        
        # Add some tags
        keywords = entry.original_prompt.lower().split()
        tags = [word for word in keywords if len(word) > 3]
        entry.metadata["tags"] = tags
        memory_manager.update(entry_id, {"metadata": entry.metadata})
    
    # Test retrieval
    print("\n=== Testing Memory Retrieval ===")
    retrieved = memory_manager.retrieve(entries[0].id)
    if retrieved:
        print(f"Retrieved: {retrieved.original_prompt}")
        print(f"With tags: {retrieved.metadata.get('tags', [])}")
    
    # Test search
    print("\n=== Testing Memory Search ===")
    results = memory_manager.search("dragon")
    print(f"Found {len(results)} entries matching 'dragon'")
    for result in results:
        print(f"- {result.original_prompt}")
    
    # Test listing
    print("\n=== Testing Recent Listing ===")
    recent = memory_manager.list_recent(limit=2)
    print(f"Found {len(recent)} recent entries")
    for result in recent:
        print(f"- {result.original_prompt}")

def test_memory_query():
    """Test the memory query handler"""
    query_handler = get_memory_query_handler()
    
    print("\n=== Testing Memory Queries ===")
    queries = [
        "Show me my recent creations",
        "Find dragons",
        "Get my last 2 items",
        "Find items with castle"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        results, summary = query_handler.process_query(query)
        print(f"Summary: {summary}")
        print(f"Found {len(results)} results")
        print("-" * 50)

def simulate_pipeline():
    """Simulate the full pipeline without actual API calls"""
    llm_enhancer = get_llm_enhancer()
    memory_manager = get_memory_manager()
    file_manager = get_file_manager()
    
    print("\n=== Simulating Full Pipeline ===")
    
    # User prompt
    prompt = "Create a magical castle on a floating island with waterfalls"
    print(f"User prompt: {prompt}")
    
    # Enhance the prompt
    enhanced_prompt = llm_enhancer.enhance_prompt(prompt)
    print(f"Enhanced prompt: {enhanced_prompt}")
    
    # Simulate Text-to-Image
    print("Calling Text-to-Image API (simulation)...")
    
    # Create a memory entry
    entry = MemoryEntry(
        original_prompt=prompt,
        enhanced_prompt=enhanced_prompt,
        image_path="datastore/images/simulated_castle.png",
        model_path="datastore/models/simulated_castle.glb"
    )
    
    # Add tags
    keywords = prompt.lower().split()
    tags = [word for word in keywords if len(word) > 3 and word not in ['with', 'and', 'the', 'create', 'make']]
    entry.metadata["tags"] = tags
    
    # Store in memory
    memory_id = memory_manager.store(entry)
    print(f"Created and stored memory entry with ID: {memory_id}")
    print(f"Tags: {tags}")
    
    # Format a response
    response = {
        "type": "creation",
        "memory_id": memory_id,
        "original_prompt": prompt,
        "enhanced_prompt": enhanced_prompt,
        "image_path": entry.image_path,
        "model_path": entry.model_path,
        "message": "Successfully created image and 3D model from your prompt."
    }
    
    print(f"Response: {json.dumps(response, indent=2)}")

def main():
    """Run all tests"""
    create_test_directories()
    test_llm_enhancer()
    test_memory_system()
    test_memory_query()
    simulate_pipeline()

if __name__ == "__main__":
    main()