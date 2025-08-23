# app/tests/test_database_relations.py
# Test database relationships and constraints.

import pytest
from sqlalchemy.exc.asyncio import AsyncSession

# from app.models import User, Post  # Example models


# one to many
@pytest.mark.asyncio
async def test_user_post_relationship(async_session: AsyncSession):
    user = User(username="testuser", email="testuser@example.com")
    async_session.add(user)
    await async_session.flush()

    post = Post(title="Test Post", content="This is a test post.", owner_id=user.id)
    async_session.add(post)
    await async_session.commit()

    await async_session.refresh(user)
    assert len(user.posts) == 1
    assert user.posts[0].title == "Test Post"


# one to many with comments
@pytest.mark.asyncio
async def test_post_comments_relationship(async_session: AsyncSession):
    user = User(username="commenter", email="commenter@testuser.com")
    post = Post(title="Another Post", content="Content here.", user=user)
    comment1 = Comment(content="First comment", post=post, user=user)
    comment2 = Comment(content="Second comment", post=post, user=user)

    async_session.add_all([user, post, comment1, comment2])
    await async_session.commit()

    await async_session.refresh(post)
    assert len(post.comments) == 2
    assert {c.content for c in post.comments} == {"First comment", "Second comment"}


# many to many
@pytest.mark.asyncio
async def test_user_roles_relationship(async_session: AsyncSession):
    user = User(username="roleuser", email="roleuser@example.com")
    role_admin = Role(name="admin")
    role_editor = Role(name="editor")
    user.roles.extend([role_admin, role_editor])

    async_session.add(user)
    await async_session.commit()

    await async_session.refresh(user)
    assert {r.name for r in user.roles} == {"admin", "editor"}
