"""Asset inventory routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import require_dispatcher, require_any
from app.db.models import Asset
from app.db.session import get_db
from app.schemas.assets import AssetCreate, AssetOut, AssetUpdate

router = APIRouter()


@router.get("/assets", response_model=list[AssetOut])
def list_assets(
    customer_id: Optional[int] = Query(None),
    site_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_any),
):
    q = db.query(Asset)
    if is_active is not None:
        q = q.filter(Asset.is_active == is_active)
    if customer_id:
        q = q.filter(Asset.customer_id == customer_id)
    if site_id:
        q = q.filter(Asset.site_id == site_id)
    if category:
        q = q.filter(Asset.category == category)
    if status:
        q = q.filter(Asset.status == status)
    if search:
        like = f"%{search}%"
        q = q.filter(
            Asset.name.ilike(like)
            | Asset.asset_tag.ilike(like)
            | Asset.serial_number.ilike(like)
            | Asset.model.ilike(like)
        )
    return q.order_by(Asset.name).offset(skip).limit(limit).all()


@router.post("/assets", response_model=AssetOut, status_code=201)
def create_asset(
    body: AssetCreate,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    if db.query(Asset).filter(Asset.asset_tag == body.asset_tag).first():
        raise HTTPException(400, f"Asset tag '{body.asset_tag}' already exists")
    if body.serial_number and db.query(Asset).filter(Asset.serial_number == body.serial_number).first():
        raise HTTPException(400, f"Serial number '{body.serial_number}' already exists")
    asset = Asset(**body.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/assets/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: int, db: Session = Depends(get_db), _=Depends(require_any)):
    a = db.query(Asset).filter(Asset.id == asset_id).first()
    if not a:
        raise HTTPException(404, "Asset not found")
    return a


@router.patch("/assets/{asset_id}", response_model=AssetOut)
def update_asset(
    asset_id: int,
    body: AssetUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    a = db.query(Asset).filter(Asset.id == asset_id).first()
    if not a:
        raise HTTPException(404, "Asset not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/assets/{asset_id}", status_code=204)
def archive_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    a = db.query(Asset).filter(Asset.id == asset_id).first()
    if not a:
        raise HTTPException(404, "Asset not found")
    a.is_active = False
    db.commit()
