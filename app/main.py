import logging
import base64
import json
import os
import re
from typing import Dict, List, Optional, Union

from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub
from core.llm_enhancer import get_llm_enhancer
from core.memory_manager import MemoryEntry, get_memory_manager
from core.file_manager import get_file_manager
from core.memory_query import get_memory_query_handler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Openfabric app IDs - would normally be loaded from config
TEXT_TO_IMAGE_APP_ID = "f0997a01-d6d3-a5fe-53d8-561300318557"
IMAGE_TO_3D_APP_ID = "69543f29-4d41-4afc-7f29-3d51591f11eb"

# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()

############################################################
# Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application.
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        # If app_ids is not set, set default app IDs
        if not conf.app_ids:
            conf.app_ids = [TEXT_TO_IMAGE_APP_ID, IMAGE_TO_3D_APP_ID]
            logging.info(f"Setting default app IDs for user '{uid}'")
        configurations[uid] = conf


############################################################
# Execution callback function
############################################################
def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """
    # Initialize services
    llm_enhancer = get_llm_enhancer()
    memory_manager = get_memory_manager()
    file_manager = get_file_manager()
    memory_query_handler = get_memory_query_handler()

    # Retrieve input
    request: InputClass = model.request
    prompt = request.prompt.strip() if request.prompt else ""
    
    if not prompt:
        model.response.message = "Please provide a text prompt to generate an image and 3D model."
        return

    # Retrieve user config
    user_config: ConfigClass = configurations.get('super-user', None)
    logging.info(f"Using configuration: {configurations}")

    # Initialize the Stub with app IDs
    app_ids = user_config.app_ids if user_config else [TEXT_TO_IMAGE_APP_ID, IMAGE_TO_3D_APP_ID]
    stub = Stub(app_ids)

    # Check if this is a memory-related query
    if llm_enhancer.is_memory_query(prompt):
        logging.info(f"Processing memory query: {prompt}")
        # Process memory query
        memory_entries, summary = memory_query_handler.process_query(prompt)
        
        # Format the response
        response_data = {
            "type": "memory_query",
            "summary": summary,
            "results": memory_entries
        }
        
        # Prepare response
        response: OutputClass = model.response
        response.message = json.dumps(response_data)
        return

    # Create a new memory entry
    memory_entry = MemoryEntry(original_prompt=prompt)
    
    # Enhance prompt with LLM
    try:
        enhanced_prompt = llm_enhancer.enhance_prompt(prompt)
        memory_entry.enhanced_prompt = enhanced_prompt
        logging.info(f"Enhanced prompt: {enhanced_prompt}")
    except Exception as e:
        logging.error(f"Error enhancing prompt: {e}")
        enhanced_prompt = prompt
        memory_entry.enhanced_prompt = prompt
    
    # Call the Text to Image app
    try:
        logging.info(f"Calling Text to Image app with prompt: {enhanced_prompt}")
        image_result = stub.call(TEXT_TO_IMAGE_APP_ID, {'prompt': enhanced_prompt}, 'super-user')
        
        # Extract the image data
        image_data = image_result.get('result')
        if not image_data:
            raise Exception("No image data returned from Text to Image app")
        
        # Save the image to disk
        image_path = file_manager.save_image(image_data, memory_entry.id)
        memory_entry.image_path = image_path
        logging.info(f"Image saved to: {image_path}")
        
    except Exception as e:
        logging.error(f"Error calling Text to Image app: {e}")
        model.response.message = f"Error generating image: {str(e)}"
        return
    
    # Call the Image to 3D app
    try:
        logging.info("Calling Image to 3D app")
        model_result = stub.call(IMAGE_TO_3D_APP_ID, {'image': image_data}, 'super-user')
        
        # Extract the 3D model data
        model_data = model_result.get('result')
        if not model_data:
            raise Exception("No model data returned from Image to 3D app")
        
        # Save the 3D model to disk
        model_path = file_manager.save_model(model_data, memory_entry.id)
        memory_entry.model_path = model_path
        logging.info(f"3D model saved to: {model_path}")
        
    except Exception as e:
        logging.error(f"Error calling Image to 3D app: {e}")
        # Still save the memory entry with just the image
        memory_manager.store(memory_entry)
        model.response.message = f"Image generated successfully, but error creating 3D model: {str(e)}"
        return
    
    # Save the complete memory entry
    memory_id = memory_manager.store(memory_entry)
    logging.info(f"Memory entry saved with ID: {memory_id}")
    
    # Add automatic tags based on the prompt
    try:
        # Simple keyword extraction for tags
        words = re.findall(r'\b\w+\b', prompt.lower())
        important_words = [word for word in words if len(word) > 3 and word not in 
                          ['with', 'and', 'the', 'this', 'that', 'make', 'create', 'generate']]
        if important_words:
            tags = important_words[:5]  # Limit to 5 tags
            memory_entry.metadata['tags'] = tags
            memory_manager.update(memory_id, {'metadata': memory_entry.metadata})
            logging.info(f"Added tags: {tags}")
    except Exception as e:
        logging.error(f"Error adding tags: {e}")
    
    # Prepare the response data
    response_data = {
        "type": "creation",
        "memory_id": memory_id,
        "original_prompt": prompt,
        "enhanced_prompt": memory_entry.enhanced_prompt,
        "image_path": memory_entry.image_path,
        "model_path": memory_entry.model_path,
        "message": "Successfully created image and 3D model from your prompt."
    }
    
    # Prepare response
    response: OutputClass = model.response
    response.message = json.dumps(response_data)