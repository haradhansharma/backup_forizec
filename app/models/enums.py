# app/models/enums.py
import enum

"""
enums keep in a single files for easier management and consistency across the app.
Pydantic serializes enums as strings by default, so we inherit from str to ensure. Better in JSON responses.
SQLALchemy Enum will write the string values to the DB (DB-Agnostic).
"""


class UserRoleEnum(str, enum.Enum):
    OWNER = "owner"
    USER = "user"


class ComplienceStatusEnum(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    IMPLEMENTED = "implemented"
    ACTIONED = "actioned"
    LIVE = "live"


class TaskStatusEnum(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PriorityEnum(str, enum.Enum):
    LOW = "low"
    MID = "mid"
    HIGH = "high"
    CRITICAL = "critical"
