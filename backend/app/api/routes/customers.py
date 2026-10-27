"""Customer management routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import require_dispatcher, require_any
from app.db.models import Customer
from app.db.session import get_db
from app.schemas.customers import CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter()


@router.get("/customers", response_model=list[CustomerOut])
def list_customers(
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_any),
):
    q = db.query(Customer)
    if is_active is not None:
        q = q.filter(Customer.is_active == is_active)
    if search:
        like = f"%{search}%"
        q = q.filter(
            Customer.name.ilike(like) | Customer.code.ilike(like) | Customer.contact_person.ilike(like)
        )
    return q.order_by(Customer.name).offset(skip).limit(limit).all()


@router.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(
    body: CustomerCreate,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    if db.query(Customer).filter(Customer.code == body.code).first():
        raise HTTPException(400, f"Customer code '{body.code}' already exists")
    customer = Customer(**body.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), _=Depends(require_any)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(404, "Customer not found")
    return c


@router.patch("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(404, "Customer not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/customers/{customer_id}", status_code=204)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_dispatcher),
):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(404, "Customer not found")
    c.is_active = False
    db.commit()
