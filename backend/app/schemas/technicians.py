"""Technician schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TechnicianCreate(BaseModel):
    user_id: Optional[int] = None
    employee_id: str
    phone: Optional[str] = None
    is_available: bool = True
    notes: Optional[str] = None

class TechnicianUpdate(BaseModel):
    phone: Optional[str] = None
    is_available: Optional[bool] = None
    notes: Optional[str] = None

class TechnicianOut(BaseModel):
    id: int
    user_id: Optional[int]
    employee_id: str
    phone: Optional[str]
    is_available: bool
    notes: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
