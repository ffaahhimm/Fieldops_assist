"""Audit log schema."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AuditLogOut(BaseModel):
    id: int
    actor_name: str
    action: str
    resource_type: str
    resource_id: Optional[int]
    detail: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
