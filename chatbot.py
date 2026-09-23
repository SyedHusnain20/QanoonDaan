"""
chatbot.py — QanoonDaan
Pakistani Legal Advisory RAG Chatbot
"""
import json
import re
from groq import Groq, RateLimitError
from retriever import LegalRetriever, _act_matches_source
from config import GROQ_API_KEY, GROQ_MODEL, DISCLAIMER, TOP_K

# Raised when Groq daily/per-minute token limit is hit
class GroqRateLimitError(Exception):
    pass

RATE_LIMIT_MESSAGE = "High traffic right now, please try again after some time."

# ─── Initialization ──────────────────────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)
retriever = LegalRetriever()

# ─── Language Detection ──────────────────────────────────────────────────────
def detect_language(text: str) -> str:
    """Detect if text is English, Urdu script, or Roman Urdu."""
    urdu_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if urdu_chars > 5 and urdu_chars > latin_chars * 0.3:
        return "urdu_script"
    
    # Heuristic for Roman Urdu
    roman_indicators = ['kya', 'hai', 'kaise', 'mujhe', 'karna', 'saza', 'chor', 'police', 'wala', 'mein', 'se', 'ka', 'ki']
    text_lower = text.lower()
    if any(word in text_lower for word in roman_indicators):
        return "roman_urdu"
        
    return "english"

# ─── Script Purity Utilities ─────────────────────────────────────────────────
_ALLOWED_SCRIPT_PATTERN = re.compile(
    r"["
    r"\u0000-\u007F"  # Basic Latin
    r"\u0080-\u00FF"  # Latin-1 Supplement
    r"\u0600-\u06FF"  # Arabic block (Urdu)
    r"\u0750-\u077F"  # Arabic Supplement
    r"\u08A0-\u08FF"  # Arabic Extended-A
    r"\uFB50-\uFDFF"  # Arabic Presentation Forms-A
    r"\uFE70-\uFEFF"  # Arabic Presentation Forms-B
    r"\u200B-\u200F"  # Zero-width / directional marks
    r"\u2010-\u2027"  # General punctuation
    r"\u2030-\u205E"  # More general punctuation
    r"\u20A0-\u20CF"  # Currency symbols
    r"\uFF01-\uFF5E"  # Fullwidth ASCII variants
    r"]+"
)

def _foreign_script_chars(text: str) -> list[str]:
    allowed_spans = {m.span() for m in _ALLOWED_SCRIPT_PATTERN.finditer(text)}
    foreign = []
    pos = 0
    for ch in text:
        in_allowed = any(start <= pos < end for start, end in allowed_spans)
        if not in_allowed and not ch.isspace():
            foreign.append(ch)
        pos += 1
    return foreign

def contains_foreign_script(text: str) -> bool:
    return bool(_foreign_script_chars(text))

def strip_foreign_script(text: str) -> str:
    foreign_chars = set(_foreign_script_chars(text))
    if not foreign_chars:
        return text
    cleaned = "".join(ch for ch in text if ch not in foreign_chars)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return cleaned.strip()

# ─── LLM Helper ──────────────────────────────────────────────────────────────
def _call_groq(system_prompt: str, user_prompt: str, temperature: float = 0.2, max_tokens: int = 1024) -> str:
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        raise GroqRateLimitError(RATE_LIMIT_MESSAGE)

# ─── Classification & Translation ────────────────────────────────────────────
CLASSIFICATION_SYSTEM_PROMPT = """You are a routing and translation assistant for QanoonDaan.
Return ONLY a single JSON object.
Fields:
- "query_type": "general_legal", "section_lookup", "greeting", "off_topic", "harmful", "ambiguous"
- "sections": array of section numbers (strings).
- "act": name of Act (string).
- "translated_question": English translation.
- "legal_concepts": array of formal legal terms (for general_legal only).

Examples:
{"query_type": "section_lookup", "sections": ["365"], "act": "Pakistan Penal Code", "translated_question": "What is Section 365?", "legal_concepts": []}
{"query_type": "general_legal", "sections": [], "act": "", "translated_question": "Boss not paying salary", "legal_concepts": ["non-payment of wages", "Payment of Wages Act"]}"""

def classify_and_translate(question: str) -> dict:
    raw = _call_groq(CLASSIFICATION_SYSTEM_PROMPT, question, temperature=0.0, max_tokens=400)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        data = {}

    return {
        "query_type": data.get("query_type") or "general_legal",
        "sections": data.get("sections") or [],
        "act": data.get("act") or "",
        "translated_question": data.get("translated_question") or question,
        "legal_concepts": data.get("legal_concepts") or [],
    }

