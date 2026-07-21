import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load variables from .env file
load_dotenv()

def generate_answer(query: str, vector_store):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment variables or .env file.")

    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile", 
        temperature=0.2,
        groq_api_key=api_key
    )
    
    # Retrieve top 8 chunks for full context coverage
    retriever = vector_store.as_retriever(search_kwargs={"k": 8})
    relevant_docs = retriever.invoke(query)
    
    # Deduplicate retrieved document chunks
    unique_docs = []
    seen_texts = set()
    for doc in relevant_docs:
        cleaned_text = doc.page_content.strip()
        if cleaned_text not in seen_texts:
            seen_texts.add(cleaned_text)
            unique_docs.append(doc)
    
    context = "\n\n".join([doc.page_content for doc in unique_docs])
    
    prompt_template = ChatPromptTemplate.from_template(
        "You are an enterprise AI assistant. Answer the user's question accurately using ONLY the context provided below:\n\n"
        "Context:\n{context}\n\n"
        "Question: {query}\n\n"
        "Answer:"
    )
    
    chain = prompt_template | llm
    response = chain.invoke({"context": context, "query": query})
    
    return {
        "answer": response.content,
        "sources": [doc.page_content[:200].replace("\n", " ").strip() + "..." for doc in unique_docs]
    }