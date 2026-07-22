import fitz  # PyMuPDF
import pdfplumber
from langchain_core.documents import Document

def extract_text_from_pdf(file_path: str):
    """
    Extracts text from both native PDFs and image/scanned PDFs.
    """
    documents = []
    
    # Try standard PyMuPDF first for speed
    doc = fitz.open(file_path)
    total_pages = len(doc)
    
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text()
        
        # If the page has text, store it
        if text.strip():
            documents.append(Document(page_content=text, metadata={"page": page_num + 1}))
            
    # Fallback if the PDF consists mostly of images/mindmaps
    if not documents or len(documents) < (total_pages / 2):
        print("Scanned/Image PDF detected. Running enhanced extraction...")
        documents = []
        with pdfplumber.open(file_path) as pdf:
            for idx, page in enumerate(pdf.pages):
                text = page.extract_text(layout=True) or ""
                if text.strip():
                    documents.append(Document(page_content=text, metadata={"page": idx + 1}))

    return documents