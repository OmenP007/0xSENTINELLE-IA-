import os
import json
import re
from typing import List, Dict, Any, Optional

RAG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag"))
KNOWLEDGE_MD_PATH = os.path.join(RAG_DIR, "knowledge.md")
DOCUMENTS_JSON_PATH = os.path.join(RAG_DIR, "documents.json")
CHROMA_DIR = os.path.join(RAG_DIR, "chroma")

os.makedirs(RAG_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)


# ─── Markdown Parser & Chunking Engine ─────────────────────────────────────────
def parse_markdown_to_chunks(md_path: str = KNOWLEDGE_MD_PATH) -> List[Dict[str, Any]]:
    """Découpe la base Markdown en chunks structurés avec métadonnées."""
    if not os.path.exists(md_path):
        return []

    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    sections = text.split("\n---")
    chunks = []

    for i, sec in enumerate(sections):
        sec = sec.strip()
        if not sec:
            continue

        # Extraction des métadonnées depuis les en-têtes
        id_match = re.search(r"ID:\s*([\w\-]+)", sec)
        cat_match = re.search(r"Catégorie:\s*([^\n|]+)", sec)
        brand_match = re.search(r"Marque:\s*([^\n|]+)", sec)
        domain_match = re.search(r"Domaine Officiel:\s*([^\n]+)", sec)
        signals_match = re.search(r"Signaux de Risque:\s*([^\n]+)", sec)
        attack_match = re.search(r"Attaque:\s*([^\n]+)", sec)

        chunk_id = id_match.group(1) if id_match else f"CHUNK-CI-{i:04d}"
        category = cat_match.group(1).strip() if cat_match else "Général"
        brand = brand_match.group(1).strip() if brand_match else "Inconnu"
        official_domain = domain_match.group(1).strip() if domain_match else ""
        signals_raw = signals_match.group(1).strip() if signals_match else ""
        attack_type = attack_match.group(1).strip() if attack_match else "Général"

        risk_signals = [s.strip() for s in signals_raw.split(",") if s.strip()]

        chunk_doc = {
            "id": chunk_id,
            "category": category,
            "brand": brand,
            "official_domain": official_domain,
            "attack_type": attack_type,
            "risk_signals": risk_signals,
            "content": sec,
            "word_count": len(sec.split()),
        }
        chunks.append(chunk_doc)

    # Sauvegarder dans documents.json
    with open(DOCUMENTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    return chunks


# ─── Vector Index & RAG Search Engine (ChromaDB + Vector Fallback) ────────────
class RAGSearchEngine:
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.chroma_collection = None
        self._init_db()

    def _init_db(self):
        # 1. Parse et charge les documents
        if not os.path.exists(DOCUMENTS_JSON_PATH):
            self.chunks = parse_markdown_to_chunks()
        else:
            try:
                with open(DOCUMENTS_JSON_PATH, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            except Exception:
                self.chunks = parse_markdown_to_chunks()

        # 2. Tentative d'initialisation de ChromaDB
        try:
            import chromadb
            client = chromadb.PersistentClient(path=CHROMA_DIR)
            self.chroma_collection = client.get_or_create_collection(
                name="0xsentinelle_knowledge",
                metadata={"description": "Connaissances Anti-Arnaques Côte d'Ivoire"}
            )
            # Indexer si la collection est vide
            if self.chroma_collection.count() == 0 and self.chunks:
                ids = [c["id"] for c in self.chunks]
                documents = [c["content"] for c in self.chunks]
                metadatas = [
                    {
                        "category": c["category"],
                        "brand": c["brand"],
                        "attack_type": c["attack_type"],
                    }
                    for c in self.chunks
                ]
                self.chroma_collection.add(ids=ids, documents=documents, metadatas=metadatas)
        except Exception as e:
            print(f"[RAG] ChromaDB indisponible, utilisation du moteur vectoriel léger Python : {e}")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Recherche les top_k passages les plus pertinents pour la requête."""
        if not query or not query.strip():
            return []

        # 1. Recherche via ChromaDB si prêt
        if self.chroma_collection:
            try:
                results = self.chroma_collection.query(
                    query_texts=[query],
                    n_results=min(top_k, len(self.chunks) or 1)
                )
                if results and results.get("documents") and results["documents"][0]:
                    matched_ids = results["ids"][0]
                    matched_chunks = [c for c in self.chunks if c["id"] in matched_ids]
                    if matched_chunks:
                        return matched_chunks
            except Exception as e:
                print(f"[RAG] Erreur query ChromaDB, fallback vectoriel: {e}")

        # 2. Moteur vectoriel de fallback (Recherche par chevauchement sémantique & mots-clés)
        query_words = set(re.findall(r"\w+", query.lower()))
        scored_chunks = []

        for chunk in self.chunks:
            chunk_words = set(re.findall(r"\w+", chunk["content"].lower()))
            overlap = len(query_words.intersection(chunk_words))
            # Boost si la marque ou la catégorie matche
            if chunk.get("brand", "").lower() in query.lower():
                overlap += 5
            if chunk.get("category", "").lower() in query.lower():
                overlap += 3
            scored_chunks.append((overlap, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_matches = [c for score, c in scored_chunks if score > 0][:top_k]

        return top_matches


# Instance unique du service RAG
rag_engine = RAGSearchEngine()



def get_relevant_rag_context(user_input: str, top_k: int = 3) -> str:
    """Retourne uniquement les passages RAG pertinents formatés pour Gemini."""
    passages = rag_engine.search(user_input, top_k=top_k)
    if not passages:
        return ""

    context_str = "--- CONNAISSANCES DE RÉFÉRENCE SPÉCIALISÉES (RAG CÔTE D'IVOIRE) ---\n"
    for idx, p in enumerate(passages, 1):
        context_str += (
            f"\n[Extrait #{idx} - ID: {p.get('id')} | Marque: {p.get('brand')} | Attaque: {p.get('attack_type')}]\n"
            f"{p.get('content')}\n"
        )
    context_str += "-------------------------------------------------------------------\n"
    return context_str
