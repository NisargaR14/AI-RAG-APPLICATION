import os
from celery import Celery
from backend.services.pdf_service import extract_text_from_pdf
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
        # Extract and chunk ANY document generically
        documents = extract_text_from_pdf(file_path)
        
        # Store vectors in Qdrant
        vector_store = get_vector_store(force_recreate=True)
        vector_store.add_documents(documents)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return {"status": "success", "chunks_processed": len(documents)}
    except Exception as e:
        return {"status": "failed", "error": str(e)}