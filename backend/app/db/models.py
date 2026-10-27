"""
FieldOps Assist — SQLAlchemy ORM Models
All timestamps stored in UTC. Relationships defined with lazy='select' by default.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Float,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ─── Enumerations ─────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin = "admin"
    dispatcher = "dispatcher"
    technician = "technician"
    manager = "manager"


class AssetStatus(str, enum.Enum):
    operational = "operational"
    degraded = "degraded"
    offline = "offline"
    retired = "retired"
    unknown = "unknown"


class TicketPriority(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class TicketStatus(str, enum.Enum):
    new = "new"
    assigned = "assigned"
    in_progress = "in_progress"
    waiting_customer = "waiting_customer"
    resolved = "resolved"
    closed = "closed"


class TicketCategory(str, enum.Enum):
    network = "network"
    cctv = "cctv"
    hardware = "hardware"
    software = "software"
    access_control = "access_control"
    intercom = "intercom"
    maintenance = "maintenance"
    other = "other"


class ContractStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    expiring_soon = "expiring_soon"
    cancelled = "cancelled"
    pending = "pending"


class MaintenanceStatus(str, enum.Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    rescheduled = "rescheduled"
    cancelled = "cancelled"


class DocStatus(str, enum.Enum):
    pending = "pending"
    indexed = "indexed"
    failed = "failed"


# ─── Association tables ───────────────────────────────────────────────────────

contract_asset = Table(
    "contract_asset",
    Base.metadata,
    Column("contract_id", ForeignKey("amc_contracts.id"), primary_key=True),
    Column("asset_id", ForeignKey("assets.id"), primary_key=True),
)

technician_skill = Table(
    "technician_skill",
    Base.metadata,
    Column("technician_id", ForeignKey("technicians.id"), primary_key=True),
    Column("skill", String(100), primary_key=True),
)


# ─── Models ───────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False, default=UserRole.dispatcher
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    technician: Mapped[Optional["Technician"]] = relationship(back_populates="user", uselist=False)
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="actor")


class Technician(Base):
    __tablename__ = "technicians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[Optional["User"]] = relationship(back_populates="technician")
    tickets: Mapped[List["ServiceTicket"]] = relationship(back_populates="technician")
    maintenance_visits: Mapped[List["MaintenanceVisit"]] = relationship(back_populates="technician")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    sites: Mapped[List["Site"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    assets: Mapped[List["Asset"]] = relationship(back_populates="customer")
    tickets: Mapped[List["ServiceTicket"]] = relationship(back_populates="customer")
    contracts: Mapped[List["AMCContract"]] = relationship(back_populates="customer")


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    customer: Mapped["Customer"] = relationship(back_populates="sites")
    assets: Mapped[List["Asset"]] = relationship(back_populates="site")
    tickets: Mapped[List["ServiceTicket"]] = relationship(back_populates="site")
    maintenance_visits: Mapped[List["MaintenanceVisit"]] = relationship(back_populates="site")

    __table_args__ = (Index("ix_sites_customer_id", "customer_id"),)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_tag: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # cctv, network, computer…
    asset_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    site_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id"), nullable=True)
    installation_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    warranty_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_service_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_maintenance_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(AssetStatus, name="asset_status"), nullable=False, default=AssetStatus.operational
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    customer: Mapped["Customer"] = relationship(back_populates="assets")
    site: Mapped[Optional["Site"]] = relationship(back_populates="assets")
    tickets: Mapped[List["ServiceTicket"]] = relationship(back_populates="asset")
    contracts: Mapped[List["AMCContract"]] = relationship(
        secondary=contract_asset, back_populates="assets"
    )

    __table_args__ = (
        Index("ix_assets_customer_id", "customer_id"),
        Index("ix_assets_status", "status"),
    )


class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    site_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id"), nullable=True)
    asset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("assets.id"), nullable=True)
    category: Mapped[str] = mapped_column(
        Enum(TicketCategory, name="ticket_category"), nullable=False, default=TicketCategory.other
    )
    priority: Mapped[str] = mapped_column(
        Enum(TicketPriority, name="ticket_priority"), nullable=False, default=TicketPriority.medium
    )
    status: Mapped[str] = mapped_column(
        Enum(TicketStatus, name="ticket_status"), nullable=False, default=TicketStatus.new
    )
    technician_id: Mapped[Optional[int]] = mapped_column(ForeignKey("technicians.id"), nullable=True)
    response_due: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    customer: Mapped["Customer"] = relationship(back_populates="tickets")
    site: Mapped[Optional["Site"]] = relationship(back_populates="tickets")
    asset: Mapped[Optional["Asset"]] = relationship(back_populates="tickets")
    technician: Mapped[Optional["Technician"]] = relationship(back_populates="tickets")
    events: Mapped[List["TicketEvent"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", order_by="TicketEvent.created_at"
    )

    __table_args__ = (
        Index("ix_tickets_status", "status"),
        Index("ix_tickets_priority", "priority"),
        Index("ix_tickets_customer_id", "customer_id"),
    )


class TicketEvent(Base):
    __tablename__ = "ticket_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("service_tickets.id"), nullable=False)
    actor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_name: Mapped[str] = mapped_column(String(255), nullable=False, default="System")
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # created, status_change, note…
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    ticket: Mapped["ServiceTicket"] = relationship(back_populates="events")


class AMCContract(Base):
    __tablename__ = "amc_contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contract_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(ContractStatus, name="contract_status"), nullable=False, default=ContractStatus.active
    )
    maintenance_frequency_days: Mapped[int] = mapped_column(Integer, default=90)  # every N days
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    customer: Mapped["Customer"] = relationship(back_populates="contracts")
    assets: Mapped[List["Asset"]] = relationship(
        secondary=contract_asset, back_populates="contracts"
    )
    maintenance_visits: Mapped[List["MaintenanceVisit"]] = relationship(
        back_populates="contract", cascade="all, delete-orphan"
    )


class MaintenanceVisit(Base):
    __tablename__ = "maintenance_visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contract_id: Mapped[Optional[int]] = mapped_column(ForeignKey("amc_contracts.id"), nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    site_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id"), nullable=True)
    asset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("assets.id"), nullable=True)
    technician_id: Mapped[Optional[int]] = mapped_column(ForeignKey("technicians.id"), nullable=True)
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False, default="preventive")
    status: Mapped[str] = mapped_column(
        Enum(MaintenanceStatus, name="maintenance_status"),
        nullable=False,
        default=MaintenanceStatus.scheduled,
    )
    checklist: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    findings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    work_performed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    contract: Mapped[Optional["AMCContract"]] = relationship(back_populates="maintenance_visits")
    technician: Mapped[Optional["Technician"]] = relationship(back_populates="maintenance_visits")
    site: Mapped[Optional["Site"]] = relationship(back_populates="maintenance_visits")

    __table_args__ = (
        Index("ix_maintenance_visits_scheduled_date", "scheduled_date"),
        Index("ix_maintenance_visits_status", "status"),
    )


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="general")
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, txt, md
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        Enum(DocStatus, name="doc_status"), nullable=False, default=DocStatus.pending
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    chunks: Mapped[List["DocumentChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("knowledge_documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Store embedding as comma-separated floats; for production use pgvector or FAISS
    embedding_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")

    __table_args__ = (Index("ix_chunks_document_id", "document_id"),)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    actor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_name: Mapped[str] = mapped_column(String(255), nullable=False, default="System")
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    actor: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_resource_type", "resource_type"),
        Index("ix_audit_logs_created_at", "created_at"),
    )
