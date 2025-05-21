#!/bin/bash

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Activate the virtual environment if it exists
source venv/bin/activate 2>/dev/null || echo "Virtual environment not found, continuing without it"

# Install Streamlit if needed
pip install streamlit

# Make the test file executable
chmod +x app/test_voice.py

# Run the voice test app
cd app
echo "Starting voice input test app..."
streamlit run test_voice.py