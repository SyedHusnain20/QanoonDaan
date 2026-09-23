import os
from dotenv import load_dotenv

load_dotenv() 

# ── Groq API ────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
# ── Embedding Model ────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # fast, lightweight, good accuracy

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR   = os.path.join(BASE_DIR, "knowledge_base")
VECTOR_STORE    = os.path.join(BASE_DIR, "vector_store", "faiss_index.bin")
CHUNKS_STORE    = os.path.join(BASE_DIR, "vector_store", "chunks.pkl")

# ── RAG Settings ───────────────────────────────────────────────────────────────
CHUNK_SIZE      = 500     # characters per chunk
CHUNK_OVERLAP   = 50      # overlap between chunks to preserve context
TOP_K           = 3       # number of relevant chunks to retrieve

# ── App Settings ───────────────────────────────────────────────────────────────
APP_TITLE       = "QanoonDaan ⚖️"
APP_DESCRIPTION = "Your AI-powered Pakistani Legal Advisory Assistant"
DISCLAIMER      = (
    "⚠️ Disclaimer: This response is for informational purposes only "
    "and does not constitute professional legal advice. "
    "Please consult a qualified lawyer for your specific situation."
)
