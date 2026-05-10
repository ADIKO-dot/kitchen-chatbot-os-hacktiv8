# 🍳 KitchenOS-AI

**AI-Powered Kitchen Operations Assistant** — Chatbot berbasis LLM untuk manajemen operasional dapur dan restoran.

> Final Project: LLM-Based Tools and Gemini API Integration for Data Scientists (Hacktiv8)

---

## 📋 Deskripsi

KitchenOS-AI adalah chatbot cerdas yang membantu operasional dapur/restoran menggunakan dengan **RAG (Retrieval-Augmented Generation)**. Sistem ini secara otomatis mendeteksi intent pengguna dan merutekan ke agent spesialis yang tepat.

### Use Case
- Asisten operasional dapur (resep, SOP, food safety)
- Kalkulasi keuangan (food cost, pricing, revenue)
- Rekomendasi menu berbasis data
- OCR/Vision untuk scan receipt dan inventory
- Pembuatan dokumen (PDF, Excel)
- Web search untuk informasi terkini

---

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                          │
│         Next.js Web UI  │  Telegram Bot             │
└──────────────────────┬──────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────┐
│                  FastAPI Backend                     │
├─────────────────────────────────────────────────────┤
│  Orchestrator (LLM-based Intent Classification)     │
├─────────────────────────────────────────────────────┤
│  Agents:                                            │
│  ├── 🍳 Kitchen Ops (OCR/Vision)                    │
│  ├── 💰 Finance (Costing, Waste, Revenue)           │
│  ├── 📚 RAG Agent (Knowledge Retrieval)             │
│  ├── 💡 Recommendation (Menu Suggestions)           │
│  ├── 📄 File Gen (PDF, Excel, Images)              │
│  ├── 🔍 Web Search (DuckDuckGo)                    │
│  ├── 💼 Career Ops (CV Tailoring)                   │
│  └── 🤖 General (Catch-all)                        │
├─────────────────────────────────────────────────────┤
│  Services:                                          │
│  ├── Memory Store (Session-based History)           │
│  ├── RAG / ChromaDB (Vector Knowledge Base)         │
│  ├── LLM Factory (Gemini + Groq + Ollama)          │
│  └── Waste Tracker, Finance, Vision, etc.           │
└─────────────────────────────────────────────────────┘
```

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| **Multi-Agent Routing** | LLM mengklasifikasi intent → route ke agent spesialis |
| **RAG System** | Knowledge base dengan ChromaDB untuk resep, SOP, food safety |
| **Conversation Memory** | Session-based history untuk konteks percakapan berkelanjutan |
| **Tone Configuration** | Pilih gaya bahasa: Formal, Casual, atau Friendly |
| **Menu Recommendation** | Rekomendasi cerdas berdasarkan resep + data waste |
| **Multi-Provider LLM** | Gemini → Groq → Ollama (auto-fallback + key rotation) |
| **OCR/Vision** | Scan receipt, inventory list, menu via OpenCV + Tesseract |
| **File Generation** | Generate PDF invoice, Excel inventory, menu images |
| **Web Search** | Real-time search via DuckDuckGo |
| **Multi-Platform** | Web UI (Next.js) + Telegram Bot |

---

## 🛠️ Parameter Kreatif

1. **Gaya Bahasa (Tone)** — User bisa memilih formal/casual/friendly
2. **Domain Knowledge** — Spesifik untuk kitchen/restaurant operations
3. **RAG + Memory** — Retrieval-Augmented Generation + conversation history
4. **Multi-Provider Fallback** — Gemini API → Groq → Ollama (auto-rotation)
5. **Rekomendasi Berbasis Data** — Menu suggestions dari waste data + knowledge base
6. **Integrasi API Eksternal** — Gemini API, Groq API, DuckDuckGo, Telegram Bot API

---

## 🚀 Setup & Instalasi

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) Ollama untuk local LLM fallback

### 1. Clone & Setup Backend

```bash
git clone https://github.com/YOUR_USERNAME/kitchenos-ai.git
cd kitchenos-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi Environment

```bash
cp .env.example .env
# Edit .env dan masukkan API keys:
# - GEMINI_API_KEYS (wajib)
# - GROQ_API_KEYS (opsional)
# - TELEGRAM_BOT_TOKEN (opsional, untuk Telegram bot)
```

### 3. Seed Knowledge Base (RAG)

```bash
python seed_knowledge.py
```

### 4. Jalankan Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Setup & Jalankan Frontend

```bash
cd web
npm install
npm run dev
```

