"""Technician management routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import require_dispatcher, require_any
from app.db.models import Technician
from app.db.session import get_db
from app.schemas.technicians import TechnicianCreate, TechnicianOut, TechnicianUpdate

router = APIRouter()


@router.get("/technicians", response_model=list[TechnicianOut])
def list_technicians(
    is_available: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_any),
):
    q = db.query(Technician)
    if is_available is not None:
        q = q.filter(Technician.is_available == is_available)
    return q.order_by(Technician.id).all()


@router.post("/technicians", response_model=TechnicianOut, status_code=201)
def create_technician(
    body: TechnicianCreate,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    if db.query(Technician).filter(Technician.employee_id == body.employee_id).first():
        raise HTTPException(400, f"Employee ID '{body.employee_id}' already exists")
    tech = Technician(**body.model_dump())
    db.add(tech)
    db.commit()
    db.refresh(tech)
    return tech


@router.get("/technicians/{tech_id}", response_model=TechnicianOut)
def get_technician(tech_id: int, db: Session = Depends(get_db), _=Depends(require_any)):
    t = db.query(Technician).filter(Technician.id == tech_id).first()
    if not t:
        raise HTTPException(404, "Technician not found")
    return t


@router.patch("/technicians/{tech_id}", response_model=TechnicianOut)
def update_technician(
    tech_id: int,
    body: TechnicianUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    t = db.query(Technician).filter(Technician.id == tech_id).first()
    if not t:
        raise HTTPException(404, "Technician not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t
