# ⚖️ QanoonDaan — Pakistani Legal Advisory Chatbot

> **Your AI-powered guide to Pakistani law** — Ask in English, Roman Urdu, or Urdu. Get accurate, law-referenced answers instantly.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-009688?style=flat-square&logo=fastapi)
![Groq](https://img.shields.io/badge/Groq-GPT--OSS--120B-orange?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS%20%2B%20BM25-Hybrid%20Search-red?style=flat-square)
![License](https://img.shields.io/badge/License-Custom%20(Use%20Only)-lightgrey?style=flat-square)

---

## 📌 What is QanoonDaan?

**QanoonDaan** (قانون دان — meaning *one who knows the law*) is a domain-specialized AI chatbot that helps Pakistani citizens understand their legal rights and obligations in plain language.

Unlike generic AI assistants, QanoonDaan is grounded in **real Pakistani legal documents** — it never makes up laws or punishments. Every answer is retrieved from official legal texts and clearly references the relevant section or article.

### Example Questions It Can Answer

- *"What is the punishment for theft in Pakistan?"*
- *"What are my rights if I'm arrested without a warrant?"*
- *"How can a woman file for divorce in Pakistan?"*
- *"What does PECA 2016 say about cyberbullying?"*
- *"Can my employer fire me without notice?"*
- *"Pakistan me chor ki saza kia he?"* (Roman Urdu)
- *"گھریلو تشدد کی سزا کیا ہے؟"* (Urdu script)

---

## ✨ Features

### 🧠 AI & RAG Pipeline
- **Retrieval-Augmented Generation (RAG)** — answers are grounded in real legal documents, not LLM guesswork
- **Hybrid search** — FAISS semantic search (55%) blended with BM25 keyword search (45%), so both meaning and exact words count
- **Section-number boost** — asking for "Section 420 of the PPC" boosts chunks from the matching Act that contain that section
- **Smart query classifier** — one LLM call labels each question (legal question, section lookup, greeting, off-topic, harmful, unclear) and translates it to English
- **Groq (`openai/gpt-oss-120b`)** — fast open-weight LLM for answer generation
- **Adaptive retrieval** — pulls the top 5 chunks for general questions and the top 8 for section lookups
- **Chat memory** — the last 5 exchanges are sent along so follow-up questions make sense
- **Low temperature (0.2)** — keeps answers factual, not creative
- **LangSmith tracing and evals** — optional tracing of every pipeline step, plus a small regression test suite

### 🌐 Multilingual Support
- **English** — primary language, full support
- **Roman Urdu** — detects and responds in Roman Urdu automatically
- **Urdu Script (اردو)** — full Urdu script input and output supported
- **Auto language detection** — bot always replies in the same language as the question
- **Translation pipeline** — Urdu/Roman Urdu questions are translated to English before FAISS retrieval for accurate results, then answered back in the original language

### 🎙️ Voice Input
- **Built-in Web Speech API** — no extra libraries or APIs needed
- **English voice input** — click 🎙️ EN and speak
- **Urdu voice input** — right-click the mic button to switch to 🎙️ اردو
- **Auto-send** — question fires automatically after speech ends
- **Live listening indicator** — red pulsing animation while recording
- Works on **Chrome and Edge** browsers

### 🎨 Chat UI
- **Dark mode** (default) — deep charcoal + emerald green + gold
- **Light mode** — soft warm white + forest green
- **Theme toggle** — smooth animated pill toggle button (top right corner)
- **Remembers preference** — theme saved in localStorage, persists on refresh
- **4 sample questions** — clickable quick-start prompts on the welcome screen
- **Typing indicator** — animated bouncing dots while bot is thinking
- **Auto-resizing textarea** — input box grows as you type
- **Enter to send**, Shift+Enter for new line
- **Fully responsive** — works on desktop, tablet, and mobile
- **Playfair Display + DM Sans** fonts — professional, readable typography

### 🔒 Safety & Ethics
- **Legal disclaimer** — every answer includes: *"This is not professional legal advice"*
- **Honest refusals** — if the bot can't find relevant context, it says so clearly instead of hallucinating
- **Script purity check** — if the reply contains stray characters from the wrong script, it is regenerated once, then cleaned
- **Rate-limit handling** — a friendly "high traffic" message when the Groq limit is hit
- **XSS protection** — all user input is HTML-escaped before rendering
- **Input validation** — empty and overly long questions are rejected gracefully
- **No source exposure** — internal PDF filenames are never shown to users

### ⚡ Performance
- **FAISS IndexFlatIP + BM25** — cosine similarity plus keyword scoring, sub-second retrieval
- **Models loaded once at startup** — no reload delay per request
- **4,387 chunks indexed** from 8 legal PDFs
- **Uvicorn ASGI server** — async, production-grade

---

## 📚 Knowledge Base

QanoonDaan is trained on **8 official Pakistani legal documents**:

| File | Coverage |
|---|---|
| `constitution_1973.pdf` | Fundamental rights, state structure, due process |
| `pakistan_penal_code.pdf` | Criminal offences and punishments |
| `criminal_procedure_code.pdf` | Arrest, bail, trial procedures |
| `criminal_laws_amendment_2023.pdf` | Harassment, defamation updates |
| `family_laws.pdf` | Divorce, khula, custody, inheritance |
| `peca_2016.pdf` | Cybercrime, online harassment, digital offences |
| `peca_amendment_2025.pdf` | Latest cybercrime law updates |
| `labor_laws.pdf` | Employment rights, minimum wage, termination |

**Total:** ~4,387 semantic chunks indexed in FAISS

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|---|---|---|
| **Web Framework** | FastAPI | 0.115.5 |
| **Server** | Uvicorn | 0.32.0 |
| **LLM** | Groq — `openai/gpt-oss-120b` | groq 0.13.0 |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | 3.3.1 |
| **Vector Search** | FAISS (CPU) | 1.9.0 |
| **Keyword Search** | rank_bm25 (BM25Okapi) | latest |
| **Math** | NumPy | 1.26.4 |
| **PDF Parsing** | PyPDF2 | 3.0.1 |
| **Form Handling** | python-multipart | 0.0.12 |
| **Templating** | Jinja2 | 3.1.4 |
| **Env Management** | python-dotenv | 1.0.0 |
| **Observability and Evals** | LangSmith | latest |
| **Container** | Docker (python:3.10-slim) | — |
| **Hosting** | Hugging Face Spaces (port 7860) | — |
| **Voice Input** | Web Speech API (browser built-in) | — |
| **Fonts** | Playfair Display, DM Sans, DM Mono (Google Fonts) | — |

---

## 🗂️ Project Structure

```
qanoondaan/
│
├── knowledge_base/                  # Legal PDF documents
│   ├── constitution_1973.pdf
│   ├── pakistan_penal_code.pdf
│   ├── criminal_procedure_code.pdf
│   ├── criminal_laws_amendment_2023.pdf
│   ├── family_laws.pdf
│   ├── peca_2016.pdf
│   ├── peca_amendment_2025.pdf
│   └── labor_laws.pdf
│
├── vector_store/                    # Generated by ingest.py
│   ├── faiss_index.bin              # FAISS vector index
│   └── chunks.pkl                   # Original text chunks
│
├── templates/
│   ├── index.html                   # Chat UI (Jinja2 template)
│   └── about.html                   # About page
│
├── static/
│   ├── style.css                    # Dark/light theme styles
│   ├── hasnain.jpg                  # Developer photo (About page)
│   └── shariahease-icon.png         # Project icon (About page)
│
├── evals/
│   └── run_evals.py                 # LangSmith regression tests
│
├── ingest.py                        # PDF → chunks → embeddings → FAISS
├── retriever.py                     # Hybrid search (FAISS + BM25 + section boost)
├── chatbot.py                       # Classifier + translation + RAG + Groq LLM
├── main.py                          # FastAPI routes
├── app.py                           # Entry point for Hugging Face Spaces
├── config.py                        # All settings and constants
├── debug_db.py                      # Checks which PDFs are in the index
├── Dockerfile                       # Container build for Hugging Face Spaces
├── requirements.txt                 # Dependencies
├── .env                             # Your API keys (never commit)
├── .gitignore                       # Protects secrets and generated files
├── .gitattributes                   # Git LFS rules for PDFs and index files
└── README.md                        # This file
```

---

## ⚙️ How It Works

```
                    ┌─────────────────────────┐
                    │   8 Pakistani Legal PDFs │
                    └────────────┬────────────┘
                                 │ ingest.py (run once)
                                 ▼
                    ┌─────────────────────────┐
                    │  Split into 500-char     │
                    │  overlapping chunks      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  all-MiniLM-L6-v2        │
                    │  converts to vectors     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  FAISS index saved to    │
                    │  vector_store/           │
                    └─────────────────────────┘

════════════════════════════════════════════════
  USER QUERY FLOW (at runtime)
════════════════════════════════════════════════

  User: "Pakistan me chor ki saza kia he?"
                    │
                    ▼
        Groq classifies the question and
        translates it to English:
        "What is the punishment for theft?"
                    │
                    ▼
        Hybrid search (FAISS + BM25) retrieves
        the top relevant legal chunks
                    │
                    ▼
        Groq (gpt-oss-120b) receives:
        ┌──────────────────────────────────┐
        │ Context: [PPC Section 379]       │
        │          [CrPC Section 54]       │
        │ Question: (original Roman Urdu)  │
        └──────────────────────────────────┘
                    │
                    ▼
        Bot replies in Roman Urdu
        with law references + disclaimer ✅
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- A free Groq API key from [console.groq.com](https://console.groq.com)
- Microsoft Visual C++ Redistributable (Windows only) — [download here](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Chrome or Edge (for voice input)

### 1. Clone the Repository
```bash
git clone https://github.com/SyedHusnain20/QanoonDaan.git
cd QanoonDaan
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a file named `.env` in the project root and add your Groq API key:
```
GROQ_API_KEY=gsk_your_key_here
```

Optional — to turn on LangSmith tracing, also add:
```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key_here
```

### 5. Add Legal PDFs
Place all 8 PDF files inside the `knowledge_base/` folder.

### 6. Build the Knowledge Base (Run Once)
```bash
python ingest.py
```
This will:
- Extract text from all PDFs
- Split into chunks
- Generate embeddings
- Save FAISS index to `vector_store/`

Expected output:
```
✅ Total chunks ready: 4387
💾 FAISS index saved → vector_store/faiss_index.bin
💾 Chunks saved      → vector_store/chunks.pkl
🎉 Ingestion complete!
```

### 7. Start the Server
```bash
uvicorn main:app --reload
```

### 8. Open in Browser
```
http://localhost:8000
```

---

## 🧪 Testing

Run the terminal pipeline test:
```bash
python chatbot.py
```

Test the retriever directly:
```bash
python retriever.py
```

Check which PDFs are in the index:
```bash
python debug_db.py
```

Run the LangSmith regression tests (needs `GROQ_API_KEY` and `LANGSMITH_API_KEY`):
```bash
python -m evals.run_evals
```

Check the API health:
```
GET http://localhost:8000/health
```

Test the API via Swagger UI:
```
http://localhost:8000/docs
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the chat UI |
| `GET` | `/about` | Serves the About page |
| `POST` | `/ask` | Accepts `question` and optional `history` (JSON string of recent turns) as form fields, returns JSON answer |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI for API testing |

### Example API Call
```bash
curl -X POST http://localhost:8000/ask \
  -F "question=What is the punishment for theft in Pakistan?"
```

### Response Format
```json
{
  "answer": "Under Section 379 of the Pakistan Penal Code...",
  "sources": ["pakistan_penal_code.pdf"],
  "disclaimer": "⚠️ This response is for informational purposes only..."
}
```

---

## 💼 Why This Project Stands Out

| What Was Built | What It Demonstrates |
|---|---|
| RAG Pipeline | Production-level AI architecture |
| Pakistani Law Domain | Real, local, unsolved problem |
| Hybrid Search (FAISS + BM25) | Strong NLP + vector and keyword search knowledge |
| Groq + gpt-oss-120b | Modern open-weight LLM integration |
| LangSmith Tracing + Evals | Production habits: observability and regression testing |
| Multilingual (EN/UR/Roman UR) | Localization + translation pipeline |
| Voice Input (Web Speech API) | Accessibility + UX thinking |
| Dark/Light Theme | Frontend polish |
| Legal Disclaimer | AI ethics and responsibility |
| FastAPI + Uvicorn | Clean backend architecture |
| Deployed on HF Spaces | Ships real products |

---

## ⚠️ Disclaimer

QanoonDaan is an **informational tool only**. It does not constitute professional legal advice. Always consult a qualified lawyer for your specific legal situation. For official legal texts, visit [pakistancode.gov.pk](https://pakistancode.gov.pk).

---

## 📄 License

This project is free to use. Modification and redistribution are not permitted without the author's consent.

---

## 🙏 Acknowledgements

- [Groq](https://groq.com) — blazing fast LLM inference
- OpenAI gpt-oss — open-weight LLM
- [FAISS by Meta AI](https://faiss.ai) — vector similarity search
- [LangSmith](https://smith.langchain.com) — tracing and evaluation
- [sentence-transformers](https://www.sbert.net) — semantic embeddings
- [FastAPI](https://fastapi.tiangolo.com) — modern Python web framework
- [pakistancode.gov.pk](https://pakistancode.gov.pk) — official legal documents

---

*Built with ❤️ for Pakistani citizens — making law accessible to everyone.*

---

## 👤 Author

**Engr. Hasnain Zainulabdin**
R&R Digital Solutions

Contact: 03126641281 | [HasnainZainulabdin@gmail.com](mailto:HasnainZainulabdin@gmail.com)
Website: https://hasnainzainulabdin.vercel.app/
