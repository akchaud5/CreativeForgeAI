#!/bin/bash

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Install required packages if needed
pip install -r requirements.txt

# Make the files executable
chmod +x app/web_app_real_llm.py
chmod +x app/core/real_llm_enhancer.py

# Run the Streamlit app with the real LLM
cd app
echo "Starting Streamlit app with DeepSeek LLM..."
streamlit run web_app_real_llm.py