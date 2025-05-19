import argparse
import json
import logging
import os
import sys
import time

from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from openfabric_pysdk.context import AppModel, State

from core.llm_enhancer import get_llm_enhancer
from core.memory_manager import get_memory_manager
from core.file_manager import get_file_manager

# Import main functions
import main

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_test_config():
    """Create a test configuration with app IDs"""
    # Create a config class instance
    config_class = ConfigClass()
    config_class.app_ids = [main.TEXT_TO_IMAGE_APP_ID, main.IMAGE_TO_3D_APP_ID]
    
    # Call the config function to register it
    conf_dict = {'super-user': config_class}
    main.config(conf_dict, None)
    logging.info("Test configuration created")

def test_prompt(prompt):
    """Test the pipeline with a specific prompt"""
    logging.info(f"Testing prompt: {prompt}")
    
    # Create a request
    input_class = InputClass()
    input_class.prompt = prompt
    
    # Create a response
    output_class = OutputClass()
    
    # Create a model
    model = AppModel()
    model.request = input_class
    model.response = output_class
    
    # Call the execute function
    main.execute(model)
    
    # Get the response
    response = model.response.message
    logging.info(f"Response received")
    
    try:
        # Parse JSON response
        response_data = json.loads(response)
        logging.info(json.dumps(response_data, indent=2))
        
        # Check if it's a creation
        if response_data.get("type") == "creation":
            memory_id = response_data.get("memory_id")
            image_path = response_data.get("image_path")
            model_path = response_data.get("model_path")
            
            logging.info(f"Memory ID: {memory_id}")
            logging.info(f"Image Path: {image_path}")
            logging.info(f"Model Path: {model_path}")
            
            # Check if files exist
            file_manager = get_file_manager()
            if image_path and os.path.exists(image_path):
                image_size = os.path.getsize(image_path)
                logging.info(f"Image file exists ({image_size} bytes)")
            else:
                logging.warning("Image file does not exist")
                
            if model_path and os.path.exists(model_path):
                model_size = os.path.getsize(model_path)
                logging.info(f"Model file exists ({model_size} bytes)")
            else:
                logging.warning("Model file does not exist")
                
            return memory_id
                
        # Check if it's a memory query
        elif response_data.get("type") == "memory_query":
            results = response_data.get("results", [])
            logging.info(f"Returned {len(results)} memory entries")
            
            return None
            
    except json.JSONDecodeError:
        logging.error("Failed to parse response as JSON")
        logging.info(f"Raw response: {response}")
    
    return None

def test_memory_query(query):
    """Test a memory query"""
    logging.info(f"Testing memory query: {query}")
    
    # Create a request
    input_class = InputClass()
    input_class.prompt = query
    
    # Create a response
    output_class = OutputClass()
    
    # Create a model
    model = AppModel()
    model.request = input_class
    model.response = output_class
    
    # Call the execute function
    main.execute(model)
    
    # Get the response
    response = model.response.message
    logging.info(f"Response received")
    
    try:
        # Parse JSON response
        response_data = json.loads(response)
        logging.info(json.dumps(response_data, indent=2))
        
        # Check the type
        if response_data.get("type") == "memory_query":
            results = response_data.get("results", [])
            logging.info(f"Returned {len(results)} memory entries")
            return results
            
    except json.JSONDecodeError:
        logging.error("Failed to parse response as JSON")
        logging.info(f"Raw response: {response}")
    
    return []

def run_tests():
    """Run a series of tests on the pipeline"""
    # Create configuration
    create_test_config()
    
    # Clear any existing memory
    memory_manager = get_memory_manager()
    memory_manager.clear_all()
    logging.info("Memory cleared")
    
    # Test 1: Create a dragon
    logging.info("TEST 1: Create a dragon")
    dragon_id = test_prompt("Make me a glowing dragon standing on a cliff at sunset")
    time.sleep(1)  # Pause to make timestamps different
    
    # Test 2: Create a robot
    logging.info("TEST 2: Create a robot")
    robot_id = test_prompt("Design a futuristic humanoid robot with glowing blue eyes")
    time.sleep(1)  # Pause to make timestamps different
    
    # Test 3: Create a landscape
    logging.info("TEST 3: Create a landscape")
    landscape_id = test_prompt("Create a beautiful mountain landscape with a lake and forest")
    time.sleep(1)  # Pause to make timestamps different
    
    # Test 4: Query for recent items
    logging.info("TEST 4: Query for recent items")
    recent_results = test_memory_query("Show me my recent creations")
    
    # Test 5: Query for dragons
    logging.info("TEST 5: Query for dragons")
    dragon_results = test_memory_query("Find dragons")
    
    # Test 6: Query with limit
    logging.info("TEST 6: Query with limit")
    limited_results = test_memory_query("Get my last 2 creations")
    
    # Test 7: Complex query
    logging.info("TEST 7: Complex query")
    complex_results = test_memory_query("Find items with glowing features")
    
    logging.info("All tests completed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the creative AI pipeline")
    parser.add_argument("--prompt", type=str, help="A prompt to test")
    parser.add_argument("--query", type=str, help="A memory query to test")
    parser.add_argument("--test-all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if args.test_all:
        run_tests()
    elif args.prompt:
        create_test_config()
        test_prompt(args.prompt)
    elif args.query:
        create_test_config()
        test_memory_query(args.query)
    else:
        parser.print_help()