# app/schemas/policy.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from app.models.enums import PriorityEnum


class PolicyCreate(BaseModel):
    service_id: int
    title: str
    number: Optional[str] = None
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.MID
    implementation_date: Optional[date] = None


class PolicyOut(PolicyCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)