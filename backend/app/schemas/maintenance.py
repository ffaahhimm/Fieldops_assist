"""Maintenance visit schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class MaintenanceVisitCreate(BaseModel):
    contract_id: Optional[int] = None
    customer_id: int
    site_id: Optional[int] = None
    asset_id: Optional[int] = None
    technician_id: Optional[int] = None
    scheduled_date: datetime
    maintenance_type: str = "preventive"
    checklist: Optional[str] = None
    notes: Optional[str] = None

class MaintenanceVisitUpdate(BaseModel):
    technician_id: Optional[int] = None
    scheduled_date: Optional[datetime] = None
    status: Optional[str] = None
    checklist: Optional[str] = None
    findings: Optional[str] = None
    work_performed: Optional[str] = None
    notes: Optional[str] = None

class MaintenanceVisitOut(BaseModel):
    id: int
    contract_id: Optional[int]
    customer_id: int
    site_id: Optional[int]
    asset_id: Optional[int]
    technician_id: Optional[int]
    scheduled_date: datetime
    maintenance_type: str
    status: str
    checklist: Optional[str]
    findings: Optional[str]
    work_performed: Optional[str]
    completed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
