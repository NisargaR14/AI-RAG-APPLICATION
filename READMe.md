# Enterprise Document Intelligence Core ⚡

An asynchronous, high-performance **Retrieval-Augmented Generation (RAG)** platform designed for **single-document precision search** and contextual synthesis.

Built with a decoupled microservice architecture using **FastAPI, Celery, Redis, Qdrant, HuggingFace Embeddings, LangChain, and Groq (Llama 3.3).**

---

# 🏗️ Architecture & Data Flow

```text
+------------------+         +-----------------+         +-------------------+
|                  | Upload  |                 |  Task   |                   |
|  Streamlit UI    | ------> | FastAPI Backend | ------> | Redis Task Queue  |
| (Frontend:8501)  |         | (API:8000)      |         | (Port:6379)       |
+------------------+         +-----------------+         +-------------------+
         ^                            |                            |
         |                            | Query                      |
         |                            v                            v
         |                   +-----------------+         +-------------------+
         |                   | Qdrant Vector   | <------ | Celery Worker     |
         +------------------ | Database        |  Index  | PDF Processing &  |
           Context Synthesis | (Port:6333)     |         | Embedding         |
             via Groq LLM    +-----------------+         +-------------------+
```

---

# 📌 System Workflow

1. **Document Ingestion**: PDFs are uploaded via the Streamlit frontend to FastAPI and passed to a Redis-backed Celery queue for non-blocking asynchronous processing.

2. **Text Chunking & Embedding**: The Celery worker parses the document, splits text into overlapping chunks, and generates vector embeddings using HuggingFace's all-MiniLM-L6-v2 model.

3. **Document-Isolated Vector Storage**: Vectors are stored in Qdrant using an isolated collection architecture (force_recreate=True) to eliminate cross-document context pollution.

4. **Context Retrieval & Synthesis**: Relevant chunks (k = 8) are retrieved using cosine similarity search and synthesized into precise answers by Llama 3.3 (via Groq) with verified context citations.

---

# ⚡ Tech Stack

**Frontend**: Streamlit, Custom CSS Styling
**Backend Framework**: FastAPI, Uvicorn, Pydantic
**Asynchronous Processing**: Celery, Redis
**Vector Database**: Qdrant Vector Search
**Embeddings & LLM**: HuggingFace all-MiniLM-L6-v2, Groq Cloud (llama-3.3-70b-versatile)
**Framework Orchestration**: LangChain
**Infrastructure Containerization**: Docker, Docker Compose

---

# 📂 Repository Structure

```text
AI-RAG/
│
├── backend/
│   ├── queue/
│   │   └── producer.py
│   │
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── pdf_service.py
│   │   └── qdrant_service.py
│   │
│   ├── config.py
│   └── main.py
│
├── frontend/
│   └── app.py
│
├── worker/
│   └── worker.py
│
├── temp_uploads/
├── .env.example
├── .gitignore
├── chat_history.json
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🚀 Local Setup & Installation

## Prerequisites

- Python 3.10+
- Docker Desktop (for Redis & Qdrant)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/NisargaR14/AI-RAG-APPLICATION.git
cd AI-RAG-APPLICATION
```
---

## Step 2: Set Up Virtual Environment & Dependencies

```bash
python -m venv .venv
```

### Windows
```bash
.venv\Scripts\activate
```

### Linux/macOS
```bash
source .venv/bin/activate
```

Install dependencies
```bash
pip install -r requirements.txt
```

---

## 3️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
QDRANT_HOST=localhost
QDRANT_PORT=6333
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

# 🛠️ Running the Application

Open 4 separate terminal tabs in your project root directory:

## 1. Start Infrastructure (Redis & Qdrant Containers)

```bash
docker compose up -d
```

## Start FastAPI Backend API

```bash
uvicorn backend.main:app --reload
```

## 3. Start Celery Background Worker

```bash
celery -A worker.worker.celery_app worker --loglevel=info -P threads
```

## 4. Start Streamlit Frontend UI

```bash
streamlit run frontend/app.py
```

**Web Application UI**: http://localhost:8501

**FastAPI Swagger Docs**: http://localhost:8000/docs



# 🌟 Key Features & Highlights

1. **Isolated Document Vectorization**: Guarantees high retrieval precision by clearing old vector collections upon indexing new documents, preventing cross-file semantic noise.

2. **Asynchronous Indexing**: Decouples PDF ingestion from the main HTTP thread using Celery workers for zero UI latency.

3. **Persistent Session History**: Local storage (chat_history.json) enables switching between active/past sessions and deleting individual chat threads.

4. **Verified Context Citations**: Exposes exact retrieved vector chunks inside expandable UI elements for output transparency and verification.