# ⚖️ QanoonDaan — Pakistani Legal Advisory Chatbot

> **Your AI-powered guide to Pakistani law** — Ask in English, Roman Urdu, or Urdu. Get accurate, law-referenced answers instantly.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-009688?style=flat-square&logo=fastapi)
![Groq](https://img.shields.io/badge/Groq-Llama3.3--70b-orange?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

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
- **Semantic search** via FAISS — finds the most relevant legal clauses for any question
- **Groq (Llama 3.3-70b)** — fast, accurate, open-source LLM for answer generation
- **Top-3 chunk retrieval** — pulls the 3 most relevant legal excerpts per query
- **Low temperature (0.2)** — keeps answers factual, not creative

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
- **XSS protection** — all user input is HTML-escaped before rendering
- **Input validation** — empty and overly long questions are rejected gracefully
- **No source exposure** — internal PDF filenames are never shown to users

### ⚡ Performance
- **FAISS IndexFlatIP** — cosine similarity search, sub-second retrieval
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
| **LLM** | Groq — Llama 3.3-70b-versatile | latest |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | 3.3.1 |
| **Vector Search** | FAISS (CPU) | 1.9.0 |
| **PDF Parsing** | PyPDF2 | 3.0.1 |
| **Templating** | Jinja2 | 3.1.4 |
| **Env Management** | python-dotenv | latest |
| **Voice Input** | Web Speech API (browser built-in) | — |
| **Fonts** | Playfair Display + DM Sans (Google Fonts) | — |

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
│   └── index.html                   # Chat UI (Jinja2 template)
│
├── static/
│   └── style.css                    # Dark/light theme styles
│
├── ingest.py                        # PDF → chunks → embeddings → FAISS
├── retriever.py                     # FAISS semantic search
├── chatbot.py                       # Translation + RAG + Groq LLM
├── main.py                          # FastAPI routes
├── config.py                        # All settings and constants
├── requirements.txt                 # Pinned dependencies
├── .env                             # Your API key (never commit)
├── .env.example                     # Template for .env
├── .gitignore                       # Protects secrets and generated files
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
        Groq translates to English:
        "What is the punishment for theft?"
                    │
                    ▼
        FAISS retrieves top 3 relevant
        legal chunks from the index
                    │
                    ▼
        Groq (Llama 3.3-70b) receives:
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
git clone https://github.com/yourusername/qanoondaan.git
cd qanoondaan
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
```bash
cp .env.example .env
```
Open `.env` and add your Groq API key:
```
GROQ_API_KEY=gsk_your_key_here
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
| `POST` | `/ask` | Accepts `question` (form field), returns JSON answer |
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
| FAISS Semantic Search | Strong NLP + vector search knowledge |
| Groq + Llama 3.3 | Modern open-source LLM integration |
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

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [Groq](https://groq.com) — blazing fast LLM inference
- [Meta LLaMA](https://llama.meta.com) — open-source LLM
- [FAISS by Meta AI](https://faiss.ai) — vector similarity search
- [sentence-transformers](https://www.sbert.net) — semantic embeddings
- [FastAPI](https://fastapi.tiangolo.com) — modern Python web framework
- [pakistancode.gov.pk](https://pakistancode.gov.pk) — official legal documents

---

*Built with ❤️ for Pakistani citizens — making law accessible to everyone.*
