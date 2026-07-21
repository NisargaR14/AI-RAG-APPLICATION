# Enterprise Document Intelligence Core ⚡

An asynchronous, high-performance Retrieval-Augmented Generation (RAG) platform designed for single-document precision search and contextual synthesis. Built with a decoupled microservice architecture using **FastAPI**, **Celery**, **Redis**, **Qdrant**, and **Groq (Llama 3.3)**.

---

## 🏢 Architecture & Data Flow

```text
+------------------+         +-----------------+         +-------------------+
|                  |  Upload |                 |  Task   |                   |
| Streamlit UI     | ------> | FastAPI Backend | ------> | Redis Task Queue  |
| (Frontend Port   |         | (API Port 8000) |         | (Port 6379)       |
|  8501)           |         +-----------------+         +-------------------+
+------------------+                  |                            |
         ^                            | Query                      v
         |                            v                  +-------------------+
         |                   +-----------------+         |                   |
         |                   | Qdrant Vector   |         | Celery Worker     |
         +------------------ | Database        | <------ | (PDF Chunking &   |
           Context Synthesis | (Port 6333)     |  Index  |  Embedding)       |
             via Groq LLM    +-----------------+         +-------------------+


1. Document Ingestion: PDFs are uploaded via the Streamlit frontend to FastAPI and passed to a Redis-backed Celery queue for non-blocking asynchronous processing.

2. Text Chunking & Embedding: The Celery worker parses the document, splits text into overlapping chunks, and generates vector embeddings using HuggingFace's all-MiniLM-L6-v2 model.

3.Document-Isolated Vector Storage: Vectors are stored in Qdrant using an isolated collection architecture (force_recreate=True) to eliminate cross-document context pollution.

4.Context Retrieval & Synthesis: Relevant chunks ($k=8$) are retrieved using cosine similarity search and synthesized into precise answers by Llama 3.3 (via Groq) with verified context citations.

📁 Repository Folder Structure

AI-RAG/
├── backend/
│   ├── queue/
│   │   └── producer.py         # Celery task producer definition
│   ├── services/
│   │   ├── llm_service.py      # Groq Llama 3.3 integration & context synthesis
│   │   ├── pdf_service.py      # PDF parsing utilities
│   │   └── qdrant_service.py   # Vector collection setup & similarity retriever
│   ├── config.py               # Environment configuration loader
│   └── main.py                 # FastAPI REST API (/upload and /query)
│
├── frontend/
│   └── app.py                  # Streamlit UI (custom dark theme, recent chats, citations)
│
├── worker/
│   └── worker.py               # Celery worker process for background vector indexing
│
├── temp_uploads/               # Temporary storage directory for uploaded PDFs (git-ignored)
├── .env.example                # Configuration template for environment variables
├── .gitignore                  # Git exclusion rules
├── chat_history.json           # Persistent local chat session storage (git-ignored)
├── docker-compose.yml          # Container setup for Redis & Qdrant services
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation

⚡ Tech Stack
Frontend: Streamlit, Custom CSS Styling

Backend Framework: FastAPI, Uvicorn, Pydantic

Asynchronous Processing: Celery, Redis

Vector Database: Qdrant Vector Search

Embeddings & LLM: HuggingFace all-MiniLM-L6-v2, Groq Cloud (llama-3.3-70b-versatile)

Framework Orchestration: LangChain

Infrastructure Containerization: Docker, Docker Compose

🚀 Local Setup & Installation
Prerequisites
Python 3.10+

Docker Desktop (for Redis & Qdrant)

Step 1: Clone the Repository
Bash
git clone [https://github.com/your-username/AI-RAG.git](https://github.com/your-username/AI-RAG.git)
cd AI-RAG

Step 2: Set Up Virtual Environment & Dependencies
Bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt

Step 3: Configure Environment Variables
Copy .env.example to .env and fill in your credentials:

Code snippet
GROQ_API_KEY=your_groq_key_here
QDRANT_HOST=localhost
QDRANT_PORT=6333
REDIS_HOST=localhost
REDIS_PORT=6379

🛠️ Running the Application
Open 4 separate terminal tabs in your project root directory:

1. Start Infrastructure (Redis & Qdrant)
Bash
docker compose up -d

2. Start FastAPI Backend API
Bash
uvicorn backend.main:app --reload

3. Start Celery Background Worker
Bash
celery -A worker.worker.celery_app worker --loglevel=info -P threads

4. Start Streamlit Frontend
Bash
streamlit run frontend/app.py
Access the Web Application at: http://localhost:8501
Access FastAPI Swagger Docs at: http://localhost:8000/docs

🌟 Key Features & Highlights

1. Isolated Document Vectorization: Guarantees high retrieval precision by clearing old vector collections upon indexing new documents, preventing cross-file semantic noise.

2. Asynchronous Indexing: Decouples PDF ingestion from the main HTTP thread using Celery workers for zero UI latency.

3. Persistent Session History: Local storage (chat_history.json) enables switching between active/past sessions and deleting individual chat threads.

4. Verified Context Citations: Exposes exact retrieved vector chunks inside expandable UI elements for output transparency and verification.