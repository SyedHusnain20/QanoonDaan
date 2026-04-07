"""
app.py — QanoonDaan
─────────────────────────────────────────────────────────────
Entry point for Hugging Face Spaces.
HF Spaces looks for app.py by default.
This simply runs the FastAPI app via uvicorn.
─────────────────────────────────────────────────────────────
"""

import uvicorn
from main import app  # noqa: F401 — imported so HF can find it

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7860,          # HF Spaces always uses port 7860
        reload=False,       # No reload in production
    )
