#!/usr/bin/env python3
"""
Web interface for the Creative AI Pipeline using Streamlit.
This provides a user-friendly way to interact with the AI pipeline.
Uses a real DeepSeek LLM for prompt enhancement.
"""

import json
import os
import base64
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st

# Import our pipeline components
from core.memory_manager import get_memory_manager, MemoryEntry
from core.file_manager import get_file_manager
from core.memory_query import get_memory_query_handler
from core.stub import Stub
# Import real LLM enhancer
from core.real_llm_enhancer import get_real_llm_enhancer
from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel

# Set Openfabric app IDs
TEXT_TO_IMAGE_APP_ID = "f0997a01-d6d3-a5fe-53d8-561300318557"
IMAGE_TO_3D_APP_ID = "69543f29-4d41-4afc-7f29-3d51591f11eb"

# Initialize components
memory_manager = get_memory_manager()
file_manager = get_file_manager()
memory_query_handler = get_memory_query_handler()

# Helper functions
def display_image(image_path):
    """Display an image from a file path."""
    if os.path.exists(image_path):
        image_data = open(image_path, "rb").read()
        b64 = base64.b64encode(image_data).decode()
        return f'<img src="data:image/png;base64,{b64}" style="max-width:100%;">'
    return "Image not found"

def display_model(model_path):
    """Display a 3D model file link."""
    if os.path.exists(model_path):
        size = os.path.getsize(model_path)
        return f'3D Model file available ({size/1024:.2f} KB)'
    return "Model not found"

# Initialize the real LLM enhancer
@st.cache_resource
def initialize_llm():
    """Initialize the DeepSeek LLM (cached to avoid reloading)."""
    return get_real_llm_enhancer()

def process_creation(prompt, llm_enhancer):
    """Process a creation request from the prompt."""
    # Create a request
    request = InputClass()
    request.prompt = prompt
    
    # Create a response
    response = OutputClass()
    
    # Create an app model
    model = AppModel()
    model.request = request
    model.response = response
    
    # Initialize the Stub with app IDs
    config = ConfigClass()
    config.app_ids = [TEXT_TO_IMAGE_APP_ID, IMAGE_TO_3D_APP_ID]
    stub = Stub(config.app_ids)
    
    # Create a new memory entry
    memory_entry = MemoryEntry(original_prompt=prompt)
    
    # Enhance prompt with LLM
    try:
        with st.spinner("Enhancing prompt with DeepSeek..."):
            enhanced_prompt = llm_enhancer.enhance_prompt(prompt)
            memory_entry.enhanced_prompt = enhanced_prompt
    except Exception as e:
        st.error(f"Error enhancing prompt: {e}")
        enhanced_prompt = prompt
        memory_entry.enhanced_prompt = prompt
    
    # Call the Text to Image app
    try:
        with st.spinner("Generating image..."):
            image_result = stub.call(TEXT_TO_IMAGE_APP_ID, {'prompt': enhanced_prompt}, 'web-user')
            
            # Extract the image data
            image_data = image_result.get('result')
            if not image_data:
                raise Exception("No image data returned from Text to Image app")
            
            # Save the image to disk
            image_path = file_manager.save_image(image_data, memory_entry.id)
            memory_entry.image_path = image_path
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None
    
    # Call the Image to 3D app
    try:
        with st.spinner("Converting to 3D model..."):
            model_result = stub.call(IMAGE_TO_3D_APP_ID, {'image': image_data}, 'web-user')
            
            # Extract the 3D model data
            model_data = model_result.get('result')
            if not model_data:
                raise Exception("No model data returned from Image to 3D app")
            
            # Save the 3D model to disk
            model_path = file_manager.save_model(model_data, memory_entry.id)
            memory_entry.model_path = model_path
    except Exception as e:
        st.warning(f"Image generated successfully, but error creating 3D model: {str(e)}")
    
    # Add automatic tags from the prompt
    words = prompt.lower().split()
    important_words = [word for word in words if len(word) > 3 and word not in 
                      ['with', 'and', 'the', 'this', 'that', 'make', 'create', 'generate']]
    if important_words:
        tags = important_words[:5]  # Limit to 5 tags
        memory_entry.metadata['tags'] = tags
    
    # Save the memory entry
    memory_id = memory_manager.store(memory_entry)
    
    return memory_entry

