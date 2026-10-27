"""Service ticket routes — the core operational module."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, require_dispatcher, require_any, require_technician
from app.db.models import ServiceTicket, TicketEvent, User, Asset
from app.db.session import get_db
from app.schemas.tickets import (
    TicketCreate, TicketOut, TicketUpdate, TicketEventOut, TicketNoteCreate,
)

router = APIRouter()

# Response SLA targets (minutes) — demo settings, not real contractual SLAs
SLA_RESPONSE_MINUTES = {
    "critical": 60,
    "high": 240,
    "medium": 480,
    "low": 1440,
}


def _auto_response_due(priority: str) -> datetime:
    minutes = SLA_RESPONSE_MINUTES.get(priority, 480)
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def _next_ticket_number(db: Session) -> str:
    count = db.query(ServiceTicket).count()
    return f"TKT-{datetime.now(timezone.utc).year}-{count + 1:04d}"


@router.get("/tickets", response_model=list[TicketOut])
def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    technician_id: Optional[int] = Query(None),
    overdue: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_any),
):
    q = db.query(ServiceTicket)
    if status:
        q = q.filter(ServiceTicket.status == status)
    if priority:
        q = q.filter(ServiceTicket.priority == priority)
    if category:
        q = q.filter(ServiceTicket.category == category)
    if customer_id:
        q = q.filter(ServiceTicket.customer_id == customer_id)
    if technician_id:
        q = q.filter(ServiceTicket.technician_id == technician_id)
    if overdue is True:
        now = datetime.now(timezone.utc)
        q = q.filter(
            ServiceTicket.response_due < now,
            ServiceTicket.status.notin_(["resolved", "closed"]),
        )
    if search:
        q = q.filter(ServiceTicket.ticket_number.ilike(f"%{search}%") | ServiceTicket.title.ilike(f"%{search}%"))
    return q.order_by(ServiceTicket.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(
    body: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dispatcher),
):
    ticket = ServiceTicket(
        **body.model_dump(exclude={"response_due"}),
        ticket_number=_next_ticket_number(db),
        response_due=body.response_due or _auto_response_due(body.priority),
    )
    db.add(ticket)
    db.flush()
    db.add(TicketEvent(
        ticket_id=ticket.id,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        event_type="created",
        detail=f"Ticket created by {current_user.full_name}.",
    ))
    # If asset provided, mark it as degraded
    if body.asset_id:
        asset = db.query(Asset).filter(Asset.id == body.asset_id).first()
        if asset and asset.status == "operational":
            asset.status = "degraded"
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db), _=Depends(require_any)):
    t = db.query(ServiceTicket).filter(ServiceTicket.id == ticket_id).first()
    if not t:
        raise HTTPException(404, "Ticket not found")
    return t


@router.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: int,
    body: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technician),
):
    t = db.query(ServiceTicket).filter(ServiceTicket.id == ticket_id).first()
    if not t:
        raise HTTPException(404, "Ticket not found")

    changes = body.model_dump(exclude_unset=True)
    old_status = t.status

    for k, v in changes.items():
        setattr(t, k, v)

    # Auto-set closed_at when resolved/closed
    new_status = changes.get("status", old_status)
    if new_status in ("resolved", "closed") and not t.closed_at:
        t.closed_at = datetime.now(timezone.utc)
        # Mark asset operational if was degraded
        if t.asset_id:
            asset = db.query(Asset).filter(Asset.id == t.asset_id).first()
            if asset and asset.status == "degraded":
                asset.status = "operational"
                asset.last_service_date = datetime.now(timezone.utc)

    if "status" in changes and changes["status"] != old_status:
        db.add(TicketEvent(
            ticket_id=t.id,
            actor_id=current_user.id,
            actor_name=current_user.full_name,
            event_type="status_change",
            detail=f"Status changed from '{old_status}' to '{changes['status']}'.",
        ))

    if "technician_id" in changes:
        db.add(TicketEvent(
            ticket_id=t.id,
            actor_id=current_user.id,
            actor_name=current_user.full_name,
            event_type="assigned",
            detail=f"Technician assignment updated by {current_user.full_name}.",
        ))

    db.commit()
    db.refresh(t)
    return t


@router.get("/tickets/{ticket_id}/events", response_model=list[TicketEventOut])
def get_ticket_events(ticket_id: int, db: Session = Depends(get_db), _=Depends(require_any)):
    t = db.query(ServiceTicket).filter(ServiceTicket.id == ticket_id).first()
    if not t:
        raise HTTPException(404, "Ticket not found")
    return t.events


@router.post("/tickets/{ticket_id}/events", response_model=TicketEventOut, status_code=201)
def add_ticket_note(
    ticket_id: int,
    body: TicketNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technician),
):
    t = db.query(ServiceTicket).filter(ServiceTicket.id == ticket_id).first()
    if not t:
        raise HTTPException(404, "Ticket not found")
    event = TicketEvent(
        ticket_id=ticket_id,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        event_type=body.event_type,
        detail=body.detail,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
