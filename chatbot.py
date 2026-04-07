"""
chatbot.py — QanoonDaan
─────────────────────────────────────────────────────────────
Takes a user question + retrieved legal chunks
→ Detects language
→ Translates to English for FAISS retrieval
→ Sends to Groq with original question language
→ Returns answer in user's language + disclaimer
─────────────────────────────────────────────────────────────
"""

from groq import Groq
from retriever import LegalRetriever
from config import GROQ_API_KEY, GROQ_MODEL, DISCLAIMER, TOP_K


# ── Initialize Groq client ─────────────────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)

# ── Initialize Retriever (loads FAISS index once) ──────────────────────────────
retriever = LegalRetriever()


# ── Step 0: Translate question to English for retrieval ────────────────────────
def translate_to_english(question: str) -> str:
    """
    Uses Groq to detect if the question is non-English.
    If so, translates it to English for better FAISS retrieval.
    Returns the English version of the question.
    """
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a translator. Your only job is to detect the language of the input "
                    "and translate it to English if it is not already in English. "
                    "If the input is already in English, return it exactly as-is. "
                    "Return ONLY the translated English text. No explanations, no extra words."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        temperature=0.0,
        max_tokens=256,
    )
    return response.choices[0].message.content.strip()


# ── Build the prompt ───────────────────────────────────────────────────────────
def build_prompt(original_question: str, chunks: list[dict]) -> str:
    """
    Combine retrieved legal chunks + original user question into a structured prompt.
    The original question (in any language) is passed so the LLM replies in that language.
    """
    context_blocks = ""
    for i, chunk in enumerate(chunks, 1):
        context_blocks += f"""
[Source {i}: {chunk['source']}]
{chunk['text']}
"""

    prompt = f"""You are QanoonDaan, an AI legal assistant specializing in Pakistani law.
You help Pakistani citizens understand their legal rights and obligations in simple, clear language.

You have been provided with relevant excerpts from official Pakistani legal documents.
Use ONLY this context to answer the question. Do not make up laws or sections.
If the context does not contain enough information, say so honestly.

Always:
- Mention the specific law or section you are referencing (e.g., "Under Section 379 of the Pakistan Penal Code...")
- Explain in simple language that a non-lawyer can understand
- Be concise but complete
- If multiple laws apply, mention all of them

─────────────────────────────────────────────────────────────
LEGAL CONTEXT:
{context_blocks}
─────────────────────────────────────────────────────────────
USER QUESTION:
{original_question}
─────────────────────────────────────────────────────────────
YOUR ANSWER:"""

    return prompt


# ── Main function: get answer from Groq ───────────────────────────────────────
def get_legal_answer(question: str) -> dict:
    """
    Full RAG pipeline:
    1. Translate question to English (for FAISS retrieval)
    2. Retrieve relevant chunks using the English translation
    3. Build prompt with original question (preserves language)
    4. Call Groq — replies in user's original language
    5. Return answer + disclaimer
    """

    # Step 1: Translate to English for accurate FAISS retrieval
    english_question = translate_to_english(question)
    print(f"🔄 Translated for retrieval: {english_question}")

    # Step 2: Retrieve using the English translation
    chunks = retriever.retrieve(english_question, top_k=TOP_K)

    if not chunks:
        return {
            "answer": "I could not find relevant legal information for your question.",
            "sources": [],
            "disclaimer": DISCLAIMER,
        }

    # Step 3: Build prompt with the ORIGINAL question (so LLM replies in same language)
    prompt = build_prompt(question, chunks)

    # Step 4: Call Groq API
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are QanoonDaan, a helpful and accurate Pakistani legal advisory assistant. "
                    "Always base your answers strictly on the provided legal context. "
                    "Never fabricate laws, sections, or punishments. "
                    "If the retrieved context is insufficient, say ONLY that you could not find "
                    "specific information and suggest visiting pakistancode.gov.pk or a qualified lawyer. "
                    "Do NOT reference any laws or sections not present in the provided context. "
                    "\n\nCRITICAL — Language Rule: "
                    "Always respond in the SAME language as the user's question. "
                    "If the question is in Roman Urdu, respond in Roman Urdu. "
                    "If the question is in Urdu script, respond in Urdu script. "
                    "If the question is in English, respond in English. "
                    "Never switch languages. Never respond in English if the question was in Urdu."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=1024,
    )

    # Step 5: Extract answer
    answer = response.choices[0].message.content.strip()

    # Step 6: Collect unique source PDFs used
    sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))

    return {
        "answer": answer,
        "sources": sources,
        "disclaimer": DISCLAIMER,
    }


# ── Terminal test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  ⚖️  QanoonDaan — Multilingual Test")
    print("=" * 60)

    test_questions = [
        "What is the punishment for theft in Pakistan?",
        "Pakistan me chor ki saza kia he?",
        "گھریلو تشدد کی سزا کیا ہے؟",
    ]

    for question in test_questions:
        print(f"\n❓ Question: {question}\n")
        result = get_legal_answer(question)
        print(f"⚖️  Answer:\n{result['answer']}")
        print(f"\n{result['disclaimer']}")
        print("\n" + "=" * 60)
