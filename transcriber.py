"""
transcriber.py
--------------
Converts recorded audio into text using Groq's hosted Whisper model.

Why an API instead of local Whisper?
- Streamlit Cloud has no microphone and limited CPU/RAM, so running
  PyTorch + a Whisper model locally is slow and often exceeds free-tier
  resource limits.
- Groq already hosts Whisper (whisper-large-v3-turbo) as an API endpoint,
  so we reuse the same Groq client we use for summarization - one API,
  one API key, no FFmpeg or PyTorch dependency needed.
"""

from groq import Groq
from config import GROQ_API_KEY, GROQ_WHISPER_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def transcribe_audio(audio_bytes: bytes, filename: str = "recording.wav") -> str:
    """
    Transcribe raw audio bytes to text using Groq's Whisper API.

    Args:
        audio_bytes: raw audio file bytes, e.g. from st.audio_input().getvalue()
        filename: filename hint sent with the upload (extension matters
                  for the API to know the audio format).

    Returns:
        The transcribed text as a plain string.
    """
    if not audio_bytes:
        raise ValueError("No audio data provided to transcribe.")

    transcription = _client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model=GROQ_WHISPER_MODEL,
        response_format="text",
    )

    # response_format="text" returns a plain string; some SDK versions may
    # wrap it in an object with a .text attribute, so handle both safely.
    if isinstance(transcription, str):
        return transcription.strip()
    return transcription.text.strip()
