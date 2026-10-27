"""Knowledge base document management routes."""

import os
import shutil
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import require_dispatcher, require_any
from app.db.models import KnowledgeDocument, DocumentChunk
from app.db.session import get_db
from app.schemas.knowledge import DocumentOut
from app.services.document_parser import parse_document
from app.services.rag_service import index_document

router = APIRouter()

ALLOWED_TYPES = {"application/pdf", "text/plain", "text/markdown"}
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


@router.get("/knowledge/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db), _=Depends(require_any)):
    return db.query(KnowledgeDocument).order_by(KnowledgeDocument.uploaded_at.desc()).all()


@router.post("/knowledge/documents", response_model=DocumentOut, status_code=201)
async def upload_document(
    title: str = Form(...),
    category: str = Form("general"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    # Validate extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type '{ext}' not allowed. Use PDF, TXT or MD.")

    # Validate size
    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(400, f"File exceeds {settings.MAX_UPLOAD_MB} MB limit.")

    # Save to disk
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{os.path.basename(file.filename or 'doc')}"
    dest_path = os.path.join(settings.UPLOAD_DIR, safe_name)
    with open(dest_path, "wb") as f:
        f.write(content)

    doc = KnowledgeDocument(
        title=title,
        category=category,
        filename=file.filename or safe_name,
        file_path=dest_path,
        file_type=ext.lstrip("."),
        file_size_bytes=len(content),
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Parse and index (best-effort; errors recorded in DB)
    try:
        chunks = parse_document(dest_path, ext)
        index_document(db, doc, chunks)
    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        db.commit()

    db.refresh(doc)
    return doc


@router.get("/knowledge/documents/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: int, db: Session = Depends(get_db), _=Depends(require_any)):
    d = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not d:
        raise HTTPException(404, "Document not found")
    return d


@router.delete("/knowledge/documents/{doc_id}", status_code=204)
def delete_document(doc_id: int, db: Session = Depends(get_db), _=Depends(require_dispatcher)):
    d = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not d:
        raise HTTPException(404, "Document not found")
    # Remove file
    if os.path.exists(d.file_path):
        os.remove(d.file_path)
    db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).delete()
    db.delete(d)
    db.commit()