# ─── Short-Circuit & Fallback Replies ────────────────────────────────────────
SHORT_CIRCUIT_TASKS = {
    "greeting": "Greet briefly, mention you are QanoonDaan.",
    "off_topic": "Politely explain you only answer Pakistani law questions.",
    "harmful": "Politely decline to help with illegal actions.",
    "ambiguous": "Ask ONE specific clarifying question."
}

def short_circuit_reply(question: str, kind: str) -> str:
    detected_lang = detect_language(question)
    lang_instruction = {
        "english": "Reply in ENGLISH.",
        "urdu_script": "Reply in URDU SCRIPT using ONLY Urdu/Arabic characters.",
        "roman_urdu": "Reply in ROMAN URDU."
    }[detected_lang]
    
    instruction = SHORT_CIRCUIT_TASKS.get(kind, SHORT_CIRCUIT_TASKS["off_topic"])
    system_prompt = f"You are QanoonDaan. {lang_instruction} Keep it 1-3 sentences. Task: {instruction}"
    reply = _call_groq(system_prompt, question, temperature=0.3, max_tokens=150)
    return strip_foreign_script(reply) if contains_foreign_script(reply) else reply

def no_context_fallback_reply(question: str) -> str:
    detected_lang = detect_language(question)
    lang_instruction = {
        "english": "Reply in ENGLISH.",
        "urdu_script": "Reply in URDU SCRIPT.",
        "roman_urdu": "Reply in ROMAN URDU."
    }[detected_lang]
    
    system_prompt = (
        f"You are QanoonDaan. Database returned no results. {lang_instruction} "
        "In 2-3 sentences: (1) apologize, (2) say database doesn't cover this, "
        "(3) recommend pakistancode.gov.pk or a lawyer."
    )
    reply = _call_groq(system_prompt, question, temperature=0.3, max_tokens=200)
    return strip_foreign_script(reply) if contains_foreign_script(reply) else reply

def section_not_found_reply(question: str, requested_sections: list[str], requested_act: str) -> str:
    detected_lang = detect_language(question)
    lang_instruction = {
        "english": "Reply in ENGLISH.",
        "urdu_script": "Reply in URDU SCRIPT.",
        "roman_urdu": "Reply in ROMAN URDU."
    }[detected_lang]
    
    section_list = ", ".join(requested_sections)
    plural = "s" if len(requested_sections) > 1 else ""
    act_note = f" of {requested_act}" if requested_act else ""
    
    system_prompt = (
        f"You are QanoonDaan. Section{plural} {section_list}{act_note} not found. {lang_instruction} "
        "In 2-3 sentences: (1) say section not found, (2) may not be in current sources, "
        "(3) recommend pakistancode.gov.pk or lawyer."
    )
    reply = _call_groq(system_prompt, question, temperature=0.2, max_tokens=200)
    return strip_foreign_script(reply) if contains_foreign_script(reply) else reply

# ─── Section Extraction & Verification ───────────────────────────────────────
def extract_requested_section(question: str) -> str | None:
    pattern = re.compile(
        r"(?:section|sec\.?|دفعہ|سیکشن)\s*[.\-:]?\s*(\d{1,4})"
        r"|(\d{1,4})\s*(?:section|دفعہ|سیکشن)",
        re.IGNORECASE,
    )
    match = pattern.search(question)
    if not match:
        return None
    return match.group(1) or match.group(2)

def section_found_in_chunks(
section_number: str,
chunks: list[dict],
act_hint: str | None = None,
) -> bool:
    # Updated to catch bare numbers at the start of a line (e.g., "365.")
    pattern = re.compile(
        rf"(?:section|sec\.?)\s*0*{re.escape(section_number)}\b"
        rf"|^\s*0*{re.escape(section_number)}\s*[.\-]",
        re.IGNORECASE | re.MULTILINE
    )
    for chunk in chunks:
        if not pattern.search(chunk["text"]):
            continue
        if not act_hint:
            return True
        if _act_matches_source(act_hint, chunk.get("source", "")):
            return True
    return False

