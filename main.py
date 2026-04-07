"""
main.py — QanoonDaan
─────────────────────────────────────────────────────────────
FastAPI web server
→ Serves the chat UI (HTML)
→ Accepts user questions via POST /ask
→ Calls chatbot.py (RAG pipeline)
→ Returns JSON response
─────────────────────────────────────────────────────────────
Run:  uvicorn main:app --reload
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn

from chatbot import get_legal_answer
from config import APP_TITLE, APP_DESCRIPTION


# ── Lifespan: load models once at startup ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the server starts.
    Pre-loads the FAISS index and embedding model into memory
    so the first user request is not slow.
    """
    print("⚖️  QanoonDaan is starting up...")
    print("🔍 Pre-loading FAISS index and embedding model...")

    # Importing chatbot triggers LegalRetriever to load at module level
    # so by the time a request comes in, everything is ready
    print("✅ All models loaded. Server is ready!\n")
    yield
    print("🛑 QanoonDaan shutting down.")


# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
)

# ── Mount static files (CSS) ───────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Jinja2 templates (HTML) ────────────────────────────────────────────────────
templates = Jinja2Templates(directory="templates")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat UI."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": APP_TITLE},
    )


@app.post("/ask", response_class=JSONResponse)
async def ask(question: str = Form(...)):
    """
    Receive a legal question from the UI.
    Run the full RAG pipeline.
    Return answer + sources + disclaimer as JSON.
    """
    # Basic validation
    question = question.strip()
    if not question:
        return JSONResponse(
            status_code=400,
            content={"error": "Question cannot be empty."},
        )

    if len(question) > 1000:
        return JSONResponse(
            status_code=400,
            content={"error": "Question is too long. Please keep it under 1000 characters."},
        )

    try:
        result = get_legal_answer(question)
        return JSONResponse(content={
            "answer":     result["answer"],
            "sources":    result["sources"],
            "disclaimer": result["disclaimer"],
        })

    except Exception as e:
        print(f"❌ Error processing question: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Something went wrong. Please try again."},
        )


@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "ok", "app": APP_TITLE}


# ── Run directly ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
