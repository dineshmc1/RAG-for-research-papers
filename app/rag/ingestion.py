import os
from typing import List, Dict, Any
from pypdf import PdfReader
import re

def clean_text(text: str) -> str:
    """Basic text cleaning."""
    return re.sub(r'\s+', ' ', text).strip()

def parse_pdf_sections(file_path: str) -> List[Dict[str, Any]]:
    """
    Parses a PDF into section-aware chunks.
    This is a heuristic implementation. In production, use Marker or PyMuPDF/fitz for better layout analysis.
    """
    reader = PdfReader(file_path)
    chunks = []
    
    current_section = "Introduction" # Default start
    
    # Simple regex for common section headers
    header_pattern = re.compile(r'^(Introduction|Abstract|Methods?|Related Work|Results?|Discussion|Conclusion|References)', re.IGNORECASE)
    
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        lines = text.split('\n')
        
        page_text_acc = ""
        
        for line in lines:
            clean_line = line.strip()
            # Heuristic check for section header
            if len(clean_line) < 50 and header_pattern.match(clean_line):
                # If we have accumulated text, save it as a chunk for the previous section
                if page_text_acc:
                    chunks.append({
                        "text": clean_text(page_text_acc),
                        "metadata": {
                            "source": os.path.basename(file_path),
                            "page": page_num + 1,
                            "section": current_section
                        }
                    })
                    page_text_acc = ""
                current_section = clean_line
            else:
                page_text_acc += line + " "

        # Add remaining text from page
        if page_text_acc:
             chunks.append({
                "text": clean_text(page_text_acc),
                "metadata": {
                    "source": os.path.basename(file_path),
                    "page": page_num + 1,
                    "section": current_section
                }
            })
            
    return chunks

def ingest_pdf(file_path: str, collection_name: str = "research_papers"):
    """
    Ingest PDF into Vector Store (ChromaDB).
    This function will be called by the UI or Agent.
    """
    # Circular import prevention
    from app.rag.retrieval import get_vectorstore
    
    chunks = parse_pdf_sections(file_path)
    if not chunks:
        return False, "No text extracted from PDF."
        
    vs = get_vectorstore(collection_name)
    
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
    
    vs.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    return True, f"Ingested {len(chunks)} chunks."
