from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# =======================
# USUARIOS
# =======================

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str  # Necesario para registro

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # Opcional en updates

class UserResponse(UserBase):
    id: int
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}  # Antes era class Config

# Opcional: para login
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"