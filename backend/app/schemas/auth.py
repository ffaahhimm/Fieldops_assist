"""Auth schemas."""
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    model_config = {"from_attributes": True}
