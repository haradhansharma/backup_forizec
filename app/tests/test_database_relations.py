# app/tests/test_database_relations.py
# Test database relationships and constraints.

import pytest
import datetime
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from app.models.core_models import (
    Service, Policy, Procedure, ChecklistItem, Risk, ActivityLog,
    User, Document, ComplianceSchedule, PolicyAcceptance, ProcedureAcceptance,
    UserInvitation, Reminder
)
from app.models.enums import (
    UserRoleEnum, ComplienceStatusEnum, TaskStatusEnum, PriorityEnum, ReminderTypeEnum
)

# ---- Helpers -----------

async def create_user(async_session, email="user@exmples.com", role=UserRoleEnum.USER):
    user = User(email=email, hashed_password = 'hashedpw', first_name = "Test", last_name="User", role=role)
    async_session.add(user)
    await async_session.flush()
    return user

async def create_service(async_session, name = "IT Service"):
    service = Service(name=name, description="IT Governance")
    async_session.add(service)
    await async_session.flush()
    return service

# --- tests ---


@pytest.mark.asyncio
async def test_service_policy_relationship(async_session: AsyncSession):
    service = await create_service(async_session)
    policy = Policy(service_id=service.id, title="Policy A", description="Test Policy")
    async_session.add(policy)
    await async_session.commit()

    # version one by adding lazy in model
    await async_session.refresh(service)    
    assert len(service.policies) == 1
    assert service.policies[0].title == "Policy A"
    
    # version two by overriding lazy of model
    # service_with_policies = await async_session.scalar(
    #     select(Service).options(selectinload(Service.policies)).where(Service.id == service.id)
    # )
    # assert len(service_with_policies.policies) == 1
    # assert service_with_policies.policies[0].title == "Policy A"
    

@pytest.mark.asyncio 
async def test_policy_procedure_relationship(async_session: AsyncSession):
    service = await create_service(async_session)
    policy = Policy(service_id=service.id, title="Policy B", description="Has Procedure") 
    procedure = Procedure(policy=policy, title="Procedure 1", path="/proc1")
    async_session.add_all([policy, procedure])
    await async_session.commit()

    # option 1
    # await async_session.refresh(policy)
    # assert len(policy.procedures) == 1
    # assert policy.procedures[0].title == "Procedure 1"
    # assert procedure.policy.title == "Policy B"
    
    
    # option2 Query with explicit selectinload to override lazy
    service_with_policies = await async_session.scalar(
        select(Service)
        .options(selectinload(Service.policies).selectinload(Policy.procedures))
        .where(Service.id == service.id)
    )

    # Assertions
    assert len(service_with_policies.policies) == 1 # type: ignore
    loaded_policy = service_with_policies.policies[0] # type: ignore
    assert loaded_policy.title == "Policy B"
    assert len(loaded_policy.procedures) == 1
    assert loaded_policy.procedures[0].title == "Procedure 1"
    
@pytest.mark.asyncio 
async def test_procedure_checklist_and_activities(async_session: AsyncSession):
    service = await create_service(async_session)
    policy = Policy(service_id=service.id, title="Policy C")
    procedure = Procedure(policy=policy, title="Procedure 2")
    checklist = ChecklistItem(procedure=procedure, description="Step 1")
    activity = ActivityLog(procedure=procedure, description="Did Something", performed_by="tester")
    async_session.add_all([policy, procedure, checklist, activity])
    await async_session.commit()

    await async_session.refresh(procedure)
    assert procedure.checklist_items[0].description=="Step 1"
    assert procedure.activities[0].performed_by=="tester"


@pytest.mark.asyncio 
async def test_user_and_documents(async_session: AsyncSession):
    user = await create_user(async_session)
    doc = Document(filename="file.txt", original_filename="orig.txt", file_path="/tmp/file.txt", user=user)
    async_session.add(doc)
    await async_session.commit()

    await async_session.refresh(user)
    assert user.documents[0].filename == "file.txt"
    assert doc.user.email == "user@exmples.com"
    
