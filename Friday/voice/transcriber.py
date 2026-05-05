import numpy as np
from faster_whisper import WhisperModel

from config.settings import WHISPER_MODEL, WHISPER_DEVICE

print("[transcriber] Loading Whisper model...")
model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type="int8")

def transcribe(audio: np.ndarray) -> str:
    """
    Takes raw int16 numpy array from listener.
    Returns transcribed text as a string.
    """
    # convert int16 → float32 normalized
    audio_float = audio.flatten().astype(np.float32) / 32768.0

    segments, info = model.transcribe(
        audio_float,
        language="en",          # skip language detection, we know it's english
        beam_size=5,            # higher = more accurate but slower
        vad_filter=True,        # faster-whisper has built-in VAD too, helps clean up
    )

    text = " ".join(segment.text.strip() for segment in segments)
    return text.strip()