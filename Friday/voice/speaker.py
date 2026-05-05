import subprocess

def speak(text: str) -> None:
    """
    Speaks the given text using Mac's built-in TTS.
    Replace with Piper later for better voice quality.
    """
    print(f"[speaker] {text}")
    subprocess.run(["say", text])