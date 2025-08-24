# app/schemas/compliance.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from app.models.enums import TaskStatusEnum, PriorityEnum

class ComplianceScheduleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: date
    assigned_to: Optional[int] = None
    priority: Optional[PriorityEnum] = PriorityEnum.MID
    related_policy_id: Optional[int] = None
    related_procedure_id: Optional[int] = None

class ComplianceScheduleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[int] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    completed_at: Optional[datetime] = None

class ComplianceScheduleOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: date
    assigned_to: Optional[int] = None
    status: TaskStatusEnum
    priority: PriorityEnum
    created_at: datetime
    completed_at: Optional[datetime] = None
    related_policy_id: Optional[int] = None
    related_procedure_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class PolicyAcceptanceCreate(BaseModel):
    policy_id: int
    accepted: bool = False
    comments: Optional[str] = None

class PolicyAcceptanceOut(BaseModel):
    id: int
    policy_id: int
    user_id: int
    accepted_at: datetime
    accepted: bool
    comments: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ProcedureAcceptanceCreate(BaseModel):
    procedure_id: int
    accepted: bool = False
    comments: Optional[str] = None

class ProcedureAcceptanceOut(BaseModel):
    id: int
    procedure_id: int
    user_id: int
    accepted_at: datetime
    accepted: bool
    comments: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)