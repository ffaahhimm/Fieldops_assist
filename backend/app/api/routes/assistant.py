"""AI Troubleshooting Assistant route."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_any
from app.db.session import get_db
from app.schemas.assistant import AssistantQuery, AssistantResponse
from app.services.rag_service import retrieve_chunks
from app.services.llm_service import generate_answer

router = APIRouter()


@router.post("/assistant", response_model=AssistantResponse)
def query_assistant(
    body: AssistantQuery,
    db: Session = Depends(get_db),
    _=Depends(require_any),
):
    # Step 1: retrieve relevant chunks
    chunks = retrieve_chunks(db, body.question, top_k=5)

    if not chunks:
        return AssistantResponse(
            answer=(
                "No relevant documentation was found in the knowledge base for your question. "
                "Please upload relevant technical manuals or troubleshooting guides to the Knowledge Base."
            ),
            sources=[],
            retrieval_only=True,
            llm_available=False,
        )

    # Step 2: generate answer (LLM or retrieval-only fallback)
    answer, llm_available = generate_answer(body.question, chunks, body.context)

    sources = [
        {
            "document_id": c["document_id"],
            "document_title": c["document_title"],
            "chunk_index": c["chunk_index"],
            "excerpt": c["content"][:400],
        }
        for c in chunks
    ]

    return AssistantResponse(
        answer=answer,
        sources=sources,
        retrieval_only=not llm_available,
        llm_available=llm_available,
    )
