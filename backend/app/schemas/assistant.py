"""AI assistant schemas."""
from typing import List, Optional, Any
from pydantic import BaseModel

class AssistantQuery(BaseModel):
    question: str
    context: Optional[str] = None  # e.g. "asset_tag=AST-CAM-001, ticket=TKT-2024-0001"

class AssistantResponse(BaseModel):
    answer: str
    sources: List[Any]
    retrieval_only: bool
    llm_available: bool
