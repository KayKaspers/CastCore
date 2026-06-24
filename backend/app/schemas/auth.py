"""Authentication schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LoginResponse(TokenPair):
    user: UserOut
