# app/schemas/risk.py 

from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class RiskCreate(BaseModel):
    date_raised: Optional[date] = None
    raised_by: str
    risk_category: str
    event: str
    cause: str
    consequence: str
    consequence_rating: str
    likelihood: str
    risk_rating: str
    action: str
    plan: str
    risk_owner: str
    resolve_by: Optional[date] = None
    method: str
    progress_compliance_reporting: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class RiskOut(RiskCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