@pytest.mark.asyncio 
async def test_complience_schedule_and_aasignment(async_session: AsyncSession):
    user = await create_user(async_session, email="user2@example.com")    
    schedule = ComplianceSchedule(
        title="Do Task",
        description="Complete Complience",
        due_date = date.today() + timedelta(days=7),
        assigned_user = user,
        priority = PriorityEnum.HIGH,

    )
    async_session.add(schedule)
    await async_session.commit()

    
    await async_session.refresh(user)
    assert user.assigned_schedules[0].title == "Do Task"
    assert schedule.priority == PriorityEnum.HIGH # type: ignore
    
@pytest.mark.asyncio 
async def test_acceptance(async_session: AsyncSession):
    user = await create_user(async_session, email="user3@example.com")   
    service = await create_service(async_session, name="IT Service 2") 
    policy = Policy(service_id = service.id, title="Acceptance Policy")
    procedure = Procedure(policy=policy, title="Acceptance Procedure")

    pa = PolicyAcceptance(policy=policy, user=user, accepted=True)
    pra = ProcedureAcceptance(procedure=procedure, user=user,accepted=False)
    async_session.add_all([policy, procedure, pa, pra])
    await async_session.commit()

    await async_session.refresh(user)
    assert user.policy_acceptances[0].accepted is True
    assert user.procedure_acceptances[0].accepted is False

    
@pytest.mark.asyncio 
async def test_user_invitation(async_session: AsyncSession):
    inviter = await create_user(async_session, email="inviter@example.com", role=UserRoleEnum.OWNER)
    invite = UserInvitation(email="invitee@example.com", inviter=inviter, token="abc123",expires_at=datetime.datetime.now(datetime.timezone.utc))
    async_session.add(invite)
    await async_session.commit()

    await async_session.refresh(inviter)
    assert inviter.invitations_sent[0].email == "invitee@example.com"
    
@pytest.mark.asyncio 
async def test_reminder(async_session: AsyncSession):
    user = await create_user(async_session, email="user4@example.com")   
    reminder = Reminder(user=user, title="Check Policy", message="Review Policy", reminder_type = ReminderTypeEnum.POLICY_REVIEW, due_date = datetime.datetime.now(datetime.timezone.utc))
    async_session.add(reminder)
    await async_session.commit()

    await async_session.refresh(user)
    assert user.reminders[0].title == "Check Policy"
    assert user.email == "user4@example.com"
    
@pytest.mark.asyncio 
async def test_cascade_delete_policy_removes_procedures(async_session: AsyncSession):
    service = await create_service(async_session, name="IT service 3")
    policy = Policy(service=service, title="Policy Cascade")
    procedure = Procedure(policy=policy, title="Cascade procedure")
    async_session.add(policy)
    await async_session.commit()

    policy_id, proc_id = policy.id, procedure.id
    await async_session.delete(policy)
    await async_session.commit()

    # Policy gone
    result = await async_session.execute(select(Policy).where(Policy.id==policy_id))
    assert result.scalar_one_or_none() is None
    
    # Procedure also gone
    result = await async_session.execute(select(Procedure).where(Procedure.id == proc_id))
    assert result.scalar_one_or_none() is None
    
@pytest.mark.asyncio 
async def test_cascade_delete_procedure_removes_checklist(async_session: AsyncSession):
    service = await create_service(async_session, name="IT service 4")
    policy = Policy(service=service, title="Policy checklist Cascade")
    procedure = Procedure(policy=policy, title="Pro checklist Cascade")
    checklist = ChecklistItem(procedure=procedure, description="step")
    async_session.add_all([policy,procedure,checklist])
    await async_session.commit()

    checklist_id = checklist.id
    await async_session.delete(procedure)
    await async_session.commit()

    # Policy gone
    result = await async_session.execute(select(ChecklistItem).where(ChecklistItem.id==checklist_id))
    assert result.scalar_one_or_none() is None
    
@pytest.mark.asyncio 
async def test_cascade_delete_user_removes_documents(async_session:AsyncSession):
    user = await create_user(async_session, email="user5@example.com")   
    doc = Document(filename="a.txt", original_filename = "a.txt", file_path = '/temp/a.txt', user = user)
    async_session.add(doc)
    await async_session.commit()

    doc_id = doc.id
    await async_session.delete(user)
    await async_session.commit()

    result = await async_session.execute(select(Document).where(Document.id==doc_id))
    assert result.scalar_one_or_none() is None 
    

