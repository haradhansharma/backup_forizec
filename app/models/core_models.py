# app/models/core_models.py
import datetime
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SAEnum
from .enums import UserRoleEnum, ComplienceStatusEnum, TaskStatusEnum, PriorityEnum, ReminderTypeEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
from passlib.hash import bcrypt

'''
set index=True on ForeignKey columns for performance optimization on lookups and joins. improve query performance. policy_id, procedure_id, service_id, uploaded_by, assigned_to, user_id, invited_by.
added risks relationships on Pilicy and Procedure models for bi-directional access to risks.
added missing back_populates/relationships sides(esp. on User, Risk, Document, acceptances, schedule, reminders) for ORM integrity and easier navigation.
added cascade="all, delete-orphan" to relationships to ensure related records are cleaned up when a parent is deleted.
Consider composite indexes if query by multiple columns concucurrently (e.g., (policy_id, status)), but only add after profiling actual query patterns.
when serializing nested objects, avoid lazy loading loops; use selectinload or joinedload in queries to avoid n+1 query issues.
'''


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    policies = relationship("Policy", back_populates="service", cascade="all, delete-orphan", lazy="selectin")


class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    number = Column(String)
    description = Column(Text)
    priority = Column(SAEnum(PriorityEnum, native_enum=False), default=PriorityEnum.MID)
    status = Column(
        SAEnum(ComplienceStatusEnum, native_enum=False), default=ComplienceStatusEnum.PENDING
    )
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    service = relationship("Service", back_populates="policies", lazy="joined")
    procedures = relationship("Procedure", back_populates="policy", cascade="all, delete-orphan", lazy="selectin")
    documents = relationship("Document", back_populates="policy", cascade="all, delete-orphan", lazy="selectin")
    acceptances = relationship(
        "PolicyAcceptance", back_populates="policy", cascade="all, delete-orphan", lazy="selectin"
    )

    # Link to Risks:
    risks = relationship("Risk", back_populates="related_policy", cascade="all, delete-orphan", lazy="selectin")


class Procedure(Base):
    __tablename__ = "procedures"
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    path = Column(String)
    version = Column(String)
    priority = Column(SAEnum(PriorityEnum, native_enum=False), default=PriorityEnum.MID)
    status = Column(
        SAEnum(ComplienceStatusEnum, native_enum=False), default=ComplienceStatusEnum.PENDING
    )
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    policy = relationship("Policy", back_populates="procedures", lazy="joined")
    checklist_items = relationship(
        "ChecklistItem", back_populates="procedure", cascade="all, delete-orphan", lazy="selectin"
    )
    activities = relationship(
        "ActivityLog", back_populates="procedure", cascade="all, delete-orphan", lazy="selectin"
    )
    documents = relationship("Document", back_populates="procedure", cascade="all, delete-orphan", lazy="selectin")
    acceptances = relationship(
        "ProcedureAcceptance", back_populates="procedure", cascade="all, delete-orphan", lazy="selectin"
    )
    # Link to Risks:
    risks = relationship("Risk", back_populates="related_procedure", cascade="all, delete-orphan", lazy="selectin")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    id = Column(Integer, primary_key=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)
    # ca be implemented later if needed
    # is_completed = Column(Boolean, default=False)
    # completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    procedure = relationship("Procedure", back_populates="checklist_items", lazy="joined")


class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True, index=True)
    date_raised = Column(Date)
    raised_by = Column(String)
    risk_category = Column(String)
    event = Column(Text)
    cause = Column(Text)
    consequence = Column(Text)
    likelihood = Column(String)
    consequence_rating = Column(String)  # renamed to avoid collision with `consequence`
    risk_rating = Column(String)
    action = Column(Text)
    plan = Column(Text)
    risk_owner = Column(String)
    resolve_by = Column(Date)
    method = Column(Text)
    progress_compliance_reporting = Column(Text)
    status = Column(String)
    email_subject = Column(String)
    email_body = Column(Text)

    related_policy_id = Column(Integer, ForeignKey("policies.id"), index=True)
    related_procedure_id = Column(Integer, ForeignKey("procedures.id"), index=True)

    related_policy = relationship("Policy", back_populates="risks", lazy="joined")
    related_procedure = relationship("Procedure", back_populates="risks", lazy="joined")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False, index=True)
    description = Column(Text)
    performed_by = Column(String(100))
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    outcome = Column(String(100))

    # Relationship to procedure
    procedure = relationship("Procedure", back_populates="activities", lazy="joined")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    role = Column(SAEnum(UserRoleEnum, native_enum=False), default=UserRoleEnum.USER)
    team = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    last_login = Column(DateTime)

    # backref relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    policy_acceptances = relationship(
        "PolicyAcceptance", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    procedure_acceptances = relationship(
        "ProcedureAcceptance", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    invitations_sent = relationship(
        "UserInvitation", back_populates="inviter", cascade="all, delete-orphan", lazy="selectin"
    )
    assigned_schedules = relationship(
        "ComplianceSchedule", back_populates="assigned_user", cascade="all, delete-orphan", lazy="selectin"
    )
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.hashed_password)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    uploaded_by = Column(Integer, ForeignKey("users.id"), index=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    # Relationships to policies/procedures
    policy_id = Column(Integer, ForeignKey("policies.id"), index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), index=True)

    policy = relationship("Policy", back_populates="documents", lazy="joined")
    procedure = relationship("Procedure", back_populates="documents", lazy="joined")
    user = relationship("User", back_populates="documents", lazy="joined")


class ComplianceSchedule(Base):
    __tablename__ = "compliance_schedule"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(Date, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(SAEnum(TaskStatusEnum, native_enum=False), default=TaskStatusEnum.PENDING)
    priority = Column(SAEnum(PriorityEnum, native_enum=False), default=PriorityEnum.MID)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    completed_at = Column(DateTime)

    # Relationships
    related_policy_id = Column(Integer, ForeignKey("policies.id"), index=True)
    related_procedure_id = Column(Integer, ForeignKey("procedures.id"), index=True)

    assigned_user = relationship("User", back_populates="assigned_schedules", lazy="joined")


class PolicyAcceptance(Base):
    __tablename__ = "policy_acceptances"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    accepted_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    accepted = Column(Boolean, default=False)
    comments = Column(Text)

    policy = relationship("Policy", back_populates="acceptances", lazy="joined")
    user = relationship("User", back_populates="policy_acceptances", lazy="joined")


class ProcedureAcceptance(Base):
    __tablename__ = "procedure_acceptances"

    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    accepted_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    accepted = Column(Boolean, default=False)
    comments = Column(Text)

    procedure = relationship("Procedure", back_populates="acceptances", lazy="joined")
    user = relationship("User", back_populates="procedure_acceptances", lazy="joined")


class UserInvitation(Base):
    __tablename__ = "user_invitations"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    role = Column(SAEnum(UserRoleEnum, native_enum=False), default=UserRoleEnum.USER)
    team = Column(String(100))
    invited_by = Column(Integer, ForeignKey("users.id"), index=True)
    invited_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    accepted = Column(Boolean, default=False)
    accepted_at = Column(DateTime)

    inviter = relationship("User", back_populates="invitations_sent", foreign_keys=[invited_by], lazy="joined")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text)
    reminder_type = Column(String(50))  # task_due, policy_review, etc.
    priority = Column(SAEnum(ReminderTypeEnum, native_enum=False), default=ReminderTypeEnum.NONE)
    due_date = Column(DateTime, nullable=False)
    sent_at = Column(DateTime)
    read_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="reminders", lazy="joined")
