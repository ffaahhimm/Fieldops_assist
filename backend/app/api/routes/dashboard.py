"""Dashboard metrics endpoint — all values derived from the database."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_any
from app.db.models import Asset, ServiceTicket, AMCContract, MaintenanceVisit, AssetStatus
from app.db.session import get_db

router = APIRouter()


@router.get("/dashboard")
def dashboard_metrics(db: Session = Depends(get_db), _=Depends(require_any)):
    now = datetime.now(timezone.utc)
    in_30_days = now + timedelta(days=30)

    # Assets
    total_assets = db.query(Asset).filter(Asset.is_active == True).count()
    assets_with_issue = db.query(Asset).filter(
        Asset.is_active == True,
        Asset.status.in_(["degraded", "offline"]),
    ).count()

    # Tickets
    open_statuses = ["new", "assigned", "in_progress", "waiting_customer"]
    open_tickets = db.query(ServiceTicket).filter(ServiceTicket.status.in_(open_statuses)).count()
    critical_tickets = db.query(ServiceTicket).filter(
        ServiceTicket.priority == "critical",
        ServiceTicket.status.in_(open_statuses),
    ).count()
    overdue_tickets = db.query(ServiceTicket).filter(
        ServiceTicket.response_due < now,
        ServiceTicket.status.in_(open_statuses),
    ).count()

    # Contracts
    expiring_contracts = db.query(AMCContract).filter(
        AMCContract.end_date <= in_30_days,
        AMCContract.status != "expired",
        AMCContract.status != "cancelled",
    ).count()

    # Maintenance
    upcoming_maintenance = db.query(MaintenanceVisit).filter(
        MaintenanceVisit.scheduled_date >= now,
        MaintenanceVisit.scheduled_date <= now + timedelta(days=30),
        MaintenanceVisit.status == "scheduled",
    ).count()
    overdue_maintenance = db.query(MaintenanceVisit).filter(
        MaintenanceVisit.scheduled_date < now,
        MaintenanceVisit.status == "scheduled",
    ).count()

    # Recent tickets (last 5)
    recent_tickets = (
        db.query(ServiceTicket)
        .order_by(ServiceTicket.updated_at.desc())
        .limit(5)
        .all()
    )

    # Ticket breakdown by status
    status_breakdown = {}
    for st in ["new", "assigned", "in_progress", "waiting_customer", "resolved", "closed"]:
        status_breakdown[st] = db.query(ServiceTicket).filter(ServiceTicket.status == st).count()

    priority_breakdown = {}
    for p in ["critical", "high", "medium", "low"]:
        priority_breakdown[p] = db.query(ServiceTicket).filter(
            ServiceTicket.priority == p,
            ServiceTicket.status.in_(open_statuses),
        ).count()

    return {
        "total_assets": total_assets,
        "assets_with_issue": assets_with_issue,
        "open_tickets": open_tickets,
        "critical_tickets": critical_tickets,
        "overdue_tickets": overdue_tickets,
        "expiring_contracts": expiring_contracts,
        "upcoming_maintenance": upcoming_maintenance,
        "overdue_maintenance": overdue_maintenance,
        "recent_tickets": [
            {
                "id": t.id,
                "ticket_number": t.ticket_number,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in recent_tickets
        ],
        "status_breakdown": status_breakdown,
        "priority_breakdown": priority_breakdown,
        "note": "DEMO DATA — fictional records only",
    }
