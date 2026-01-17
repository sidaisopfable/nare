"""
Sage RAG Module
Local embeddings with Sentence Transformers + ChromaDB for vector storage.
"""

import os
from pathlib import Path
from typing import List, Tuple
import hashlib
import json

# Lazy imports to avoid loading heavy libs until needed
_embedding_model = None
_chroma_client = None
_collection = None

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
CHROMA_DIR = Path.home() / ".sage_chroma"
CACHE_FILE = CHROMA_DIR / "doc_hashes.json"


def get_embedding_model():
    """Lazy load the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        # all-MiniLM-L6-v2 is fast and good enough for this use case
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


def get_collection():
    """Get or create the ChromaDB collection."""
    global _chroma_client, _collection
    if _collection is None:
        import chromadb
        from chromadb.config import Settings
        
        CHROMA_DIR.mkdir(exist_ok=True)
        
        _chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        _collection = _chroma_client.get_or_create_collection(
            name="sage_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def compute_doc_hash(content: str) -> str:
    """Compute hash of document content."""
    return hashlib.md5(content.encode()).hexdigest()


def load_doc_hashes() -> dict:
    """Load cached document hashes."""
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def save_doc_hashes(hashes: dict):
    """Save document hashes."""
    CHROMA_DIR.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(hashes))


def chunk_document(content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split document into overlapping chunks.
    
    Args:
        content: Full document text
        chunk_size: Target characters per chunk
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    # Split by paragraphs first
    paragraphs = content.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # If adding this paragraph exceeds chunk size, save current and start new
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep some overlap
            words = current_chunk.split()
            overlap_words = words[-overlap//5:] if len(words) > overlap//5 else []
            current_chunk = ' '.join(overlap_words) + ' ' + para
        else:
            current_chunk += '\n\n' + para if current_chunk else para
    
    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def index_knowledge_base(force: bool = False) -> int:
    """
    Index all knowledge documents into ChromaDB.
    
    Args:
        force: If True, re-index everything even if unchanged
    
    Returns:
        Number of chunks indexed
    """
    collection = get_collection()
    model = get_embedding_model()
    
    # Load existing hashes
    old_hashes = load_doc_hashes()
    new_hashes = {}
    
    all_chunks = []
    all_ids = []
    all_metadatas = []
    
    # Process each knowledge file
    for filepath in KNOWLEDGE_DIR.glob("*.md"):
        content = filepath.read_text()
        doc_hash = compute_doc_hash(content)
        doc_name = filepath.stem
        
        new_hashes[doc_name] = doc_hash
        
        # Skip if unchanged and not forcing
        if not force and old_hashes.get(doc_name) == doc_hash:
            continue
        
        # Delete old chunks for this document
        try:
            existing = collection.get(where={"source": doc_name})
            if existing['ids']:
                collection.delete(ids=existing['ids'])
        except:
            pass
        
        # Chunk the document
        chunks = chunk_document(content)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_name}_{i}"
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadatas.append({
                "source": doc_name,
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
    
    # Embed and store
    if all_chunks:
        embeddings = model.encode(all_chunks).tolist()
        collection.add(
            ids=all_ids,
            embeddings=embeddings,
            documents=all_chunks,
            metadatas=all_metadatas
        )
    
    # Save new hashes
    save_doc_hashes(new_hashes)
    
    return len(all_chunks)


def retrieve(query: str, n_results: int = 3) -> List[Tuple[str, str, float]]:
    """
    Retrieve most relevant chunks for a query.
    
    Args:
        query: User's input text
        n_results: Number of chunks to retrieve
    
    Returns:
        List of (chunk_text, source_doc, relevance_score) tuples
    """
    collection = get_collection()
    model = get_embedding_model()
    
    # Ensure knowledge base is indexed
    if collection.count() == 0:
        index_knowledge_base()
    
    # Embed the query
    query_embedding = model.encode([query]).tolist()
    
    # Search
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format results
    retrieved = []
    for doc, metadata, distance in zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ):
        # Convert distance to similarity (cosine distance → similarity)
        similarity = 1 - distance
        retrieved.append((doc, metadata['source'], similarity))
    
    return retrieved


def build_context(query: str, n_results: int = 3) -> Tuple[str, List[str]]:
    """
    Build context string from retrieved chunks.
    
    Args:
        query: User's input text
        n_results: Number of chunks to retrieve
    
    Returns:
        (context_string, list_of_sources)
    """
    retrieved = retrieve(query, n_results)
    
    if not retrieved:
        return "", []
    
    context_parts = []
    sources = []
    
    for chunk, source, score in retrieved:
        # Only include if relevance is above threshold
        if score > 0.3:
            context_parts.append(f"[From: {source}]\n{chunk}")
            if source not in sources:
                sources.append(source)
    
    context = "\n\n---\n\n".join(context_parts)
    return context, sources


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "index":
        print("Indexing knowledge base...")
        n = index_knowledge_base(force=True)
        print(f"Indexed {n} chunks")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "I feel like a failure after rejection"
        print(f"Searching for: {query}\n")
        
        results = retrieve(query, n_results=3)
        for chunk, source, score in results:
            print(f"--- {source} (score: {score:.3f}) ---")
            print(chunk[:300] + "..." if len(chunk) > 300 else chunk)
            print()
    
    else:
        print("Usage:")
        print("  python rag.py index          # Index knowledge base")
        print("  python rag.py search <query> # Search for relevant chunks")