def process_query(prompt, llm_enhancer):
    """Process a memory query request from the prompt."""
    # Check if this is a memory query
    if llm_enhancer.is_memory_query(prompt):
        # Parse the query parameters
        query_params = llm_enhancer.parse_memory_query(prompt)
        
        # Extract search terms
        search_terms = query_params.get("search_terms", [])
        
        # For debugging
        st.write(f"Search terms: {search_terms}")
        
        # Create the search query
        search_query = " ".join(set(search_terms)) if search_terms else ""
        
        # Get limit and sort parameters
        limit = query_params.get("limit", 5)
        reverse = query_params.get("reverse", True)
        
        # Search memory
        memory_entries = memory_manager.search(
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
                exists, size, _ = file_manager.get_file_info(entry.image_path)
                entry_dict["image_exists"] = exists
                entry_dict["image_size"] = size
                
            if entry.model_path:
                exists, size, _ = file_manager.get_file_info(entry.model_path)
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
    else:
        # Not a memory query
        return [], "This doesn't appear to be a memory query. Try phrases like 'show me', 'find', etc."

# Streamlit app
def main():
    st.set_page_config(
        page_title="Creative AI Pipeline with DeepSeek",
        page_icon="🧠",
        layout="wide",
    )
    
    st.title("🌟 Creative AI Pipeline with DeepSeek")
    st.subheader("Turn your text prompts into images and 3D models")
    
    # Initialize the LLM (cached)
    with st.spinner("Loading DeepSeek LLM..."):
        llm_enhancer = initialize_llm()
    
    tab1, tab2 = st.tabs(["Create", "Search"])
    
    # Creation tab
    with tab1:
        st.markdown("""
        Enter a descriptive prompt, and the AI will:
        1. Enhance it with DeepSeek LLM
        2. Generate an image
        3. Convert the image to a 3D model
        """)
        
        prompt = st.text_area("Your prompt:", height=100, 
                            placeholder="Example: A floating crystal city in the clouds")
        
        if st.button("Generate", key="generate_button"):
            if not prompt:
                st.error("Please enter a prompt.")
            else:
                result = process_creation(prompt, llm_enhancer)
                
                if result:
                    st.success("Creation successful!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Original Prompt")
                        st.write(result.original_prompt)
                        
                        st.markdown("### Enhanced Prompt")
                        st.write(result.enhanced_prompt)
                        
                        st.markdown("### Tags")
                        tags = result.metadata.get('tags', [])
                        st.write(", ".join(tags))
                    
                    with col2:
                        st.markdown("### Generated Image")
                        if result.image_path and os.path.exists(result.image_path):
                            st.markdown(display_image(result.image_path), unsafe_allow_html=True)
                        else:
                            st.warning("Image not available.")
                        
                        st.markdown("### 3D Model")
                        if result.model_path and os.path.exists(result.model_path):
                            st.markdown(display_model(result.model_path))
                            st.download_button(
                                label="Download 3D Model",
                                data=open(result.model_path, "rb").read(),
                                file_name=os.path.basename(result.model_path),
                                mime="application/octet-stream"
                            )
                        else:
                            st.warning("3D model not available.")
    
    # Search tab
    with tab2:
        st.markdown("""
        Search your past creations using natural language queries:
        - "Show me recent dragons"
        - "Find castles with clouds"
        - "Get my last 3 creations"
        """)
        
        search_prompt = st.text_input("Search prompt:", placeholder="Example: Find my recent creations")
        
        if st.button("Search", key="search_button"):
            if not search_prompt:
                st.error("Please enter a search prompt.")
            else:
                results, summary = process_query(search_prompt, llm_enhancer)
                
                st.markdown(f"### {summary}")
                
                if results:
                    for result in results:
                        with st.expander(f"{result['original_prompt']} ({result['date']})"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**Original Prompt:**")
                                st.write(result['original_prompt'])
                                
                                st.markdown("**Enhanced Prompt:**")
                                st.write(result.get('enhanced_prompt', 'N/A'))
                                
                                st.markdown("**Tags:**")
                                tags = result.get('metadata', {}).get('tags', [])
                                st.write(", ".join(tags))
                            
                            with col2:
                                if 'image_path' in result and result.get('image_exists', False):
                                    st.markdown("**Generated Image:**")
                                    st.markdown(display_image(result['image_path']), unsafe_allow_html=True)
                                
                                if 'model_path' in result and result.get('model_exists', False):
                                    st.markdown("**3D Model:**")
                                    st.markdown(display_model(result['model_path']))
                                    st.download_button(
                                        label="Download 3D Model",
                                        data=open(result['model_path'], "rb").read(),
                                        file_name=os.path.basename(result['model_path']),
                                        mime="application/octet-stream"
                                    )

    # Display information about the app
    st.sidebar.title("About")
    st.sidebar.info(
        """
        This web app demonstrates the Creative AI Pipeline 
        with DeepSeek LLM for prompt enhancement.
        
        The app features:
        - **DeepSeek LLM** for prompt enhancement
        - Text-to-Image generation
        - Image-to-3D model conversion
        - Memory system for past creations
        
        Note: The image and 3D model generation is using 
        mock services for demonstration purposes.
        """
    )
    
    st.sidebar.title("Statistics")
    memory_count = len(memory_manager.search(limit=1000))
    st.sidebar.metric("Total Creations", memory_count)
    
    # Show model information
    st.sidebar.title("Model Information")
    st.sidebar.info(
        """
        **Model**: DeepSeek 6.7B Instruct
        
        DeepSeek is an advanced language model with 
        strong reasoning and creative capabilities.
        
        In this app, it's used to enhance prompts by adding
        descriptive details, style information, and
        composition elements.
        """
    )
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 Creative AI Pipeline")

if __name__ == "__main__":
    main()