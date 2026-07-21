import os
from celery import Celery
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.services.qdrant_service import get_vector_store

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

celery_app = Celery(
    "rag_tasks",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)

@celery_app.task(name="process_pdf_task")
def process_pdf_task(file_path: str):
    try:
        # Load PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        
        # Force recreate collection to delete old PDF data on new upload
        vector_store = get_vector_store(force_recreate=True)
        vector_store.add_documents(chunks)
        
        # Cleanup temporary uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return {"status": "success", "chunks_processed": len(chunks)}
    except Exception as e:
        return {"status": "failed", "error": str(e)}