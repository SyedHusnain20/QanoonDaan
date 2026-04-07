"""
ingest.py — QanoonDaan
─────────────────────────────────────────────────────────────
Reads all PDFs from knowledge_base/
→ Extracts text
→ Splits into overlapping chunks
→ Converts chunks to vectors (embeddings)
→ Saves FAISS index + chunks to vector_store/
─────────────────────────────────────────────────────────────
Run once:  python ingest.py
"""

import os
import pickle
import PyPDF2
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config import (
    KNOWLEDGE_DIR,
    VECTOR_STORE,
    CHUNKS_STORE,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

# ── Known PDFs in knowledge_base/ ─────────────────────────────────────────────
PDF_FILES = [
    "constitution_1973.pdf",
    "criminal_laws_amendment_2023.pdf",
    "criminal_procedure_code.pdf",
    "family_laws.pdf",
    "labor_laws.pdf",
    "pakistan_penal_code.pdf",
    "peca_2016.pdf",
    "peca_amendment_2025.pdf",
]


# ── Step 1: Extract text from a single PDF ─────────────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        print(f"  ✅ Extracted {len(text):,} characters from {os.path.basename(pdf_path)}")
    except Exception as e:
        print(f"  ❌ Failed to read {os.path.basename(pdf_path)}: {e}")
    return text


# ── Step 2: Split text into overlapping chunks ─────────────────────────────────
def split_into_chunks(text: str, source: str) -> list[dict]:
    """
    Split a large text into smaller overlapping chunks.
    Each chunk is stored as a dict with 'text' and 'source' keys.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "source": source,
            })
        start += CHUNK_SIZE - CHUNK_OVERLAP  # overlap so context isn't lost
    return chunks


# ── Step 3: Load all PDFs and build chunk list ─────────────────────────────────
def load_all_pdfs() -> list[dict]:
    """Load every PDF from knowledge_base/ and return all chunks."""
    all_chunks = []
    print("\n📂 Loading PDFs from knowledge_base/...\n")

    for filename in PDF_FILES:
        pdf_path = os.path.join(KNOWLEDGE_DIR, filename)

        if not os.path.exists(pdf_path):
            print(f"  ⚠️  Not found, skipping: {filename}")
            continue

        print(f"📄 Processing: {filename}")
        text = extract_text_from_pdf(pdf_path)

        if not text.strip():
            print(f"  ⚠️  No text extracted (possibly scanned PDF): {filename}")
            continue

        chunks = split_into_chunks(text, source=filename)
        all_chunks.extend(chunks)
        print(f"  📦 Created {len(chunks)} chunks\n")

    return all_chunks


# ── Step 4: Generate embeddings and save FAISS index ──────────────────────────
def build_faiss_index(chunks: list[dict]):
    """Convert chunks to vectors and save FAISS index + chunks to disk."""

    print(f"🤖 Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Extract plain text for embedding
    texts = [chunk["text"] for chunk in chunks]

    print(f"⚡ Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Normalize vectors (improves cosine similarity search)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner Product = cosine similarity
    index.add(embeddings)

    # Save FAISS index
    os.makedirs(os.path.dirname(VECTOR_STORE), exist_ok=True)
    faiss.write_index(index, VECTOR_STORE)
    print(f"\n💾 FAISS index saved → {VECTOR_STORE}")

    # Save chunks (so we can map search results back to text)
    with open(CHUNKS_STORE, "wb") as f:
        pickle.dump(chunks, f)
    print(f"💾 Chunks saved       → {CHUNKS_STORE}")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  ⚖️  QanoonDaan — Knowledge Base Ingestion")
    print("=" * 55)

    # 1. Load all PDFs and chunk them
    chunks = load_all_pdfs()

    if not chunks:
        print("\n❌ No chunks created. Check your knowledge_base/ folder.")
        exit(1)

    print(f"\n✅ Total chunks ready: {len(chunks)}")

    # 2. Embed and save
    build_faiss_index(chunks)

    print("\n🎉 Ingestion complete! You can now run retriever.py")
    print("=" * 55)
