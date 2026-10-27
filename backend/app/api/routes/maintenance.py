"""Maintenance visit routes."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import require_dispatcher, require_any, require_technician
from app.db.models import MaintenanceVisit, MaintenanceStatus
from app.db.session import get_db
from app.schemas.maintenance import MaintenanceVisitCreate, MaintenanceVisitOut, MaintenanceVisitUpdate

router = APIRouter()


@router.get("/maintenance", response_model=list[MaintenanceVisitOut])
def list_visits(
    status: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    technician_id: Optional[int] = Query(None),
    upcoming: bool = Query(False),
    overdue: bool = Query(False),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_any),
):
    q = db.query(MaintenanceVisit)
    if status:
        q = q.filter(MaintenanceVisit.status == status)
    if customer_id:
        q = q.filter(MaintenanceVisit.customer_id == customer_id)
    if technician_id:
        q = q.filter(MaintenanceVisit.technician_id == technician_id)
    if upcoming:
        now = datetime.now(timezone.utc)
        q = q.filter(
            MaintenanceVisit.scheduled_date >= now,
            MaintenanceVisit.status == MaintenanceStatus.scheduled,
        )
    if overdue:
        now = datetime.now(timezone.utc)
        q = q.filter(
            MaintenanceVisit.scheduled_date < now,
            MaintenanceVisit.status == MaintenanceStatus.scheduled,
        )
    return q.order_by(MaintenanceVisit.scheduled_date).offset(skip).limit(limit).all()


@router.post("/maintenance", response_model=MaintenanceVisitOut, status_code=201)
def create_visit(
    body: MaintenanceVisitCreate,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    visit = MaintenanceVisit(**body.model_dump())
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


@router.get("/maintenance/{visit_id}", response_model=MaintenanceVisitOut)
def get_visit(visit_id: int, db: Session = Depends(get_db), _=Depends(require_any)):
    v = db.query(MaintenanceVisit).filter(MaintenanceVisit.id == visit_id).first()
    if not v:
        raise HTTPException(404, "Maintenance visit not found")
    return v


@router.patch("/maintenance/{visit_id}", response_model=MaintenanceVisitOut)
def update_visit(
    visit_id: int,
    body: MaintenanceVisitUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_technician),
):
    v = db.query(MaintenanceVisit).filter(MaintenanceVisit.id == visit_id).first()
    if not v:
        raise HTTPException(404, "Maintenance visit not found")
    data = body.model_dump(exclude_unset=True)
    for k, val in data.items():
        setattr(v, k, val)
    if data.get("status") == "completed" and not v.completed_at:
        v.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(v)
    return v
