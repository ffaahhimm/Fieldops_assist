"""Asset schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AssetCreate(BaseModel):
    asset_tag: str
    name: str
    category: str
    asset_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    ip_address: Optional[str] = None
    customer_id: int
    site_id: Optional[int] = None
    installation_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    status: str = "operational"
    notes: Optional[str] = None

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    asset_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    ip_address: Optional[str] = None
    site_id: Optional[int] = None
    installation_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    last_service_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class AssetOut(BaseModel):
    id: int
    asset_tag: str
    name: str
    category: str
    asset_type: Optional[str]
    manufacturer: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    ip_address: Optional[str]
    customer_id: int
    site_id: Optional[int]
    installation_date: Optional[datetime]
    warranty_expiry: Optional[datetime]
    last_service_date: Optional[datetime]
    next_maintenance_date: Optional[datetime]
    status: str
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
