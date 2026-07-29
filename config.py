"""
config.py
---------
Central place for configuration values: API keys, model names,
file paths, and constants used across the app.
"""

import os

# --- Groq API Key ---
# Best practice: never hardcode secrets. Read from an environment variable.
# Set it in your terminal before running:
#   Windows (PowerShell): $env:GROQ_API_KEY="your_key_here"
#   Mac/Linux:            export GROQ_API_KEY="your_key_here"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# --- Groq model to use for summarization ---
# llama-3.3-70b-versatile is a strong, fast general-purpose model on Groq.
GROQ_MODEL = "llama-3.3-70b-versatile"

# --- Whisper model size ---
# Options: tiny, base, small, medium, large (bigger = more accurate, slower).
# "base" is a good balance for a first working version.
WHISPER_MODEL_SIZE = "base"

# --- Audio recording settings ---
SAMPLE_RATE = 16000   # 16kHz is what Whisper expects; keeps file size small
CHANNELS = 1          # Mono audio is sufficient for speech

# --- Folder paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = os.path.join(BASE_DIR, "recordings")
DOCX_OUTPUT_DIR = os.path.join(BASE_DIR, "generated_docs")
DATABASE_PATH = os.path.join(BASE_DIR, "meetings.db")

# Ensure the folders exist when the app starts.
os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(DOCX_OUTPUT_DIR, exist_ok=True)
