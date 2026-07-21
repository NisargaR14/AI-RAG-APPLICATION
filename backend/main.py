from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os

from backend.services.qdrant_service import get_vector_store
from backend.services.llm_service import generate_answer
from worker.worker import celery_app

app = FastAPI()

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs("temp_uploads", exist_ok=True)
    file_path = f"temp_uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    task = celery_app.send_task("process_pdf_task", args=[file_path])
    return {"status": "processing", "task_id": task.id}

@app.post("/query")
async def query_pdf(question: str):
    try:
        vector_store = get_vector_store()
        result = generate_answer(question, vector_store)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))