"""
Reproducible seed data for the FieldOps Assist demo.
All records are clearly fictional. Running this multiple times is safe — existing
records are detected by unique keys and skipped.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import (
    User, Technician, Customer, Site, Asset, ServiceTicket, TicketEvent,
    AMCContract, MaintenanceVisit,
    AssetStatus, TicketStatus, TicketPriority, TicketCategory,
    ContractStatus, MaintenanceStatus,
)
from app.core.security import hash_password


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def seed_demo_data() -> None:
    db: Session = SessionLocal()
    try:
        _seed(db)
    finally:
        db.close()


def _seed(db: Session) -> None:
    # ── Users ────────────────────────────────────────────────────────────────
    admin = db.query(User).filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@fieldops-demo.local",
            full_name="Alex Admin",
            hashed_password=hash_password("Admin@1234"),
            role="admin",
        )
        db.add(admin)

    dispatcher = db.query(User).filter_by(username="dispatcher").first()
    if not dispatcher:
        dispatcher = User(
            username="dispatcher",
            email="dispatch@fieldops-demo.local",
            full_name="Dana Dispatcher",
            hashed_password=hash_password("Dispatch@1234"),
            role="dispatcher",
        )
        db.add(dispatcher)

    tech_user1 = db.query(User).filter_by(username="tech.ibrahim").first()
    if not tech_user1:
        tech_user1 = User(
            username="tech.ibrahim",
            email="ibrahim@fieldops-demo.local",
            full_name="Ibrahim Al-Rashidi",
            hashed_password=hash_password("Tech@1234"),
            role="technician",
        )
        db.add(tech_user1)

    tech_user2 = db.query(User).filter_by(username="tech.priya").first()
    if not tech_user2:
        tech_user2 = User(
            username="tech.priya",
            email="priya@fieldops-demo.local",
            full_name="Priya Nair",
            hashed_password=hash_password("Tech@1234"),
            role="technician",
        )
        db.add(tech_user2)

    manager_user = db.query(User).filter_by(username="manager").first()
    if not manager_user:
        manager_user = User(
            username="manager",
            email="manager@fieldops-demo.local",
            full_name="Mona Al-Farsi",
            hashed_password=hash_password("Manager@1234"),
            role="manager",
        )
        db.add(manager_user)

    db.flush()

    # ── Technicians ──────────────────────────────────────────────────────────
    tech1 = db.query(Technician).filter_by(employee_id="EMP-001").first()
    if not tech1:
        tech1 = Technician(
            user_id=tech_user1.id,
            employee_id="EMP-001",
            phone="+971-50-1234567",
            is_available=True,
            notes="Specialises in CCTV, NVR, and structured cabling.",
        )
        db.add(tech1)

    tech2 = db.query(Technician).filter_by(employee_id="EMP-002").first()
    if not tech2:
        tech2 = Technician(
            user_id=tech_user2.id,
            employee_id="EMP-002",
            phone="+971-55-9876543",
            is_available=True,
            notes="Networking, access control, and server maintenance.",
        )
        db.add(tech2)

    db.flush()

    # ── Customers ────────────────────────────────────────────────────────────
    customer1 = db.query(Customer).filter_by(code="CUST-001").first()
    if not customer1:
        customer1 = Customer(
            code="CUST-001",
            name="Gulf Commerce LLC",
            contact_person="Khalid Al-Mansoori",
            email="khalid@gulfcommerce.demo",
            phone="+971-4-3456789",
            address="Office Tower B, Dubai Investment Park, Dubai, UAE",
            notes="Primary office in DIP. Three branches in Sharjah and Abu Dhabi.",
        )
        db.add(customer1)

    customer2 = db.query(Customer).filter_by(code="CUST-002").first()
    if not customer2:
        customer2 = Customer(
            code="CUST-002",
            name="Crescent Medical Centre",
            contact_person="Dr. Ayesha Rahman",
            email="it@crescentmedical.demo",
            phone="+971-2-8765432",
            address="Al Muroor Road, Abu Dhabi, UAE",
            notes="Healthcare client. CCTV, access control and server room support.",
        )
        db.add(customer2)

    customer3 = db.query(Customer).filter_by(code="CUST-003").first()
    if not customer3:
        customer3 = Customer(
            code="CUST-003",
            name="Al Noor Logistics",
            contact_person="Tariq Hussain",
            email="ops@alnoorlogistics.demo",
            phone="+971-6-5432198",
            address="Industrial Area 12, Sharjah, UAE",
            notes="Warehouse and fleet office. Large CCTV deployment.",
        )
        db.add(customer3)

    db.flush()

    # ── Sites ────────────────────────────────────────────────────────────────
    site1 = db.query(Site).filter_by(name="Gulf Commerce — DIP Main Office").first()
    if not site1:
        site1 = Site(
            customer_id=customer1.id,
            name="Gulf Commerce — DIP Main Office",
            address="Office Tower B, Floor 5, Dubai Investment Park, Dubai",
            contact_name="Reem Hassan",
            contact_phone="+971-50-3333444",
        )
        db.add(site1)

    site2 = db.query(Site).filter_by(name="Gulf Commerce — Sharjah Branch").first()
    if not site2:
        site2 = Site(
            customer_id=customer1.id,
            name="Gulf Commerce — Sharjah Branch",
            address="Al Nahda, Sharjah, UAE",
            contact_name="Omar Khalil",
            contact_phone="+971-55-2211330",
        )
        db.add(site2)

    site3 = db.query(Site).filter_by(name="Crescent Medical Centre — Main Building").first()
    if not site3:
        site3 = Site(
            customer_id=customer2.id,
            name="Crescent Medical Centre — Main Building",
            address="Al Muroor Road, Abu Dhabi",
            contact_name="Sana Ali",
            contact_phone="+971-2-8765500",
        )
        db.add(site3)

    site4 = db.query(Site).filter_by(name="Al Noor — Warehouse A").first()
    if not site4:
        site4 = Site(
            customer_id=customer3.id,
            name="Al Noor — Warehouse A",
            address="Industrial Area 12, Block C, Sharjah",
            contact_name="Tariq Hussain",
            contact_phone="+971-50-9988776",
        )
        db.add(site4)

    db.flush()

    # ── Assets ───────────────────────────────────────────────────────────────
    asset_cam1 = db.query(Asset).filter_by(asset_tag="AST-CAM-001").first()
    if not asset_cam1:
        asset_cam1 = Asset(
            asset_tag="AST-CAM-001",
            name="CCTV Camera — Lobby Entrance",
            category="cctv",
            asset_type="IP Dome Camera",
            manufacturer="Hikvision",
            model="DS-2CD2147G2-LU",
            serial_number="HKV-2024-001",
            ip_address="192.168.10.21",
            customer_id=customer1.id,
            site_id=site1.id,
            installation_date=utcnow() - timedelta(days=365),
            warranty_expiry=utcnow() + timedelta(days=365),
            status=AssetStatus.offline,  # This is the camera in our demo ticket
            notes="4MP ColorVu outdoor dome. Covers main lobby entrance.",
        )
        db.add(asset_cam1)

    asset_nvr1 = db.query(Asset).filter_by(asset_tag="AST-NVR-001").first()
    if not asset_nvr1:
        asset_nvr1 = Asset(
            asset_tag="AST-NVR-001",
            name="NVR — Main Security Room",
            category="cctv",
            asset_type="Network Video Recorder",
            manufacturer="Hikvision",
            model="DS-7616NXI-I2/16P/S",
            serial_number="HKV-NVR-2024-001",
            ip_address="192.168.10.10",
            customer_id=customer1.id,
            site_id=site1.id,
            installation_date=utcnow() - timedelta(days=365),
            warranty_expiry=utcnow() + timedelta(days=365),
            status=AssetStatus.operational,
            notes="16-channel NVR. Connected to all lobby and floor cameras.",
        )
        db.add(asset_nvr1)

    asset_sw1 = db.query(Asset).filter_by(asset_tag="AST-SW-001").first()
    if not asset_sw1:
        asset_sw1 = Asset(
            asset_tag="AST-SW-001",
            name="Network Switch — Floor 5 IDF",
            category="network",
            asset_type="Managed Switch",
            manufacturer="Cisco",
            model="Catalyst 2960-X",
            serial_number="CSC-SW-2024-001",
            ip_address="192.168.1.5",
            customer_id=customer1.id,
            site_id=site1.id,
            installation_date=utcnow() - timedelta(days=500),
            warranty_expiry=utcnow() - timedelta(days=30),  # Warranty expired
            status=AssetStatus.operational,
            notes="48-port PoE+ switch. Powers IP cameras and WAPs.",
        )
        db.add(asset_sw1)

    asset_srv1 = db.query(Asset).filter_by(asset_tag="AST-SRV-001").first()
    if not asset_srv1:
        asset_srv1 = Asset(
            asset_tag="AST-SRV-001",
            name="File Server — Primary",
            category="server",
            asset_type="Rack Server",
            manufacturer="Dell",
            model="PowerEdge R540",
            serial_number="DELL-SRV-2024-001",
            customer_id=customer2.id,
            site_id=site3.id,
            installation_date=utcnow() - timedelta(days=730),
            warranty_expiry=utcnow() + timedelta(days=180),
            status=AssetStatus.operational,
            notes="Primary file server. Windows Server 2022.",
        )
        db.add(asset_srv1)

    asset_ac1 = db.query(Asset).filter_by(asset_tag="AST-AC-001").first()
    if not asset_ac1:
        asset_ac1 = Asset(
            asset_tag="AST-AC-001",
            name="Access Control — Server Room Door",
            category="access_control",
            asset_type="Card Reader",
            manufacturer="HID Global",
            model="RP40",
            serial_number="HID-AC-2024-001",
            customer_id=customer2.id,
            site_id=site3.id,
            installation_date=utcnow() - timedelta(days=400),
            warranty_expiry=utcnow() + timedelta(days=200),
            status=AssetStatus.operational,
        )
        db.add(asset_ac1)

    asset_cam2 = db.query(Asset).filter_by(asset_tag="AST-CAM-002").first()
    if not asset_cam2:
        asset_cam2 = Asset(
            asset_tag="AST-CAM-002",
            name="CCTV Camera — Warehouse Gate",
            category="cctv",
            asset_type="PTZ Camera",
            manufacturer="Dahua",
            model="SD49425XB-HNR",
            serial_number="DAH-2024-002",
            ip_address="192.168.20.31",
            customer_id=customer3.id,
            site_id=site4.id,
            installation_date=utcnow() - timedelta(days=200),
            warranty_expiry=utcnow() + timedelta(days=565),
            status=AssetStatus.degraded,
            notes="PTZ camera. Intermittent connection to NVR.",
        )
        db.add(asset_cam2)

    db.flush()

    # ── Service Tickets ──────────────────────────────────────────────────────
    ticket1 = db.query(ServiceTicket).filter_by(ticket_number="TKT-2024-0001").first()
    if not ticket1:
        ticket1 = ServiceTicket(
            ticket_number="TKT-2024-0001",
            title="Lobby CCTV Camera Offline — No Feed",
            description=(
                "The IP dome camera at the main lobby entrance (AST-CAM-001) has been offline "
                "since this morning. The NVR is showing 'No signal' for that channel. "
                "Security staff cannot monitor the entrance. Please investigate urgently."
            ),
            customer_id=customer1.id,
            site_id=site1.id,
            asset_id=asset_cam1.id,
            category=TicketCategory.cctv,
            priority=TicketPriority.high,
            status=TicketStatus.in_progress,
            technician_id=tech1.id,
            response_due=utcnow() + timedelta(hours=4),
            resolution_notes=None,
        )
        db.add(ticket1)
        db.flush()

        db.add(TicketEvent(
            ticket_id=ticket1.id,
            actor_name="Dana Dispatcher",
            event_type="created",
            detail="Ticket created. Customer reported camera offline.",
        ))
        db.add(TicketEvent(
            ticket_id=ticket1.id,
            actor_name="Dana Dispatcher",
            event_type="assigned",
            detail="Assigned to Ibrahim Al-Rashidi (EMP-001) for on-site investigation.",
        ))
        db.add(TicketEvent(
            ticket_id=ticket1.id,
            actor_name="Ibrahim Al-Rashidi",
            event_type="note",
            detail="Initial check: NVR channel 3 shows 'No signal'. Camera PoE indicator on switch port 21 shows amber. Possible PoE fault or cable issue. Will test with spare cable.",
        ))

    ticket2 = db.query(ServiceTicket).filter_by(ticket_number="TKT-2024-0002").first()
    if not ticket2:
        ticket2 = ServiceTicket(
            ticket_number="TKT-2024-0002",
            title="Network Switch — Intermittent Packet Loss",
            description=(
                "Users on Floor 5 are experiencing intermittent network drops every 30-60 minutes. "
                "Issue started after power outage last Friday. Switch (AST-SW-001) is operational "
                "but logs may show errors."
            ),
            customer_id=customer1.id,
            site_id=site1.id,
            asset_id=asset_sw1.id,
            category=TicketCategory.network,
            priority=TicketPriority.critical,
            status=TicketStatus.new,
            response_due=utcnow() - timedelta(hours=2),  # Overdue for demo
        )
        db.add(ticket2)
        db.flush()

        db.add(TicketEvent(
            ticket_id=ticket2.id,
            actor_name="Dana Dispatcher",
            event_type="created",
            detail="Ticket created. Customer reported intermittent packet loss after power outage.",
        ))

    ticket3 = db.query(ServiceTicket).filter_by(ticket_number="TKT-2024-0003").first()
    if not ticket3:
        ticket3 = ServiceTicket(
            ticket_number="TKT-2024-0003",
            title="Access Control Card Reader Not Responding",
            description=(
                "The HID card reader on the server room door (AST-AC-001) stopped responding "
                "to staff cards this morning. Door cannot be opened with access cards. "
                "Emergency key access is available but needs urgent resolution."
            ),
            customer_id=customer2.id,
            site_id=site3.id,
            asset_id=asset_ac1.id,
            category=TicketCategory.access_control,
            priority=TicketPriority.critical,
            status=TicketStatus.assigned,
            technician_id=tech2.id,
            response_due=utcnow() + timedelta(hours=2),
        )
        db.add(ticket3)
        db.flush()

        db.add(TicketEvent(
            ticket_id=ticket3.id,
            actor_name="Dana Dispatcher",
            event_type="created",
            detail="Ticket created. Server room access control failure.",
        ))
        db.add(TicketEvent(
            ticket_id=ticket3.id,
            actor_name="Dana Dispatcher",
            event_type="assigned",
            detail="Assigned to Priya Nair (EMP-002).",
        ))

    ticket4 = db.query(ServiceTicket).filter_by(ticket_number="TKT-2024-0004").first()
    if not ticket4:
        ticket4 = ServiceTicket(
            ticket_number="TKT-2024-0004",
            title="Warehouse PTZ Camera Intermittent Connection",
            description=(
                "The PTZ camera at the warehouse gate (AST-CAM-002) keeps disconnecting from "
                "the NVR. Connection drops every few hours. Firmware may need update."
            ),
            customer_id=customer3.id,
            site_id=site4.id,
            asset_id=asset_cam2.id,
            category=TicketCategory.cctv,
            priority=TicketPriority.medium,
            status=TicketStatus.resolved,
            technician_id=tech1.id,
            resolution_notes="Updated camera firmware to v2.800.17. Connection stable after 24h observation. Root cause: memory leak in previous firmware version.",
            closed_at=utcnow() - timedelta(days=2),
        )
        db.add(ticket4)
        db.flush()

        db.add(TicketEvent(
            ticket_id=ticket4.id,
            actor_name="Dana Dispatcher",
            event_type="created",
            detail="Ticket created.",
        ))
        db.add(TicketEvent(
            ticket_id=ticket4.id,
            actor_name="Ibrahim Al-Rashidi",
            event_type="note",
            detail="Checked NVR logs — disconnection pattern every 4-6 hours. Manufacturer advisory mentions firmware v2.800.16 memory leak. Upgrading firmware.",
        ))
        db.add(TicketEvent(
            ticket_id=ticket4.id,
            actor_name="Ibrahim Al-Rashidi",
            event_type="status_change",
            detail="Status changed to Resolved. Firmware updated. Camera stable.",
        ))

    db.flush()

    # ── AMC Contracts ────────────────────────────────────────────────────────
    contract1 = db.query(AMCContract).filter_by(contract_number="AMC-2024-001").first()
    if not contract1:
        contract1 = AMCContract(
            contract_number="AMC-2024-001",
            customer_id=customer1.id,
            start_date=utcnow() - timedelta(days=180),
            end_date=utcnow() + timedelta(days=25),  # Expiring soon — dashboard alert
            status=ContractStatus.expiring_soon,
            maintenance_frequency_days=90,
            notes="Full CCTV and networking AMC. 4 visits per year.",
        )
        db.add(contract1)
        db.flush()
        contract1.assets.append(asset_cam1)
        contract1.assets.append(asset_nvr1)
        contract1.assets.append(asset_sw1)

    contract2 = db.query(AMCContract).filter_by(contract_number="AMC-2024-002").first()
    if not contract2:
        contract2 = AMCContract(
            contract_number="AMC-2024-002",
            customer_id=customer2.id,
            start_date=utcnow() - timedelta(days=30),
            end_date=utcnow() + timedelta(days=335),
            status=ContractStatus.active,
            maintenance_frequency_days=90,
            notes="Server room, access control and CCTV. Quarterly visits.",
        )
        db.add(contract2)
        db.flush()
        contract2.assets.append(asset_srv1)
        contract2.assets.append(asset_ac1)

    db.flush()

    # ── Maintenance Visits ────────────────────────────────────────────────────
    mv1 = db.query(MaintenanceVisit).filter_by(
        contract_id=contract1.id, scheduled_date=utcnow().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=20)
    ).first() if contract1 else None

    if not mv1 and contract1:
        mv1 = MaintenanceVisit(
            contract_id=contract1.id,
            customer_id=customer1.id,
            site_id=site1.id,
            technician_id=tech1.id,
            scheduled_date=utcnow() + timedelta(days=20),
            maintenance_type="preventive",
            status=MaintenanceStatus.scheduled,
            checklist='["Inspect all cameras","Check NVR storage","Clean camera lenses","Test PoE injectors","Verify recording schedules"]',
            notes="Quarterly preventive maintenance — Q1 2025.",
        )
        db.add(mv1)

    mv2 = db.query(MaintenanceVisit).filter_by(
        contract_id=contract2.id if contract2 else None
    ).first()

    if not mv2 and contract2:
        mv2 = MaintenanceVisit(
            contract_id=contract2.id,
            customer_id=customer2.id,
            site_id=site3.id,
            technician_id=tech2.id,
            scheduled_date=utcnow() + timedelta(days=45),
            maintenance_type="preventive",
            status=MaintenanceStatus.scheduled,
            checklist='["Inspect server room UPS","Check server health metrics","Test access control cards","Review CCTV coverage"]',
        )
        db.add(mv2)

    # A completed past visit
    mv3_exists = db.query(MaintenanceVisit).filter_by(
        customer_id=customer1.id, status="completed"
    ).first()
    if not mv3_exists and contract1:
        mv3 = MaintenanceVisit(
            contract_id=contract1.id,
            customer_id=customer1.id,
            site_id=site1.id,
            technician_id=tech1.id,
            scheduled_date=utcnow() - timedelta(days=90),
            maintenance_type="preventive",
            status=MaintenanceStatus.completed,
            checklist='["Inspect all cameras","Check NVR storage","Clean camera lenses"]',
            findings="All cameras operational. NVR storage at 68%. Cleaned camera 3 lens (dust). Recommended storage expansion within 6 months.",
            work_performed="Cleaned camera lenses. Verified recording schedules. Updated NVR firmware.",
            completed_at=utcnow() - timedelta(days=89),
        )
        db.add(mv3)

    db.commit()
    print("[Seed] Demo data verified/created successfully.")
