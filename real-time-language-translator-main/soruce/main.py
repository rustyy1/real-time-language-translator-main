import os
import time
import pygame
from gtts import gTTS
import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator
import uuid

translator = Translator()  # Initialize the translator module.
pygame.mixer.init()  # Initialize the mixer module.

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

def translator_function(spoken_text, from_language, to_language):
    return translator.translate(spoken_text, src=from_language, dest=to_language)

def text_to_voice(text_data, to_language):
    filename = f"cache_file_{uuid.uuid4()}.mp3"  # Generate a unique filename.
    myobj = gTTS(text=text_data, lang=to_language, slow=False)
    myobj.save(filename)
    audio = pygame.mixer.Sound(filename)  # Load the sound.
    audio.play()

    while pygame.mixer.get_busy():  # Wait for the audio to finish playing.
        time.sleep(0.1)

    os.remove(filename)

def cleanup():
    pygame.mixer.quit()  # Quit the mixer properly

def main_process(output_placeholder, subtitle_placeholder, from_language, to_language):
    rec = sr.Recognizer()
    with sr.Microphone() as source:
        output_placeholder.text("Listening...")
        rec.pause_threshold = 1

        audio = rec.listen(source, phrase_time_limit=10)

    try:
        output_placeholder.text("Processing...")
        spoken_text = rec.recognize_google(audio, language=from_language)

        output_placeholder.text("Translating...")
        translated_text = translator_function(spoken_text, from_language, to_language)

        # Display the translated text as subtitles
        subtitle_placeholder.markdown(f"*Translated Text:* {translated_text.text}", unsafe_allow_html=True)

        # Show progress bar during text-to-speech conversion
        with st.spinner('Speaking...'):
            text_to_voice(translated_text.text, to_language)

    except Exception as e:
        output_placeholder.text(f"Error: {e}")

# HTML and CSS injection
st.markdown("""
    <style>
    /* General Styles */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
        color: #495057;
        margin: 0;
        padding: 0;
    }

    /* Header Styling */
    .stTitle {
        text-align: center;
        color: #343a40;
        font-size: 2.5rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
        font-weight: bold;
    }

    /* Container for UI elements */
    .stContainer {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    /* Dropdown and Button Styles */
    .stSelectbox, .stButton {
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: 1px solid #ced4da;
        background-color: #ffffff;
        font-size: 1rem;
        color: #495057;
        transition: all 0.3s;
    }

    .stSelectbox:hover, .stButton:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
        cursor: pointer;
    }

    .stButton {
        background-color: #007bff;
        color: #ffffff;
        border: none;
    }

    .stButton:hover {
        background-color: #0056b3;
    }

    /* Progress Spinner Styles */
    .stSpinner {
        color: #007bff;
    }

    /* Subtitle Styling */
    .stSubtitle {
        font-size: 1.25rem;
        color: #007bff;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "isTranslateOn" not in st.session_state:
    st.session_state.isTranslateOn = False

# UI layout
st.markdown('<h1 class="stTitle">Language Translator</h1>', unsafe_allow_html=True)

# Container for UI elements
with st.container():
    # Dropdowns for selecting languages
    col1, col2 = st.columns(2)

    with col1:
        from_language_name = st.selectbox("Select Source Language:", list(LANGUAGES.values()), key="source_language")

    with col2:
        to_language_name = st.selectbox("Select Target Language:", list(LANGUAGES.values()), key="target_language")

    # Convert language names to language codes
    from_language = get_language_code(from_language_name)
    to_language = get_language_code(to_language_name)

    # Buttons to trigger translation
    col3, col4 = st.columns(2)

    with col3:
        start_button = st.button("Start")

    with col4:
        stop_button = st.button("Stop")

    # Create placeholders for output and subtitles
    output_placeholder = st.empty()
    subtitle_placeholder = st.empty()

    # Check if "Start" button is clicked
    if start_button:
        if not st.session_state.isTranslateOn:
            st.session_state.isTranslateOn = True
            main_process(output_placeholder, subtitle_placeholder, from_language, to_language)

    # Check if "Stop" button is clicked
    if stop_button:
        st.session_state.isTranslateOn = False
        cleanup()
