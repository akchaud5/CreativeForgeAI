"""
Voice-to-text component for Streamlit using browser's Web Speech API.
This component allows users to input prompts by speaking instead of typing.
"""

import os
import streamlit as st
import streamlit.components.v1 as components
import json
from typing import Optional, Callable

# Get the directory of this file
COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_voice_to_text(
    language: str = "en-US",
    continuous: bool = False,
    placeholder: str = "Click to speak...",
    key: Optional[str] = None,
    callback: Optional[Callable[[str], None]] = None
) -> str:
    """
    Create a voice-to-text component that uses the browser's Web Speech API.
    
    Args:
        language: Speech recognition language (default: "en-US")
        continuous: Whether to continuously listen for speech (default: False)
        placeholder: Text to show in the button when not recording
        key: Optional unique key for the component instance
        callback: Optional callback function to call when speech is recognized
        
    Returns:
        str: The recognized text
    """
    # Create a unique key if none is provided
    if key is None:
        key = "voice_input_" + str(id(placeholder))
    
    # Create a unique session state key for storing the result
    result_key = f"{key}_result"
    
    # Initialize session state for storing the result
    if result_key not in st.session_state:
        st.session_state[result_key] = ""
    
    # Define the HTML/JS code for the voice-to-text component
    component_html = f"""
    <script>
    // Voice-to-text component using Web Speech API
    const setupVoiceInput = () => {{
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            console.error('Speech recognition not supported in this browser');
            document.getElementById('voice-button-{key}').innerText = 'Speech recognition not supported';
            document.getElementById('voice-button-{key}').disabled = true;
            return;
        }}
        
        // Create speech recognition object
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        // Configure recognition
        recognition.lang = '{language}';
        recognition.continuous = {str(continuous).lower()};
        recognition.interimResults = false;
        
        // Variables to track state
        let isListening = false;
        const button = document.getElementById('voice-button-{key}');
        const status = document.getElementById('voice-status-{key}');
        
        // Handle start/stop button
        button.onclick = () => {{
            if (isListening) {{
                recognition.stop();
                button.classList.remove('recording');
                button.innerText = '{placeholder}';
                status.innerText = '';
            }} else {{
                recognition.start();
                button.classList.add('recording');
                button.innerText = 'Listening... Click to stop';
                status.innerText = 'Listening...';
            }}
            isListening = !isListening;
        }};
        
        // Handle speech recognition results
        recognition.onresult = (event) => {{
            const transcript = event.results[0][0].transcript;
            document.getElementById('voice-output-{key}').innerText = transcript;
            
            // Send result back to Streamlit
            const data = {{
                result: transcript,
                key: '{result_key}'
            }};
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: data
            }}, '*');
        }};
        
        // Handle errors
        recognition.onerror = (event) => {{
            console.error('Speech recognition error', event.error);
            status.innerText = 'Error: ' + event.error;
            button.classList.remove('recording');
            button.innerText = '{placeholder}';
            isListening = false;
        }};
        
        // Handle end of speech recognition
        recognition.onend = () => {{
            button.classList.remove('recording');
            button.innerText = '{placeholder}';
            status.innerText = '';
            isListening = false;
        }};
    }};
    
    // Set up when the document is loaded
    document.addEventListener('DOMContentLoaded', setupVoiceInput);
    </script>
    
    <style>
    .voice-container {{
        margin-bottom: 10px;
    }}
    .voice-button {{
        background-color: #f0f2f6;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 10px 15px;
        font-size: 14px;
        cursor: pointer;
        transition: background-color 0.3s, color 0.3s;
        width: 100%;
        text-align: center;
    }}
    .voice-button:hover {{
        background-color: #e0e2e6;
    }}
    .voice-button.recording {{
        background-color: #ff4b4b;
        color: white;
        animation: pulse 1.5s infinite;
    }}
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
        100% {{ opacity: 1; }}
    }}
    .voice-status {{
        font-size: 12px;
        color: #888;
        height: 16px;
        margin-top: 4px;
        text-align: center;
    }}
    .voice-output {{
        display: none;
    }}
    </style>
    
    <div class="voice-container">
        <button id="voice-button-{key}" class="voice-button">{placeholder}</button>
        <div id="voice-status-{key}" class="voice-status"></div>
        <div id="voice-output-{key}" class="voice-output"></div>
    </div>
    """
    
    # Render the HTML component
    components.html(component_html, height=100)
    
    # Handle the result from the component
    component_value = st.session_state.get(result_key, "")
    
    # Call the callback function if provided and there's a new result
    if callback is not None and component_value:
        callback(component_value)
    
    return component_value

def voice_input_area(
    label: str = "Voice Input",
    language: str = "en-US", 
    placeholder: str = "Click to speak...",
    key: Optional[str] = None
) -> str:
    """
    Create a voice input area with both a microphone button and a text area.
    
    Args:
        label: Label for the input area
        language: Speech recognition language
        placeholder: Text to show in the button when not recording
        key: Optional unique key for the component
        
    Returns:
        str: The input text (either from voice or manual typing)
    """
    if key is None:
        key = "voice_input_" + str(id(label))
    
    text_key = f"{key}_text"
    
    if text_key not in st.session_state:
        st.session_state[text_key] = ""
    
    st.markdown(f"### {label}")
    
    # Define callback to update text area when speech is recognized
    def update_text_area(text):
        st.session_state[text_key] = text
    
    # Create the voice input component
    voice_result = create_voice_to_text(
        language=language,
        placeholder=placeholder,
        key=key,
        callback=update_text_area
    )
    
    # If we got new voice input, update the text area
    if voice_result:
        st.session_state[text_key] = voice_result
    
    # Create a text area that shows the recognized speech and allows manual editing
    text_input = st.text_area(
        label="Edit or type manually if needed:",
        value=st.session_state[text_key],
        key=text_key,
        height=100
    )
    
    # Return either the voice result or the edited text
    return text_input