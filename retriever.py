"""
retriever.py — QanoonDaan
─────────────────────────────────────────────────────────────
Loads the FAISS index + chunks from vector_store/
→ Takes a user question
→ Converts it to a vector
→ Searches FAISS for the most relevant legal chunks
→ Returns top-K chunks with their source PDF names
─────────────────────────────────────────────────────────────
"""

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config import (
    VECTOR_STORE,
    CHUNKS_STORE,
    EMBEDDING_MODEL,
    TOP_K,
)


class LegalRetriever:
    """Loads the FAISS index once and answers semantic search queries."""

    def __init__(self):
        print("🔍 Loading FAISS index and chunks...")

        # ── Verify files exist ─────────────────────────────────────────────────
        if not os.path.exists(VECTOR_STORE):
            raise FileNotFoundError(
                f"FAISS index not found at '{VECTOR_STORE}'. "
                "Please run ingest.py first."
            )
        if not os.path.exists(CHUNKS_STORE):
            raise FileNotFoundError(
                f"Chunks file not found at '{CHUNKS_STORE}'. "
                "Please run ingest.py first."
            )

        # ── Load FAISS index ───────────────────────────────────────────────────
        self.index = faiss.read_index(VECTOR_STORE)

        # ── Load chunks (text + source) ────────────────────────────────────────
        with open(CHUNKS_STORE, "rb") as f:
            self.chunks = pickle.load(f)

        # ── Load embedding model ───────────────────────────────────────────────
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        print(f"✅ Retriever ready — {len(self.chunks):,} chunks indexed.\n")

    def retrieve(self, question: str, top_k: int = TOP_K) -> list[dict]:
        """
        Given a user question, return the top-K most relevant legal chunks.

        Returns a list of dicts:
        [
            {"text": "...", "source": "peca_2016.pdf", "score": 0.91},
            ...
        ]
        """
        # 1. Embed the question
        query_vector = self.model.encode([question], convert_to_numpy=True)

        # 2. Normalize (must match how we stored embeddings in ingest.py)
        query_vector = query_vector / np.linalg.norm(query_vector, axis=1, keepdims=True)

        # 3. Search FAISS for top-K similar chunks
        scores, indices = self.index.search(query_vector, top_k)

        # 4. Build results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue  # FAISS returns -1 if fewer results than top_k
            chunk = self.chunks[idx]
            results.append({
                "text":   chunk["text"],
                "source": chunk["source"],
                "score":  round(float(score), 4),
            })

        return results


# ── Quick terminal test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    retriever = LegalRetriever()

    test_questions = [
        "What is the punishment for theft in Pakistan?",
        "What are my rights if arrested without a warrant?",
        "What does PECA say about cyberbullying?",
        "How can a woman file for divorce in Pakistan?",
        "What are the minimum wage laws in Pakistan?",
    ]

    for question in test_questions:
        print("=" * 60)
        print(f"❓ Question: {question}")
        print("=" * 60)

        results = retriever.retrieve(question)

        for i, result in enumerate(results, 1):
            print(f"\n📌 Result {i} | Source: {result['source']} | Score: {result['score']}")
            print(f"   {result['text'][:300]}...")  # show first 300 chars

        print()