@pytest.mark.asyncio 
async def test_enum_presistence_policy_status_and_priority(async_session: AsyncSession):
    service = await create_service(async_session, name="IT service 5")
    policy = Policy(
        service=service,
        title="Enum Policy",
        status=ComplienceStatusEnum.REVIEWED,
        priority=PriorityEnum.CRITICAL

    )
    async_session.add(policy)
    await async_session.commit()

    result = await async_session.execute(select(Policy).where(Policy.id==policy.id))
    fetched = result.scalar_one()
    assert fetched.status == ComplienceStatusEnum.REVIEWED # type: ignore
    assert fetched.priority == PriorityEnum.CRITICAL # type: ignore

@pytest.mark.asyncio 
async def test_enum_presistence_schedule_status_and_priority(async_session: AsyncSession):
    user = await create_user(async_session, email="user6@example.com")   
    schedule = ComplianceSchedule(
        title = "Enum Schedule",
        description="Chek Enums",
        due_date = date.today(),
        assigned_user = user,
        status = TaskStatusEnum.IN_PROGRESS,
        priority = PriorityEnum.LOW
    )
    async_session.add(schedule)
    await async_session.commit()

    result = await async_session.execute(select(ComplianceSchedule).where(ComplianceSchedule.id == schedule.id))
    fetched = result.scalar_one()
    assert fetched.status == TaskStatusEnum.IN_PROGRESS # type: ignore
    assert fetched.priority == PriorityEnum.LOW # type: ignore
    
@pytest.mark.asyncio 
async def test_bidirectional_policy_risk_navigation(async_session: AsyncSession):
    service = await create_service(async_session, name="IT service 6")
    policy = Policy(service=service, title="Policy BiDir")
    risk = Risk(related_policy=policy, event="Cyber Attack")
    async_session.add_all([policy, risk])
    await async_session.commit()

    # FOrward: Policy to Risk
    await async_session.refresh(policy)
    assert policy.risks[0].event == "Cyber Attack"
    
    # Backward Risk to policy
    await async_session.refresh(risk) 
    assert risk.related_policy.title == "Policy BiDir"
    
@pytest.mark.asyncio 
async def test_bidirectional_user_document_navigation(async_session: AsyncSession):
    user = await create_user(async_session, email="user7@example.com")   
    doc = Document(
        filename = "doc.pdf",
        original_filename = "doc.pdf",
        file_path = "/tmp/doc.pdf",
        user = user
    )
    async_session.add(doc)
    await async_session.commit()

    # Forward: User to document
    await async_session.refresh(user)
    assert user.documents[0].filename == "doc.pdf"
    
    # Backward Document to user
    await async_session.refresh(doc)
    assert doc.user.email == "user7@example.com"
    

# # one to many
# @pytest.mark.asyncio
# async def test_user_post_relationship(async_session: AsyncSession):
#     user = User(username="testuser", email="testuser@example.com")
#     async_session.add(user)
#     await async_session.flush()

#     post = Post(title="Test Post", content="This is a test post.", owner_id=user.id)
#     async_session.add(post)
#     await async_session.commit()

#     await async_session.refresh(user)
#     assert len(user.posts) == 1
#     assert user.posts[0].title == "Test Post"


# # one to many with comments
# @pytest.mark.asyncio
# async def test_post_comments_relationship(async_session: AsyncSession):
#     user = User(username="commenter", email="commenter@testuser.com")
#     post = Post(title="Another Post", content="Content here.", user=user)
#     comment1 = Comment(content="First comment", post=post, user=user)
#     comment2 = Comment(content="Second comment", post=post, user=user)

#     async_session.add_all([user, post, comment1, comment2])
#     await async_session.commit()

#     await async_session.refresh(post)
#     assert len(post.comments) == 2
#     assert {c.content for c in post.comments} == {"First comment", "Second comment"}


# # many to many
# @pytest.mark.asyncio
# async def test_user_roles_relationship(async_session: AsyncSession):
#     user = User(username="roleuser", email="roleuser@example.com")
#     role_admin = Role(name="admin")
#     role_editor = Role(name="editor")
#     user.roles.extend([role_admin, role_editor])

#     async_session.add(user)
#     await async_session.commit()

#     await async_session.refresh(user)
#     assert {r.name for r in user.roles} == {"admin", "editor"}
