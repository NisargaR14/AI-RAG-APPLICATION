import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def generate_answer(query: str, vector_store):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment variables or .env file.")

    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=0.0,
        max_tokens=1024,
        groq_api_key=api_key
    )
    
    # Retrieve top 8 overlapping chunks
    retriever = vector_store.as_retriever(search_kwargs={"k": 8})
    relevant_docs = retriever.invoke(query)
    
    if not relevant_docs:
        return {
            "answer": "No relevant documents found. Please ensure a document has been uploaded and indexed.",
            "sources": []
        }

    # Deduplicate retrieved document chunks while preserving order
    unique_docs = []
    seen_texts = set()
    for doc in relevant_docs:
        cleaned_text = doc.page_content.strip()
        if cleaned_text not in seen_texts:
            seen_texts.add(cleaned_text)
            unique_docs.append(doc)
    
    context = "\n\n---\n\n".join([doc.page_content for doc in unique_docs])
    
    # Fully generic prompt template for ANY document
    prompt_template = ChatPromptTemplate.from_template(
        "You are an enterprise document intelligence assistant. "
        "Answer the question thoroughly and accurately using ONLY the provided context below.\n\n"
        "Guidelines:\n"
        "1. Base your answer strictly on the facts present in the context.\n"
        "2. When answering questions about lists, counts, or structured details, inspect all retrieved context chunks completely.\n"
        "3. If the context does not contain sufficient information to answer the question, state clearly that the context does not provide this information.\n\n"
        "Context:\n{context}\n\n"
        "Question:\n{query}\n\n"
        "Answer:"
    )
    
    chain = prompt_template | llm
    response = chain.invoke({"context": context, "query": query})
    
    return {
        "answer": response.content,
        "sources": [
            f"(Page {doc.metadata.get('page', 'N/A')}): {doc.page_content[:150].replace('\n', ' ').strip()}..."
            for doc in unique_docs
        ]
    }