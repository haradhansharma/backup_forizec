# app/schemas/procedure.py
from pydantic import BaseModel, ConfigDict  
from typing import Optional
from datetime import date
from app.models.enums import PriorityEnum


class ProcedureCreate(BaseModel):
    policy_id: int
    title: str
    path: Optional[str] = None
    version: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.MID
    implementation_date: Optional[date] = None


class ProcedureOut(ProcedureCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)