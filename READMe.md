# 1. Start Redis & Qdrant
docker compose up -d

# 2. Start Uvicorn API
uvicorn backend.main:app --reload

# 3. Start Celery Worker
celery -A worker.worker.celery_app worker --loglevel=info -P threads

# 4. Start Streamlit UI
streamlit run frontend/app.py