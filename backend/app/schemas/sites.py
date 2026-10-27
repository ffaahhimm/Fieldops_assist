"""Site schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SiteCreate(BaseModel):
    customer_id: int
    name: str
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None

class SiteUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None

class SiteOut(BaseModel):
    id: int
    customer_id: int
    name: str
    address: Optional[str]
    contact_name: Optional[str]
    contact_phone: Optional[str]
    notes: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
