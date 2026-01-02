import os
import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Using BAAI/bge-m3 as requested
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"

_vectorstore_instance = None

def get_embeddings():
    # Helper to get embedding model. Using CPU for safety/compatibility.
    # Users can configure device if needed.
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def get_vectorstore(collection_name: str = "research_papers"):
    """
    Get or create ChromaDB vector store.
    """
    global _vectorstore_instance
    if _vectorstore_instance:
        return _vectorstore_instance # Verify collection name matches if we cache? For now simplified.
        
    embeddings = get_embeddings()
    # Persistent storage in ./chroma_db
    persist_directory = os.path.join(os.getcwd(), "chroma_db")
    
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    _vectorstore_instance = vectorstore
    return vectorstore

def retrieve_context(query: str, k: int = 5, filter_dict: dict = None):
    """
    Retrieve context from vector store.
    """
    vs = get_vectorstore()
    
    # Basic similarity search
    # If filter_dict is provided (e.g. {"section": "Results"}), pass to search
    if filter_dict:
        docs = vs.similarity_search(query, k=k, filter=filter_dict)
    else:
        docs = vs.similarity_search(query, k=k)
        
    return [{"content": d.page_content, "metadata": d.metadata} for d in docs]
