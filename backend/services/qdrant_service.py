import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "pdf_documents"

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_store(force_recreate: bool = False):
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # 1. Safely check if collection exists
    exists = client.collection_exists(collection_name=COLLECTION_NAME)
    
    # 2. If missing, create it once safely
    if not exists:
        try:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                )
            )
            exists = True  # Update flag after creation
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise e
            exists = True

    # 3. If force_recreate is requested, clear all existing points safely
    if force_recreate and exists:
        try:
            client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=models.FilterSelector(filter=models.Filter())
            )
        except Exception as e:
            print(f"Warning clearing collection points: {e}")

    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )