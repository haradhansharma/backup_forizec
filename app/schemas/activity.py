# app/schemas/activity.py
from pydantic import BaseModel, ConfigDict, constr
from typing import Optional
from datetime import datetime


class ActivityLogCreate(BaseModel):
    procedure_id: int
    description: Optional[str] = None
    performed_by: Optional[constr(max_length=100)] = None  # type: ignore
    outcome: Optional[constr(max_length=100)] = None  # type: ignore

    model_config = ConfigDict(from_attributes=True)


class ActivityLogOut(ActivityLogCreate):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
