#!/bin/bash

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate 2>/dev/null || echo "Virtual environment not found, continuing without it"

# Install required packages if needed
pip install -r requirements.txt

# Make the files executable
chmod +x app/web_app_lite.py
chmod +x app/core/lite_llm_enhancer.py

# Run the Streamlit app with the lite LLM
cd app
echo "Starting Streamlit app with lightweight LLM enhancer..."
streamlit run web_app_lite.py