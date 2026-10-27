"""Reports routes — data exports and printable service reports."""

import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.deps import require_any
from app.db.models import ServiceTicket, Asset, MaintenanceVisit, AMCContract
from app.db.session import get_db

router = APIRouter()


@router.get("/reports/tickets")
def tickets_report(db: Session = Depends(get_db), _=Depends(require_any)):
    tickets = db.query(ServiceTicket).order_by(ServiceTicket.created_at.desc()).all()
    now = datetime.now(timezone.utc)
    return [
        {
            "ticket_number": t.ticket_number,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
            "category": t.category,
            "customer_id": t.customer_id,
            "technician_id": t.technician_id,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            "closed_at": t.closed_at.isoformat() if t.closed_at else None,
            "overdue": bool(
                t.response_due
                and t.response_due < now
                and t.status not in ("resolved", "closed")
            ),
        }
        for t in tickets
    ]


@router.get("/reports/tickets/csv")
def tickets_csv(db: Session = Depends(get_db), _=Depends(require_any)):
    tickets = db.query(ServiceTicket).order_by(ServiceTicket.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Ticket #", "Title", "Status", "Priority", "Category", "Created", "Closed"])
    for t in tickets:
        writer.writerow([
            t.ticket_number, t.title, t.status, t.priority, t.category,
            t.created_at, t.closed_at,
        ])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tickets.csv"},
    )


@router.get("/reports/assets")
def assets_report(db: Session = Depends(get_db), _=Depends(require_any)):
    assets = db.query(Asset).filter(Asset.is_active == True).order_by(Asset.category).all()
    return [
        {
            "asset_tag": a.asset_tag,
            "name": a.name,
            "category": a.category,
            "manufacturer": a.manufacturer,
            "model": a.model,
            "status": a.status,
            "customer_id": a.customer_id,
            "site_id": a.site_id,
            "warranty_expiry": a.warranty_expiry.isoformat() if a.warranty_expiry else None,
        }
        for a in assets
    ]


@router.get("/reports/assets/csv")
def assets_csv(db: Session = Depends(get_db), _=Depends(require_any)):
    assets = db.query(Asset).filter(Asset.is_active == True).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Asset Tag", "Name", "Category", "Manufacturer", "Model", "Serial", "Status", "Warranty Expiry"])
    for a in assets:
        writer.writerow([
            a.asset_tag, a.name, a.category, a.manufacturer, a.model,
            a.serial_number, a.status,
            a.warranty_expiry.date() if a.warranty_expiry else "",
        ])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=assets.csv"},
    )


@router.get("/reports/tickets/{ticket_id}/service-report")
def service_report(ticket_id: int, db: Session = Depends(get_db), _=Depends(require_any)):
    t = db.query(ServiceTicket).filter(ServiceTicket.id == ticket_id).first()
    if not t:
        from fastapi import HTTPException
        raise HTTPException(404, "Ticket not found")
    return {
        "ticket_number": t.ticket_number,
        "title": t.title,
        "description": t.description,
        "customer_id": t.customer_id,
        "site_id": t.site_id,
        "asset_id": t.asset_id,
        "category": t.category,
        "priority": t.priority,
        "status": t.status,
        "technician_id": t.technician_id,
        "resolution_notes": t.resolution_notes,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "closed_at": t.closed_at.isoformat() if t.closed_at else None,
        "events": [
            {"event_type": e.event_type, "detail": e.detail, "actor": e.actor_name, "at": e.created_at.isoformat()}
            for e in t.events
        ],
        "disclaimer": "This report is generated from demo data and does not represent a real service engagement.",
    }
