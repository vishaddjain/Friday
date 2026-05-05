import queue
import threading
import numpy as np
import sounddevice as sd
import torch
from openwakeword.model import Model as WakeWordModel

from config.settings import (
    SAMPLE_RATE, CHANNELS, CHUNK_SAMPLES,
    WAKE_WORD_MODEL, WAKE_WORD_THRESHOLD,
    VAD_THRESHOLD, VAD_SILENCE_MS, VAD_MIN_SPEECH_MS
)

print("[listener] Loading wake word model...")
wake_model = WakeWordModel(wakeword_models=[WAKE_WORD_MODEL], inference_framework="onnx")

print("[listener] Loading VAD model...")
vad_model, _ = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    force_reload=False
)
vad_model.eval()

def _to_tensor(chunk: np.ndarray) -> torch.Tensor:
    """Convert int16 numpy chunk → float32 tensor silero expects."""
    audio = chunk.flatten().astype(np.float32) / 32768.0
    return torch.from_numpy(audio)


def _is_speech(chunk: np.ndarray) -> bool:
    tensor = _to_tensor(chunk)
    prob = vad_model(tensor, SAMPLE_RATE).item()
    return prob > VAD_THRESHOLD


# ── Main function ─────────────────────────────────────────────────────────────
def listen_for_utterance() -> np.ndarray | None:
    """
    Blocks until:
      1. Wake word is detected
      2. User speaks
      3. Silence is detected
    Returns the full utterance as a numpy array, or None on error.
    """
    audio_q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(f"[listener] stream status: {status}")
        audio_q.put(indata.copy())

    print("[listener] Listening for wake word...")

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        blocksize=CHUNK_SAMPLES,
        callback=callback,
    ):
        # ── Phase 1: wait for wake word ───────────────────────────────────
        while True:
            chunk = audio_q.get()
            prediction = wake_model.predict(chunk.flatten())
            score = prediction.get(WAKE_WORD_MODEL, 0.0)
            if score >= WAKE_WORD_THRESHOLD:
                print(f"[listener] Wake word detected! (score={score:.2f})")
                break

        # ── Phase 2: accumulate utterance via VAD ─────────────────────────
        print("[listener] Listening for speech...")

        utterance    = []
        silence_ms   = 0
        speaking     = False
        speech_ms    = 0

        silence_chunks_needed = VAD_SILENCE_MS // (CHUNK_SAMPLES * 1000 // SAMPLE_RATE)

        while True:
            chunk = audio_q.get()

            if _is_speech(chunk):
                utterance.append(chunk)
                speech_ms += CHUNK_SAMPLES * 1000 // SAMPLE_RATE
                silence_ms = 0
                speaking = True
            else:
                if speaking:
                    utterance.append(chunk)   # include trailing silence
                    silence_ms += CHUNK_SAMPLES * 1000 // SAMPLE_RATE

                    if silence_ms >= VAD_SILENCE_MS:
                        # check we got enough actual speech
                        if speech_ms >= VAD_MIN_SPEECH_MS:
                            print(f"[listener] Utterance captured ({speech_ms}ms speech)")
                            break
                        else:
                            # too short, reset and wait again
                            utterance = []
                            silence_ms = 0
                            speech_ms = 0
                            speaking = False

    if not utterance:
        return None

    return np.concatenate(utterance, axis=0)