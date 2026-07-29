"""
transcriber.py
--------------
Converts a .wav audio file into text using OpenAI's Whisper model
(running locally, not via API).
"""

import whisper
from config import WHISPER_MODEL_SIZE

# Whisper models are large (tens to hundreds of MB) and slow to load.
# We cache the loaded model in a module-level variable so it's only
# loaded once per app run, not on every transcription request.
_model = None


def _get_model():
    """Load the Whisper model once and reuse it on subsequent calls."""
    global _model
    if _model is None:
        _model = whisper.load_model(WHISPER_MODEL_SIZE)
    return _model


def transcribe_audio(wav_path: str) -> str:
    """
    Transcribe the given .wav file to text.

    Args:
        wav_path: path to a .wav audio file on disk.

    Returns:
        The transcribed text as a single string.
    """
    model = _get_model()

    # fp16=False avoids a warning/error on machines without a compatible GPU
    # (CPU-only inference falls back to fp32 automatically).
    result = model.transcribe(wav_path, fp16=False)

    return result["text"].strip()
