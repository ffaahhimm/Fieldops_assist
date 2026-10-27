"""Contract schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ContractCreate(BaseModel):
    contract_number: str
    customer_id: int
    start_date: datetime
    end_date: datetime
    maintenance_frequency_days: int = 90
    notes: Optional[str] = None
    asset_ids: Optional[List[int]] = None

class ContractUpdate(BaseModel):
    end_date: Optional[datetime] = None
    maintenance_frequency_days: Optional[int] = None
    notes: Optional[str] = None
    asset_ids: Optional[List[int]] = None

class ContractOut(BaseModel):
    id: int
    contract_number: str
    customer_id: int
    start_date: datetime
    end_date: datetime
    status: str
    maintenance_frequency_days: int
    notes: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
