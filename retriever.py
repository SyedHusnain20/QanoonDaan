"""
retriever.py — QanoonDaan
Hybrid Retriever (FAISS + BM25 + Act-Aware Section Boost)
"""
import os
import pickle
import re
import numpy as np
import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from config import VECTOR_STORE, CHUNKS_STORE, EMBEDDING_MODEL, TOP_K

# ─── Tokenization + section-number helpers ───────────────────────────────────
# Updated regex to catch bare numbers at the start of a line (e.g., "365. Whoever...")
# which is how Pakistani legal documents actually format their sections.
_SECTION_PATTERN = re.compile(
    r"(?:section|sec\.?|دفعہ|سیکشن)\s*[.\-:]?\s*(\d{1,4})"
    r"|(\d{1,4})\s*(?:section|دفعہ|سیکشن)"
    r"|^\s*(\d{1,4})\s*[.\-]",  # Bare number at start of line followed by . or -
    re.IGNORECASE | re.MULTILINE,
)
_TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)
_ACT_STOPWORDS = {
    "the", "of", "act", "code", "ordinance", "law", "pakistan", "and", "for",
}

# Common abbreviations for Pakistani Acts and their significant full-name tokens.
# This bridges the gap between formal names ("Pakistan Penal Code") and 
# typical filename abbreviations ("ppc_1860.pdf").
_ACT_SYNONYMS = {
    "ppc": {"penal"},
    "crpc": {"criminal", "procedure"},
    "cpc": {"civil", "procedure"},
    "peca": {"prevention", "electronic", "crimes"},
    "ata": {"anti", "terrorism"},
    "eta": {"electronic", "transactions"},
}

def _tokenize(text: str) -> list[str]:
    return _TOKEN_PATTERN.findall(text.lower())

def _act_tokens(text: str) -> set[str]:
    """
    Normalizes an Act name OR a source filename into a comparable token set.
    Expands known abbreviations (e.g., 'ppc' -> 'penal') so that 
    'ppc_1860.pdf' correctly matches 'Pakistan Penal Code'.
    """
    if not text:
        return set()
    raw_tokens = re.findall(r"[a-zA-Z]+", text.lower())
    tokens = {t for t in raw_tokens if t not in _ACT_STOPWORDS and len(t) > 1}
    
    # Expand abbreviations to their full-name tokens, and vice versa
    expanded = set(tokens)
    for abbr, full_tokens in _ACT_SYNONYMS.items():
        if abbr in tokens:
            expanded.update(full_tokens)
        if full_tokens.issubset(tokens):
            expanded.add(abbr)
            
    return expanded

def _act_matches_source(act_hint: str, source_filename: str) -> bool:
    """True if the normalized tokens of act_hint and source_filename overlap."""
    if not act_hint:
        return False
    hint_tokens = _act_tokens(act_hint)
    source_tokens = _act_tokens(os.path.splitext(source_filename)[0])
    if not hint_tokens or not source_tokens:
        return False
    return bool(hint_tokens & source_tokens)

def _extract_section_numbers(text: str) -> set[str]:
    """Returns the set of section numbers found in text."""
    found = set()
    for m in _SECTION_PATTERN.finditer(text):
        # group(1) or group(2) are from word-matched patterns, group(3) is bare number
        num = m.group(1) or m.group(2) or m.group(3)
        if num:
            found.add(num.lstrip("0") or "0")
    return found

def _minmax_normalize(scores: np.ndarray) -> np.ndarray:
    """Scales scores to [0, 1] for safe blending."""
    lo, hi = float(scores.min()), float(scores.max())
    if hi - lo < 1e-12:
        return np.zeros_like(scores)
    return (scores - lo) / (hi - lo)

# ─── Retriever Class ─────────────────────────────────────────────────────────
class LegalRetriever:
    VECTOR_WEIGHT = 0.55
    BM25_WEIGHT = 0.45
    SECTION_MATCH_BOOST = 10.0

    def __init__(self):
        print("🔍 Loading FAISS index, BM25 index, and chunks...")

        if not os.path.exists(VECTOR_STORE):
            raise FileNotFoundError(f"FAISS index not found at '{VECTOR_STORE}'.")
        if not os.path.exists(CHUNKS_STORE):
            raise FileNotFoundError(f"Chunks file not found at '{CHUNKS_STORE}'.")

        self.index = faiss.read_index(VECTOR_STORE)
        with open(CHUNKS_STORE, "rb") as f:
            self.chunks = pickle.load(f)

        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self._bm25_corpus_tokens = [_tokenize(c["text"]) for c in self.chunks]
        self.bm25 = BM25Okapi(self._bm25_corpus_tokens)
        self._chunk_sections = [_extract_section_numbers(c["text"]) for c in self.chunks]

        print(f"✅ Retriever ready — {len(self.chunks):,} chunks indexed (hybrid: vector + BM25).\n")

    def retrieve(self, question: str, top_k: int = TOP_K, act_hint: str | None = None) -> list[dict]:
        n = len(self.chunks)
        if n == 0:
            return []

        # 1. Dense vector search across FULL corpus
        query_vector = self.model.encode([question], convert_to_numpy=True)
        query_vector = query_vector / np.linalg.norm(query_vector, axis=1, keepdims=True)
        v_scores, v_indices = self.index.search(query_vector, n)

        vector_scores = np.zeros(n, dtype=np.float64)
        for score, idx in zip(v_scores[0], v_indices[0]):
            if idx != -1:
                vector_scores[idx] = float(score)
        vector_scores = _minmax_normalize(vector_scores)

        # 2. BM25 keyword search across FULL corpus
        bm25_raw_scores = np.array(self.bm25.get_scores(_tokenize(question)), dtype=np.float64)
        bm25_scores = _minmax_normalize(bm25_raw_scores)
 
        # 3. Blend signals
        combined = self.VECTOR_WEIGHT * vector_scores + self.BM25_WEIGHT * bm25_scores

        # 4. Exact section-number boost (Act-aware)
        requested_sections = set()
        for m in _SECTION_PATTERN.finditer(question):
            num = m.group(1) or m.group(2) or m.group(3)
            if num:
                requested_sections.add(num.lstrip("0") or "0")

        if requested_sections:
            number_match_indices = [i for i in range(n) if requested_sections & self._chunk_sections[i]]

            if act_hint:
                act_and_number_match_indices = [
                    i for i in number_match_indices if _act_matches_source(act_hint, self.chunks[i]["source"])
                ]
                if act_and_number_match_indices:
                    for i in act_and_number_match_indices:
                        combined[i] += self.SECTION_MATCH_BOOST
            else:
                for i in number_match_indices:
                    combined[i] += self.SECTION_MATCH_BOOST

        # 5. Take top_k by combined score
        top_k = min(top_k, n)
        top_indices = np.argpartition(-combined, top_k - 1)[:top_k]
        top_indices = top_indices[np.argsort(-combined[top_indices])]

        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            results.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "score": round(float(combined[idx]), 4),
            })

        return results

if __name__ == "__main__":
    retriever = LegalRetriever()
    test_questions = [
        "What is the punishment for theft in Pakistan?",
        "What is Section 420 of the Pakistan Penal Code?",
        "Section 369 PPC",
    ]
    for question in test_questions:
        print(f"❓ Question: {question}")
        results = retriever.retrieve(question)
        for i, result in enumerate(results, 1):
            print(f"📌 Result {i} | Source: {result['source']} | Score: {result['score']}")
            print(f"   {result['text'][:200]}...\n")