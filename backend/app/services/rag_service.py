"""
RAG (Retrieval-Augmented Generation) service.

Index strategy:
- Embeddings are generated using sentence-transformers (all-MiniLM-L6-v2 by default).
- Vectors are stored as JSON in the DocumentChunk table (SQLite-compatible).
- For production, swap the in-DB storage for a proper vector store (pgvector, FAISS, Chroma).
- If sentence-transformers is not available, falls back to keyword (TF-IDF-like) retrieval.

This module NEVER invents citations. It only returns chunks that exist in the database.
"""

import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from app.db.models import KnowledgeDocument, DocumentChunk

logger = logging.getLogger(__name__)

# Try to load sentence-transformers; gracefully degrade if unavailable
_embedder = None
try:
    from sentence_transformers import SentenceTransformer
    from app.core.config import settings
    _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
    logger.info("Sentence-transformers embedder loaded: %s", settings.EMBEDDING_MODEL)
except Exception as e:
    logger.warning("sentence-transformers not available (%s). Using keyword fallback.", e)


def index_document(db: Session, doc: KnowledgeDocument, chunks: List[str]) -> None:
    """Store chunks in DB with optional embeddings."""
    now = datetime.now(timezone.utc)
    for i, content in enumerate(chunks):
        embedding_json = None
        if _embedder is not None:
            try:
                vec = _embedder.encode(content, convert_to_numpy=True).tolist()
                embedding_json = json.dumps(vec)
            except Exception as e:
                logger.warning("Embedding failed for chunk %d: %s", i, e)

        db.add(DocumentChunk(
            document_id=doc.id,
            chunk_index=i,
            content=content,
            embedding_json=embedding_json,
        ))

    doc.status = "indexed"
    doc.chunk_count = len(chunks)
    doc.indexed_at = now
    db.commit()


def retrieve_chunks(db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant chunks for a query.
    Uses cosine similarity if embeddings are available, otherwise keyword overlap.
    Returns only chunks that exist in the DB — never fabricated content.
    """
    chunks = (
        db.query(DocumentChunk)
        .join(KnowledgeDocument)
        .filter(KnowledgeDocument.status == "indexed")
        .all()
    )

    if not chunks:
        return []

    if _embedder is not None:
        return _embed_retrieve(query, chunks, top_k)
    else:
        return _keyword_retrieve(query, chunks, top_k)


def _embed_retrieve(query: str, chunks: List[DocumentChunk], top_k: int) -> List[Dict]:
    import numpy as np

    query_vec = _embedder.encode(query, convert_to_numpy=True)
    scored = []
    for chunk in chunks:
        if not chunk.embedding_json:
            continue
        try:
            doc_vec = np.array(json.loads(chunk.embedding_json))
            # Cosine similarity
            sim = float(np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec) + 1e-9))
            scored.append((sim, chunk))
        except Exception:
            continue

    scored.sort(key=lambda x: x[0], reverse=True)
    return [_chunk_to_dict(c) for _, c in scored[:top_k]]


def _keyword_retrieve(query: str, chunks: List[DocumentChunk], top_k: int) -> List[Dict]:
    """Simple keyword overlap scoring as fallback when embeddings unavailable."""
    query_words = set(query.lower().split())
    scored = []
    for chunk in chunks:
        words = set(chunk.content.lower().split())
        score = len(query_words & words)
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [_chunk_to_dict(c) for _, c in scored[:top_k]]


def _chunk_to_dict(chunk: DocumentChunk) -> Dict[str, Any]:
    return {
        "chunk_id": chunk.id,
        "document_id": chunk.document_id,
        "document_title": chunk.document.title if chunk.document else "Unknown",
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
    }
