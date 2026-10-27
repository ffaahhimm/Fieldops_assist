"""Site management routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import require_dispatcher, require_any
from app.db.models import Site
from app.db.session import get_db
from app.schemas.sites import SiteCreate, SiteOut, SiteUpdate

router = APIRouter()


@router.get("/sites", response_model=list[SiteOut])
def list_sites(
    customer_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_any),
):
    q = db.query(Site)
    if customer_id:
        q = q.filter(Site.customer_id == customer_id)
    if search:
        q = q.filter(Site.name.ilike(f"%{search}%"))
    return q.order_by(Site.name).offset(skip).limit(limit).all()


@router.post("/sites", response_model=SiteOut, status_code=201)
def create_site(body: SiteCreate, db: Session = Depends(get_db), _=Depends(require_dispatcher)):
    site = Site(**body.model_dump())
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/sites/{site_id}", response_model=SiteOut)
def get_site(site_id: int, db: Session = Depends(get_db), _=Depends(require_any)):
    s = db.query(Site).filter(Site.id == site_id).first()
    if not s:
        raise HTTPException(404, "Site not found")
    return s


@router.patch("/sites/{site_id}", response_model=SiteOut)
def update_site(
    site_id: int,
    body: SiteUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    s = db.query(Site).filter(Site.id == site_id).first()
    if not s:
        raise HTTPException(404, "Site not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/sites/{site_id}", status_code=204)
def delete_site(site_id: int, db: Session = Depends(get_db), _=Depends(require_dispatcher)):
    s = db.query(Site).filter(Site.id == site_id).first()
    if not s:
        raise HTTPException(404, "Site not found")
    db.delete(s)
    db.commit()
