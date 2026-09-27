from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from services import rag_service

router = APIRouter()


@router.post("/upload/knowledge")
async def upload_knowledge(file: UploadFile = File(...)):
    """Permet de charger une nouvelle base de connaissances Markdown (.md) et d'actualiser le RAG."""
    if not file.filename.endswith((".md", ".txt")):
        raise HTTPException(status_code=400, detail="Veuillez fournir un fichier Markdown (.md) ou texte (.txt)")

    content = await file.read()
    text_content = content.decode("utf-8")

    # Mettre à jour le fichier knowledge.md
    with open(rag_service.KNOWLEDGE_MD_PATH, "w", encoding="utf-8") as f:
        f.write(text_content)

    # Ré-indexer la base RAG (Chunks + ChromaDB)
    chunks = rag_service.parse_markdown_to_chunks()
    rag_service.rag_engine = rag_service.RAGSearchEngine()

    return {
        "status": "success",
        "message": "Base de connaissances RAG mise à jour avec succès !",
        "filename": file.filename,
        "total_chunks": len(chunks),
        "total_words": sum(c.get("word_count", 0) for c in chunks),
    }


@router.get("/rag/status")
def get_rag_status():
    """Renvoie le statut et les métriques de la base RAG."""
    chunks = rag_service.rag_engine.chunks
    return {
        "status": "active",
        "vector_db": "ChromaDB" if rag_service.rag_engine.chroma_collection else "Python Vector Engine",
        "total_documents": len(chunks),
        "total_words": sum(c.get("word_count", 0) for c in chunks),
        "knowledge_file": rag_service.KNOWLEDGE_MD_PATH,
    }
