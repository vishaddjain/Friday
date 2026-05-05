from pathlib import Path 
from dotenv import load_dotenv
import os

load_dotenv()

#Paths

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "models"
VOICES_DIR = MODELS_DIR / "voices"
DB_DIR = DATA_DIR / "db"

for d in [DATA_DIR, MODELS_DIR, VOICES_DIR, DB_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Audio ──────────────────────────────────────────────────
SAMPLE_RATE    = 16000   
CHANNELS       = 1       
CHUNK_MS       = 32      
CHUNK_SAMPLES  = 512 

# ── Wake Word ──────────────────────────────────────────────
WAKE_WORD_MODEL     = "hey_jarvis"   
WAKE_WORD_THRESHOLD = 0.3            

# ── VAD (Voice Activity Detection) ────────────────────────
VAD_THRESHOLD        = 0.5   
VAD_SILENCE_MS       = 800   
VAD_MIN_SPEECH_MS    = 200   

# ── STT (Whisper) ──────────────────────────────────────────
WHISPER_MODEL  = "base.en"   
WHISPER_DEVICE = "cpu"       

# ── TTS (Piper) ────────────────────────────────────────────
PIPER_VOICE    = VOICES_DIR / "en_US-lessac-medium.onnx"
PIPER_BINARY   = "/usr/local/bin/piper"   

# ── LLM ────────────────────────────────────────────────────
OLLAMA_URL     = "http://localhost:11434"
OLLAMA_MODEL   = "phi3:mini"
#CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")   # fallback

# ── Secrets ────────────────────────────────────────────────
#HA_URL   = os.getenv("HA_URL")    
#HA_TOKEN = os.getenv("HA_TOKEN")  
