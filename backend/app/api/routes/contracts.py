"""AMC contract management routes."""

from datetime import datetime, timedelta, timezone
from typing import Optional

# pyrefly: ignore[missing-import]
from fastapi import APIRouter, Depends, HTTPException, Query
# pyrefly: ignore[missing-import]
from sqlalchemy.orm import Session

from app.core.deps import require_dispatcher, require_any
from app.db.models import AMCContract, Asset, MaintenanceVisit, MaintenanceStatus
from app.db.session import get_db
from app.schemas.contracts import ContractCreate, ContractOut, ContractUpdate

router = APIRouter()


def _refresh_contract_status(contract: AMCContract) -> None:
    now = datetime.now(timezone.utc)
    if contract.end_date.replace(tzinfo=timezone.utc) < now:
        contract.status = "expired"
    elif contract.end_date.replace(tzinfo=timezone.utc) < now + timedelta(days=30):
        contract.status = "expiring_soon"
    else:
        contract.status = "active"


@router.get("/contracts", response_model=list[ContractOut])
def list_contracts(
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    expiring_soon: bool = Query(False),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_any),
):
    q = db.query(AMCContract)
    if customer_id:
        q = q.filter(AMCContract.customer_id == customer_id)
    if status:
        q = q.filter(AMCContract.status == status)
    if expiring_soon:
        soon = datetime.now(timezone.utc) + timedelta(days=30)
        q = q.filter(AMCContract.end_date <= soon, AMCContract.status != "expired")
    return q.order_by(AMCContract.end_date).offset(skip).limit(limit).all()


@router.post("/contracts", response_model=ContractOut, status_code=201)
def create_contract(
    body: ContractCreate,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    if db.query(AMCContract).filter(AMCContract.contract_number == body.contract_number).first():
        raise HTTPException(400, f"Contract number '{body.contract_number}' already exists")
    contract = AMCContract(**body.model_dump(exclude={"asset_ids"}))
    _refresh_contract_status(contract)
    db.add(contract)
    db.flush()
    if body.asset_ids:
        assets = db.query(Asset).filter(Asset.id.in_(body.asset_ids)).all()
        contract.assets.extend(assets)
    db.commit()
    db.refresh(contract)
    return contract


@router.get("/contracts/{contract_id}", response_model=ContractOut)
def get_contract(contract_id: int, db: Session = Depends(get_db), _=Depends(require_any)):
    c = db.query(AMCContract).filter(AMCContract.id == contract_id).first()
    if not c:
        raise HTTPException(404, "Contract not found")
    return c


@router.patch("/contracts/{contract_id}", response_model=ContractOut)
def update_contract(
    contract_id: int,
    body: ContractUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    c = db.query(AMCContract).filter(AMCContract.id == contract_id).first()
    if not c:
        raise HTTPException(404, "Contract not found")
    for k, v in body.model_dump(exclude_unset=True, exclude={"asset_ids"}).items():
        setattr(c, k, v)
    if body.asset_ids is not None:
        assets = db.query(Asset).filter(Asset.id.in_(body.asset_ids)).all()
        c.assets = assets
    _refresh_contract_status(c)
    db.commit()
    db.refresh(c)
    return c