# ─── Prompt Building ─────────────────────────────────────────────────────────
ANSWER_SYSTEM_PROMPT = """You are QanoonDaan, a Pakistani legal information assistant.
Base answers STRICTLY on the provided context. Never fabricate laws.

CRITICAL RULE — OUT OF SCOPE:
If the user asks about a specific Act, law, or topic that is NOT present in the provided context,
you MUST respond with ONLY this message (translated to the user's language):
"I don't have information about [law name] in my current knowledge base. Please visit pakistancode.gov.pk or consult a qualified lawyer."
DO NOT mention any other law or information you found in the context.
DO NOT say "however" and then describe something else. Just stop.

RESPONSE STRUCTURE (only when the asked law IS in context):
(a) Plain-language explanation: 2-4 sentences explaining the law in everyday words.
(b) Legal basis: Cite the specific section(s)/act(s) from the context naturally.
(c) Closing recommendation: Always recommend visiting pakistancode.gov.pk or a lawyer.

LANGUAGE RULE: Respond in the SAME language as the user's question.
SCRIPT PURITY: If writing Urdu script, use ONLY Urdu/Arabic characters. No Korean/Chinese/Cyrillic.
WORD PURITY: Every word must belong to the response language (e.g., use 'visit karein', not 'visita').

EXAMPLE CORRECT OUTPUT (law is in context):
A woman in Pakistan can end her marriage by exercising the right of Khula or approaching a family court. This is based on Section X of the Y Act. I recommend visiting pakistancode.gov.pk for details.

EXAMPLE CORRECT OUTPUT (law is NOT in context):
I don't have information about the Companies Act 2017 in my current knowledge base. Please visit pakistancode.gov.pk or consult a qualified lawyer.

INCORRECT OUTPUT (Never do this):
"The context does not mention X. However, it does mention Y which says..."
"X is not in my sources, but related law Z states..."
1. EXPLANATION: ...
2. BASIS: ..."""

def build_prompt(original_question: str, chunks: list[dict], requested_sections: list[str] | None = None, asked_act: str = "") -> str:
    context_blocks = ""
    for i, chunk in enumerate(chunks, 1):
        context_blocks += f"\n[Source {i}: {chunk['source']}]\n{chunk['text']}\n"

    if requested_sections is None:
        single = extract_requested_section(original_question)
        requested_sections = [single] if single else []

    retrieval_check = ""
    if requested_sections:
        found = [s for s in requested_sections if section_found_in_chunks(s, chunks)]
        missing = [s for s in requested_sections if s not in found]

        lines = ["─" * 63, "RETRIEVAL CHECK:"]
        if found:
            lines.append(f"Section(s) {', '.join(found)} ARE present — base explanation on this text.")
        if missing:
            lines.append(f"Section(s) {', '.join(missing)} NOT found. State plainly they were not found.")
        retrieval_check = "\n".join(lines) + "\n"

    # Tell the model what law was explicitly asked for so it can apply the out-of-scope rule
    scope_note = ""
    if asked_act:
        scope_note = f"ASKED LAW: The user is specifically asking about \"{asked_act}\". If this law is not present in the context sources above, apply the OUT OF SCOPE rule — do not discuss other laws found in context.\n"

    return f"""You are QanoonDaan. Use ONLY the provided context.
LEGAL CONTEXT:
{context_blocks}
{scope_note}{retrieval_check}─────────────────────────────────────────────────────────────
USER QUESTION:
{original_question}
─────────────────────────────────────────────────────────────
YOUR ANSWER:"""

# ─── Main Pipeline ───────────────────────────────────────────────────────────
def get_legal_answer(question: str, history: list[dict] | None = None) -> dict:
    try:
        return _get_legal_answer_internal(question, history=history or [])
    except GroqRateLimitError:
        print("⚠️ Groq rate limit hit — returning user-facing fallback.")
        return {
            "answer": RATE_LIMIT_MESSAGE,
            "sources": [],
            "disclaimer": DISCLAIMER,
        }

