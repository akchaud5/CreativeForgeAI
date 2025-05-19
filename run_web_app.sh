#!/bin/bash

# Install required packages if needed
if ! command -v streamlit &> /dev/null
then
    echo "Installing Streamlit..."
    pip install -r requirements.txt
fi

# Run the Streamlit app
cd app
streamlit run web_app.py