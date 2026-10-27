"""Ticket and TicketEvent schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class TicketCreate(BaseModel):
    title: str
    description: str
    customer_id: int
    site_id: Optional[int] = None
    asset_id: Optional[int] = None
    category: str = "other"
    priority: str = "medium"
    technician_id: Optional[int] = None
    response_due: Optional[datetime] = None

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    technician_id: Optional[int] = None
    resolution_notes: Optional[str] = None
    response_due: Optional[datetime] = None

class TicketEventOut(BaseModel):
    id: int
    ticket_id: int
    actor_name: str
    event_type: str
    detail: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}

class TicketNoteCreate(BaseModel):
    event_type: str = "note"
    detail: str

class TicketOut(BaseModel):
    id: int
    ticket_number: str
    title: str
    description: str
    customer_id: int
    site_id: Optional[int]
    asset_id: Optional[int]
    category: str
    priority: str
    status: str
    technician_id: Optional[int]
    response_due: Optional[datetime]
    resolution_notes: Optional[str]
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
