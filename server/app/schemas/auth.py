from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone_number: str | None = None
    locale: str = "en"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    email: str | None = None


class AuthUser(BaseModel):
    user_id: UUID
    email: EmailStr
    full_name: str
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    locale: str = "en"
    is_admin: bool = False

    class Config:
        from_attributes = True
