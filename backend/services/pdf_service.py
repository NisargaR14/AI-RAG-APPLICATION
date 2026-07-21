from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_and_chunk_pdf(pdf_path: str):
    """
    1. Loads text from a PDF file.
    2. Splits it into overlapping chunks to preserve semantic context.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    # 1000 characters per chunk with 200 character overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200 
        # Shifts each chunk window back by 200 characters. 
        # This ensures that sentences split at chunk boundaries don't lose key context.
    )
    chunks = text_splitter.split_documents(documents)
    return chunks