"""
config.py
---------
Central place for configuration values: API keys, model names,
file paths, and constants used across the app.
"""

import os

# --- Groq API Key ---
# Best practice: never hardcode secrets.
# Locally: set an environment variable, or use .streamlit/secrets.toml
# On Streamlit Cloud: set it in the app's "Secrets" settings.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# If deployed on Streamlit Cloud with st.secrets, prefer that if present
# and the environment variable wasn't set.
try:
    import streamlit as st
    if not GROQ_API_KEY and "GROQ_API_KEY" in st.secrets:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    # st.secrets raises if no secrets.toml exists at all (e.g. running
    # outside Streamlit) - safe to ignore, we already have the env var path.
    pass

# --- Groq models ---
# Used for summarization (text generation).
GROQ_MODEL = "llama-3.3-70b-versatile"

# Used for speech-to-text. Groq hosts Whisper as an API, so we don't need
# to download/run any model locally (no PyTorch, no FFmpeg required).
GROQ_WHISPER_MODEL = "whisper-large-v3-turbo"

# --- Folder paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCX_OUTPUT_DIR = os.path.join(BASE_DIR, "generated_docs")
DATABASE_PATH = os.path.join(BASE_DIR, "meetings.db")

os.makedirs(DOCX_OUTPUT_DIR, exist_ok=True)
