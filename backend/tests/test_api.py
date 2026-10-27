"""
FieldOps Assist — Backend Test Suite

Run with:  cd backend && pytest -v
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── In-memory SQLite for tests ────────────────────────────────────────────────
TEST_DB_URL = "sqlite:///:memory:"

from app.db.base import Base
from app.db.session import get_db
from main import app

from sqlalchemy.pool import StaticPool

engine_test = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine_test)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db):
    def override_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helper: create a user and log in ─────────────────────────────────────────

def _create_admin(client):
    from app.core.security import hash_password
    from app.db.models import User
    # We can't use the client to create users without auth, so inject directly
    return None  # Not needed if we seed via fixture


def _get_token(client, username="admin", password="Admin@1234") -> str:
    resp = client.post("/api/auth/token", data={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Health check ──────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── Database init ─────────────────────────────────────────────────────────────

def test_db_tables_created(db):
    from sqlalchemy import inspect
    inspector = inspect(engine_test)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "customers" in tables
    assert "assets" in tables
    assert "service_tickets" in tables


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_login_wrong_password(client):
    r = client.post("/api/auth/token", data={"username": "admin", "password": "wrong"})
    assert r.status_code == 401


def test_protected_endpoint_no_token(client):
    r = client.get("/api/customers")
    assert r.status_code == 401


# ── Customer CRUD (requires seeded admin user) ────────────────────────────────

def _seed_admin(db):
    from app.db.models import User
    from app.core.security import hash_password
    if not db.query(User).filter_by(username="admin").first():
        user = User(
            username="admin",
            email="admin@test.local",
            full_name="Test Admin",
            hashed_password=hash_password("Admin@1234"),
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()


def test_customer_create_and_list(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)

    # Create
    r = client.post("/api/customers", json={
        "code": "TEST-001",
        "name": "Test Company LLC",
        "contact_person": "Jane Doe",
        "email": "jane@test.demo",
        "phone": "+971-1-0000000",
    }, headers=headers)
    assert r.status_code == 201
    data = r.json()
    assert data["code"] == "TEST-001"
    assert data["name"] == "Test Company LLC"

    # List
    r2 = client.get("/api/customers", headers=headers)
    assert r2.status_code == 200
    assert any(c["code"] == "TEST-001" for c in r2.json())


def test_customer_duplicate_code_rejected(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)

    payload = {"code": "DUP-001", "name": "Dupe Co"}
    client.post("/api/customers", json=payload, headers=headers)
    r = client.post("/api/customers", json=payload, headers=headers)
    assert r.status_code == 400


# ── Asset CRUD ────────────────────────────────────────────────────────────────

def _seed_customer(client, headers):
    r = client.post("/api/customers", json={"code": "ASSET-CUST", "name": "Asset Test Co"}, headers=headers)
    return r.json()["id"]


def test_asset_create_and_retrieve(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)
    cust_id = _seed_customer(client, headers)

    r = client.post("/api/assets", json={
        "asset_tag": "AST-TEST-001",
        "name": "Test Camera",
        "category": "cctv",
        "customer_id": cust_id,
        "status": "operational",
    }, headers=headers)
    assert r.status_code == 201
    asset_id = r.json()["id"]

    r2 = client.get(f"/api/assets/{asset_id}", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["asset_tag"] == "AST-TEST-001"


def test_asset_duplicate_tag_rejected(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)
    cust_id = _seed_customer(client, headers)

    payload = {"asset_tag": "DUP-TAG", "name": "Cam", "category": "cctv", "customer_id": cust_id}
    client.post("/api/assets", json=payload, headers=headers)
    r = client.post("/api/assets", json=payload, headers=headers)
    assert r.status_code == 400


# ── Ticket CRUD ───────────────────────────────────────────────────────────────

def test_ticket_create(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)
    cust_id = _seed_customer(client, headers)

    r = client.post("/api/tickets", json={
        "title": "Test Ticket",
        "description": "Something broke.",
        "customer_id": cust_id,
        "priority": "high",
        "category": "network",
    }, headers=headers)
    assert r.status_code == 201
    data = r.json()
    assert data["ticket_number"].startswith("TKT-")
    assert data["status"] == "new"


def test_ticket_status_update(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)
    cust_id = _seed_customer(client, headers)

    r = client.post("/api/tickets", json={
        "title": "Status Test",
        "description": "Needs update.",
        "customer_id": cust_id,
        "priority": "medium",
        "category": "other",
    }, headers=headers)
    ticket_id = r.json()["id"]

    r2 = client.patch(f"/api/tickets/{ticket_id}", json={"status": "in_progress"}, headers=headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "in_progress"


def test_ticket_activity_history(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)
    cust_id = _seed_customer(client, headers)

    r = client.post("/api/tickets", json={
        "title": "History Test",
        "description": "Event check.",
        "customer_id": cust_id,
        "priority": "low",
        "category": "other",
    }, headers=headers)
    ticket_id = r.json()["id"]

    # Add note
    client.post(f"/api/tickets/{ticket_id}/events", json={
        "event_type": "note",
        "detail": "Checked the cable, looks ok.",
    }, headers=headers)

    r2 = client.get(f"/api/tickets/{ticket_id}/events", headers=headers)
    assert r2.status_code == 200
    events = r2.json()
    assert len(events) >= 2  # created + note
    assert any(e["event_type"] == "note" for e in events)


# ── Overdue ticket calculation ────────────────────────────────────────────────

def test_overdue_ticket_filter(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)
    cust_id = _seed_customer(client, headers)

    # Create ticket with past due date
    past = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    r = client.post("/api/tickets", json={
        "title": "Overdue Test",
        "description": "Was due hours ago.",
        "customer_id": cust_id,
        "priority": "critical",
        "category": "network",
        "response_due": past,
    }, headers=headers)
    assert r.status_code == 201

    r2 = client.get("/api/tickets?overdue=true", headers=headers)
    assert r2.status_code == 200
    assert any(t["title"] == "Overdue Test" for t in r2.json())


# ── Contract expiry calculation ───────────────────────────────────────────────

def test_contract_expiry_status(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)
    cust_id = _seed_customer(client, headers)

    soon = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    start = (datetime.now(timezone.utc) - timedelta(days=200)).isoformat()

    r = client.post("/api/contracts", json={
        "contract_number": "EXP-TEST-001",
        "customer_id": cust_id,
        "start_date": start,
        "end_date": soon,
    }, headers=headers)
    assert r.status_code == 201
    assert r.json()["status"] == "expiring_soon"


# ── Dashboard derives values from DB ─────────────────────────────────────────

def test_dashboard_returns_db_values(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)

    r = client.get("/api/dashboard", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "total_assets" in data
    assert "open_tickets" in data
    assert isinstance(data["total_assets"], int)


# ── AI assistant graceful degradation ────────────────────────────────────────

def test_assistant_no_documents(client, db):
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)

    r = client.post("/api/assistant", json={"question": "What should I check for a camera offline?"}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    # With no documents, must not invent — it should return a clear no-result response
    assert data["sources"] == []
    assert "knowledge base" in data["answer"].lower() or "no relevant" in data["answer"].lower()
    assert data["llm_available"] is False


# ── REGRESSION: ticket list shape and auth ───────────────────────────────────
# These tests document the root cause of the page.tsx data-loading failure:
#   1. Unauthenticated calls return 401 (not a network error).
#   2. The ticket list endpoint returns a PLAIN JSON ARRAY (not {items:[...]}).
#   3. Fields are `title` and `ticket_number`, NOT `subject` or `id` for display.

def test_ticket_list_requires_authentication(client, db):
    """GET /api/tickets with no token must return 401, not 200 or 500."""
    r = client.get("/api/tickets")
    assert r.status_code == 401, (
        f"Expected 401 but got {r.status_code}. "
        "This is the root cause: page.tsx was calling the endpoint without a JWT token."
    )
    body = r.json()
    assert "detail" in body


def test_dashboard_requires_authentication(client, db):
    """GET /api/dashboard with no token must return 401."""
    r = client.get("/api/dashboard")
    assert r.status_code == 401, (
        f"Expected 401 but got {r.status_code}. "
        "Dashboard endpoint also requires authentication."
    )


def test_ticket_list_returns_plain_array_not_wrapped(client, db):
    """
    The /api/tickets endpoint returns a plain JSON array [], NOT {items: [...], total: N}.
    The frontend must NOT do tickRes.data.items — it must use tickRes.data directly.
    """
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)

    r = client.get("/api/tickets", headers=headers)
    assert r.status_code == 200

    data = r.json()
    # MUST be a list, never a dict with an 'items' key
    assert isinstance(data, list), (
        f"Expected a plain list but got {type(data).__name__}. "
        "frontend must read tickRes.data directly, not tickRes.data.items"
    )


def test_ticket_list_field_names_match_frontend_types(client, db):
    """
    Each ticket in the list must have `title` (NOT `subject`) and `ticket_number`.
    This validates the TicketOut schema against what page.tsx expects.
    """
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)
    cust_id = _seed_customer(client, headers)

    # Create a ticket so we have at least one to inspect
    r = client.post("/api/tickets", json={
        "title": "Schema Regression Test",
        "description": "Verify field names match frontend ServiceTicket type.",
        "customer_id": cust_id,
        "priority": "medium",
        "category": "network",
    }, headers=headers)
    assert r.status_code == 201

    r2 = client.get("/api/tickets", headers=headers)
    assert r2.status_code == 200
    tickets = r2.json()
    assert len(tickets) >= 1

    ticket = tickets[0]
    # Required fields that frontend ServiceTicket type references
    assert "title" in ticket, "'title' field missing — frontend was reading 'subject' which does not exist"
    assert "ticket_number" in ticket, "'ticket_number' field missing"
    assert "status" in ticket
    assert "priority" in ticket
    assert "category" in ticket
    assert "created_at" in ticket
    assert "id" in ticket

    # Must NOT have a field called 'subject'
    assert "subject" not in ticket, (
        "'subject' found but should not exist. Frontend must use 'title'."
    )


def test_dashboard_summary_card_fields_are_integers(client, db):
    """
    Dashboard must return total_assets, open_tickets, critical_tickets, overdue_tickets
    as integer values — not null, not strings. These back the summary stat cards.
    """
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)

    r = client.get("/api/dashboard", headers=headers)
    assert r.status_code == 200
    data = r.json()

    for field in ("total_assets", "open_tickets", "critical_tickets", "overdue_tickets"):
        assert field in data, f"'{field}' missing from dashboard response"
        assert isinstance(data[field], int), (
            f"'{field}' must be an int, got {type(data[field]).__name__}: {data[field]}"
        )
        assert data[field] >= 0, f"'{field}' must be non-negative, got {data[field]}"


def test_ticket_list_with_empty_db_returns_empty_array(client, db):
    """
    When no tickets exist, the list endpoint returns [] (empty list), not an error.
    Frontend must show 'No tickets match' state, not an error banner.
    """
    _seed_admin(db)
    token = _get_token(client)
    headers = _auth_headers(token)

    r = client.get("/api/tickets", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # No tickets seeded, so list must be empty
    assert data == [], f"Expected [] but got {len(data)} tickets in empty DB"