def _get_legal_answer_internal(question: str, history: list[dict] | None = None) -> dict:
    # 1. Classify & Translate
    classification = classify_and_translate(question)
    query_type = classification["query_type"]
    english_question = classification["translated_question"]
    requested_sections = classification["sections"]
    requested_act = classification["act"]
    legal_concepts = classification["legal_concepts"]
    
    print(f"🔎 Query type: {query_type} | sections: {requested_sections} | act: {requested_act!r} | concepts: {legal_concepts}")

    # 2a. Short-circuit
    if query_type in ("greeting", "off_topic", "harmful", "ambiguous"):
        return {
            "answer": short_circuit_reply(question, query_type),
            "sources": [],
            "disclaimer": DISCLAIMER,
        }

    # 2b. Build retrieval query
    if query_type == "general_legal" and legal_concepts:
        retrieval_query = english_question + ". Relevant legal concepts: " + ", ".join(legal_concepts)
    elif query_type == "section_lookup" and requested_sections:
        section_tokens = " ".join(f"Section {s}" for s in requested_sections)
        retrieval_query = f"{section_tokens} {requested_act} {english_question}".strip()
    else:
        retrieval_query = english_question

    effective_top_k = max(TOP_K, 8) if query_type == "section_lookup" else max(TOP_K, 5)
    chunks = retriever.retrieve(retrieval_query, top_k=effective_top_k, act_hint=requested_act)

    # 2c. Fallback retry for section lookups
    if query_type == "section_lookup" and requested_sections:
        still_missing = [s for s in requested_sections if not section_found_in_chunks(s, chunks, act_hint=requested_act)]
        if still_missing:
            fallback_query = " ".join(f"Section {s}" for s in still_missing)
            if requested_act:
                fallback_query += f" {requested_act}"
            retry_chunks = retriever.retrieve(fallback_query, top_k=effective_top_k, act_hint=requested_act)
            seen = {(c["source"], c["text"]) for c in chunks}
            for c in retry_chunks:
                if (c["source"], c["text"]) not in seen:
                    chunks.append(c)

    if not chunks:
        return {"answer": no_context_fallback_reply(question), "sources": [], "disclaimer": DISCLAIMER}

    # 3. Act-Aware Post-Retrieval Filtering
    if query_type == "section_lookup" and requested_sections:
        found = [s for s in requested_sections if section_found_in_chunks(s, chunks, act_hint=requested_act)]
        if not found:
            return {"answer": section_not_found_reply(question, requested_sections, requested_act), "sources": [], "disclaimer": DISCLAIMER}

            if requested_act:
        # Updated regex to match bare numbers at the start of a line
                section_pattern_cache = {
                    s: re.compile(
                        rf"(?:section|sec\.?)\s*0*{re.escape(s)}\b"
                        rf"|^\s*0*{re.escape(s)}\s*[.\-]",
                        re.IGNORECASE | re.MULTILINE
            )
            for s in requested_sections
        }
            
            def _chunk_is_safe_to_keep(chunk: dict) -> bool:
                chunk_mentions_requested_section = any(pat.search(chunk["text"]) for pat in section_pattern_cache.values())
                if not chunk_mentions_requested_section:
                    return True
                return _act_matches_source(requested_act, chunk.get("source", ""))

            chunks = [c for c in chunks if _chunk_is_safe_to_keep(c)]
            if not chunks:
                return {"answer": section_not_found_reply(question, requested_sections, requested_act), "sources": [], "disclaimer": DISCLAIMER}

    # 4. Build prompt & generate answer
    prompt = build_prompt(question, chunks, requested_sections=requested_sections, asked_act=requested_act)

    # Inject last 5 turns of history into the messages for context
    MAX_HISTORY = 5
    recent_history = (history or [])[-MAX_HISTORY:]
    history_messages = [
        {"role": turn["role"], "content": turn["content"]}
        for turn in recent_history
        if turn.get("role") in ("user", "assistant") and turn.get("content")
    ]

    try:
        answer_response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                *history_messages,
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        answer = answer_response.choices[0].message.content.strip()
    except RateLimitError:
        raise GroqRateLimitError(RATE_LIMIT_MESSAGE)

    # 5. Script Purity Safety Net
    if contains_foreign_script(answer):
        print("⚠️ Foreign-script contamination detected — regenerating once.")
        retry_messages = [
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": answer},
            {"role": "user", "content": "Your previous response contained characters from a non-Urdu script. Rewrite the ENTIRE answer using ONLY correct script characters."}
        ]
        try:
            retry_response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=retry_messages,
                temperature=0.0,
                max_tokens=1024,
            )
            answer = retry_response.choices[0].message.content.strip()
        except RateLimitError:
            raise GroqRateLimitError(RATE_LIMIT_MESSAGE)

        if contains_foreign_script(answer):
            print("⚠️ Still contaminated after retry — stripping foreign characters.")
            answer = strip_foreign_script(answer)

    # 6. Collect sources and return
    sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))
    return {"answer": answer, "sources": sources, "disclaimer": DISCLAIMER}

# ─── CLI Test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  ⚖️  QanoonDaan — Scenario Test")
    print("=" * 60)
    test_questions = [
        "What is the punishment for theft in Pakistan?",
        "Pakistan me chor ki saza kia he?",
        "گھریلو تشدد کی سزا کیا ہے؟",
        "What are Sections 365, 368, and 369 of the Pakistan Penal Code?",
        "What is section 9999 of the PPC?",
        "Hi there!",
        "What is data science?",
        "How do I bribe a police officer to drop a case?",
    ]

    for q in test_questions:
        print(f"\n❓ Question: {q}\n")
        result = get_legal_answer(q)
        print(f"⚖️ Answer:\n{result['answer']}")
        print(f"\n{result['disclaimer']}")
        print("\n" + "=" * 60)