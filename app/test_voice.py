#!/usr/bin/env python3
"""
Simple test script for the voice-to-text component.
This is a standalone Streamlit app that allows testing the voice input component.
"""

import streamlit as st
from voice_to_text import voice_input_area, create_voice_to_text

def main():
    st.set_page_config(
        page_title="Voice Input Test",
        page_icon="🎤",
        layout="wide"
    )
    
    st.title("🎤 Voice-to-Text Component Test")
    st.subheader("Test the voice input functionality for the Creative AI Pipeline")
    
    # Direct component test
    st.markdown("## 1. Basic Voice Component")
    st.markdown("This tests the raw voice component without text area.")
    
    voice_result = create_voice_to_text(
        language="en-US",
        continuous=False,
        placeholder="Click to start recording",
        key="simple_test"
    )
    
    st.markdown("**Result:**")
    st.markdown(f"Voice input: {voice_result}")
    
    # Voice input area test
    st.markdown("## 2. Voice Input Area")
    st.markdown("This tests the combined voice input with text area.")
    
    voice_text = voice_input_area(
        label="Test Voice Input",
        placeholder="Click to speak...",
        key="area_test"
    )
    
    if st.button("Process Input"):
        st.markdown("**Result:**")
        st.markdown(f"Processed text: {voice_text}")
        
        if voice_text:
            # Simulate processing
            st.success("Voice input successfully received and processed!")
            
            # Show what would happen in the main app
            enhanced = voice_text + " (This would be enhanced with the LLM)"
            st.markdown("**Enhanced prompt would be:**")
            st.markdown(f"`{enhanced}`")
        else:
            st.error("No input received. Please speak or type something.")
    
    # Language tests
    st.markdown("## 3. Different Languages")
    
    language = st.selectbox(
        "Select language for voice recognition:",
        options=[
            "en-US", "en-GB", "fr-FR", "de-DE", "es-ES", 
            "it-IT", "pt-BR", "ja-JP", "ko-KR", "zh-CN"
        ]
    )
    
    voice_lang_test = voice_input_area(
        label=f"Test Voice Input ({language})",
        language=language,
        placeholder=f"Click to speak in {language}...",
        key="lang_test"
    )
    
    if st.button("Process Language Input"):
        st.markdown("**Result:**")
        st.markdown(f"Recognized text ({language}): {voice_lang_test}")
    
    # Additional settings
    st.markdown("## Settings and Information")
    st.info("""
    **How it works:**
    - Uses the Web Speech API built into modern browsers
    - No data is sent to external servers (browser-native functionality)
    - May require microphone permission from your browser
    - Works best in Chrome, Edge, and Safari (Firefox support is limited)
    
    **Troubleshooting:**
    - Make sure your microphone is connected and working
    - Allow microphone access when prompted by the browser
    - If you don't see any results, try a different browser
    """)

if __name__ == "__main__":
    main()