Frontend akan berjalan di `http://localhost:3000`

### 6. (Optional) Jalankan Telegram Bot

```bash
python telegram_bot.py
```

---

## 📡 API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/chat` | Main chat (text, dengan session & tone) |
| POST | `/chat/image` | Chat dengan upload gambar |
| GET | `/history/{session_id}` | Ambil conversation history |
| DELETE | `/history/{session_id}` | Hapus conversation history |
| POST | `/rag/add` | Tambah dokumen ke knowledge base |
| POST | `/rag/batch` | Tambah batch dokumen |
| GET | `/rag/documents` | List semua dokumen di knowledge base |
| DELETE | `/rag/{doc_id}` | Hapus dokumen dari knowledge base |
| GET | `/health` | Health check |

### Contoh Request

```bash
# Chat biasa
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Berikan resep nasi goreng", "tone": "casual"}'

# Chat dengan session (memory)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Lanjutkan resep tadi", "session_id": "abc-123", "tone": "friendly"}'

# Tambah knowledge ke RAG
curl -X POST http://localhost:8000/rag/add \
  -H "Content-Type: application/json" \
  -d '{"id": "recipe-rendang", "text": "Resep Rendang: ...", "metadata": {"source": "recipe"}}'
```

---

## 🧠 Cara Kerja RAG

```
User: "Bagaimana SOP penyimpanan daging?"
         │
         ▼
┌─────────────────────┐
│  1. Orchestrator     │ → Klasifikasi intent → "rag"
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  2. RAG Agent        │
│  - Search ChromaDB   │ → Cari dokumen relevan (cosine similarity)
│  - Retrieve top 3    │ → Ambil SOP food safety, SOP inventory
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  3. LLM Generation   │ → Kirim retrieved docs + question ke Gemini
│  - Context: docs     │ → Generate jawaban berdasarkan knowledge base
│  - History: memory   │
└─────────┬───────────┘
          ▼
     Response + Sources
```

**Keuntungan RAG:**
- Jawaban akurat berdasarkan data yang sudah diverifikasi
- Bisa di-update tanpa retrain model
- Mengurangi hallucination
- Bisa cite sumber

---

## 📁 Struktur Project

```
kitchenos-ai/
├── main.py                 # FastAPI entry point
├── agents/
│   ├── orchestrator.py     # Intent classifier & router
│   ├── general_agent.py    # General conversation
│   ├── rag_agent.py        # RAG-based Q&A
│   ├── recommendation_agent.py  # Menu recommendations
│   ├── kitchen_ops.py      # OCR/Vision
│   ├── finance_agent.py    # Financial calculations
│   ├── file_gen_agent.py   # PDF/Excel generation
│   ├── web_search_agent.py # Web search
│   └── career_ops_agent.py # CV tailoring
├── services/
│   ├── memory.py           # Conversation history store
│   ├── rag.py              # ChromaDB vector store
│   ├── finance.py          # Food cost calculations
│   ├── waste.py            # Waste tracking
│   ├── vision.py           # OCR with OpenCV
│   ├── web_search.py       # DuckDuckGo search
│   └── ...                 # Other services
├── utils/
│   ├── llm_factory.py      # Multi-provider LLM (Gemini/Groq/Ollama)
│   ├── config.py           # Environment config
│   └── api_key_manager.py  # Key rotation
├── web/                    # Next.js frontend
│   ├── app/
│   ├── components/Chat.tsx
│   └── lib/api.ts
├── telegram_bot.py         # Telegram interface
├── seed_knowledge.py       # RAG knowledge seeder
├── requirements.txt
└── .env.example
```

---

## 🖥️ Screenshots

> Screenshots akan ditambahkan setelah deployment.

### Web UI
- Chat interface dengan tone selector
- Quick-start buttons untuk fitur populer
- Session-based conversation dengan memory

### Telegram Bot
- Text chat dengan auto-routing
- Image upload untuk OCR

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Google Gemini 2.0 Flash, Groq (Llama 3.3 70B), Ollama |
| Backend | FastAPI, Python 3.11+ |
| Frontend | Next.js 14, React, TailwindCSS |
| Vector DB | ChromaDB (RAG) |
| OCR | OpenCV + Tesseract |
| Search | DuckDuckGo Search API |
| Bot | python-telegram-bot |
| File Gen | ReportLab (PDF), OpenPyXL (Excel) |

---

## 👤 Author

**I PUTU ADIBAWA** — Hacktiv8 Data Science Program

---

## 📄 License

MIT License
