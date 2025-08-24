# app/schemas/user.py

from pydantic import BaseModel, EmailStr, constr, ConfigDict
from typing import Optional
from app.models.enums import UserRoleEnum
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  # type: ignore
    first_name: Optional[constr(max_length=100)] = None  # type: ignore
    last_name: Optional[constr(max_length=100)] = None  # type: ignore
    role: UserRoleEnum = UserRoleEnum.USER
    team: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    team: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRoleEnum
    team: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserInvitationCreate(BaseModel):
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.USER
    team: Optional[str] = None


class UserInvitationOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRoleEnum
    team: Optional[str] = None
    invited_at: datetime
    expires_at: datetime
    accepted: bool
    accepted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
