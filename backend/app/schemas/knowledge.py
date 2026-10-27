"""Knowledge document schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DocumentOut(BaseModel):
    id: int
    title: str
    category: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    error_message: Optional[str]
    chunk_count: int
    uploaded_at: datetime
    indexed_at: Optional[datetime]
    model_config = {"from_attributes": True}
