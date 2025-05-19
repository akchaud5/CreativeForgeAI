#!/usr/bin/env python3
"""
Simple utility to check memory file contents.
"""

import json
import os
import sys

def main():
    # Determine paths
    memory_file = os.path.join('datastore', 'memory.json')
    
    # Check if the file exists
    if not os.path.exists(memory_file):
        print(f"Memory file {memory_file} does not exist")
        
        # Check for any other memory files
        search_path = 'datastore'
        if os.path.exists(search_path):
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.json') and file != 'tokens.json':
                        print(f"Found potential memory file: {os.path.join(root, file)}")
        
        return
    
    # Read the memory file
    try:
        with open(memory_file, 'r') as f:
            memory_data = json.load(f)
        
        # Print summary
        print(f"Memory file contains {len(memory_data)} entries")
        
        # Print details for each entry
        for entry_id, entry_data in memory_data.items():
            print(f"\nEntry ID: {entry_id}")
            print(f"  Prompt: {entry_data.get('original_prompt', 'N/A')}")
            print(f"  Date: {entry_data.get('date', 'N/A')}")
            print(f"  Image: {entry_data.get('image_path', 'N/A')}")
            print(f"  Model: {entry_data.get('model_path', 'N/A')}")
            
            # Print tags if available
            metadata = entry_data.get('metadata', {})
            tags = metadata.get('tags', [])
            if tags:
                print(f"  Tags: {', '.join(tags)}")
    
    except Exception as e:
        print(f"Error reading memory file: {e}")

if __name__ == "__main__":
    main()