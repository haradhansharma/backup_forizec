# app/schemas/document.py
from pydantic import BaseModel, ConfigDict, constr
from typing import Optional
from datetime import datetime

class DocumentCreate(BaseModel):
    filename: constr(max_length=255) # type: ignore
    original_filename: constr(max_length=255) # type: ignore
    file_path: constr(max_length=500) # type: ignore
    file_size: int
    mime_type: constr(max_length=100) # type: ignore
    policy_id: Optional[int] = None
    procedure_id: Optional[int] = None

class DocumentOut(DocumentCreate):
    id: int
    uploaded_by: Optional[int] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)