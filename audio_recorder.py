"""
audio_recorder.py
------------------
Handles recording audio from the microphone and saving it as a .wav file.

Design note:
Streamlit reruns the whole script on every interaction, so we can't use a
simple blocking "record for N seconds" call triggered by a button press in
the usual way. Instead, we expose a class-based recorder that:
  1. Starts a background audio stream when the user clicks "Start Recording".
  2. Continuously buffers audio frames while recording is active.
  3. Stops the stream and writes the buffered audio to a .wav file when the
     user clicks "Stop Recording".

This class is imported and controlled by app.py (the Streamlit UI).
"""

import os
import queue
import datetime
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as wav_write

from config import SAMPLE_RATE, CHANNELS, RECORDINGS_DIR


class AudioRecorder:
    """Records microphone audio in a background stream until stopped."""

    def __init__(self, sample_rate=SAMPLE_RATE, channels=CHANNELS):
        self.sample_rate = sample_rate
        self.channels = channels
        self._audio_queue = queue.Queue()   # thread-safe buffer for audio chunks
        self._stream = None
        self.is_recording = False

    def _callback(self, indata, frames, time_info, status):
        """
        Called automatically by sounddevice on a separate audio thread
        for every small chunk of captured audio. We just push the chunk
        into a queue so the main thread can collect it later.
        """
        if status:
            # Non-fatal warnings (e.g. buffer overflow) get printed, not raised.
            print(f"Recording status warning: {status}")
        self._audio_queue.put(indata.copy())

    def start(self):
        """Begin capturing audio from the default microphone."""
        if self.is_recording:
            return  # already recording, do nothing

        # Clear any leftover data from a previous session.
        self._audio_queue = queue.Queue()

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self._callback,
        )
        self._stream.start()
        self.is_recording = True

    def stop_and_save(self) -> str:
        """
        Stop capturing audio and write everything collected so far
        to a timestamped .wav file. Returns the path to the saved file.
        """
        if not self.is_recording:
            raise RuntimeError("Recorder is not currently recording.")

        self._stream.stop()
        self._stream.close()
        self.is_recording = False

        # Drain the queue into a single numpy array.
        chunks = []
        while not self._audio_queue.empty():
            chunks.append(self._audio_queue.get())

        if not chunks:
            raise RuntimeError("No audio was captured. Check your microphone.")

        audio_data = np.concatenate(chunks, axis=0)

        # Convert float32 samples (-1.0 to 1.0) to int16 PCM, which is the
        # standard format for .wav files and what Whisper expects.
        audio_int16 = np.int16(audio_data * 32767)

        # Build a unique filename using the current timestamp.
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meeting_{timestamp}.wav"
        filepath = os.path.join(RECORDINGS_DIR, filename)

        wav_write(filepath, self.sample_rate, audio_int16)

        return filepath
