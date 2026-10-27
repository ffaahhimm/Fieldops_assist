"""Audit log routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db.models import AuditLog
from app.db.session import get_db
from app.schemas.audit import AuditLogOut

router = APIRouter()


@router.get("/audit", response_model=list[AuditLogOut])
def list_audit_logs(
    resource_type: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    q = db.query(AuditLog)
    if resource_type:
        q = q.filter(AuditLog.resource_type == resource_type)
    return q.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
