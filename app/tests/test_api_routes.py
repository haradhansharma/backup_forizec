# app/tests/test_api_routes.py
# This file contains tests for the API routes of the FastAPI application.
import pytest

# Each tuple: (method, route, expected_status, content_type, expected_contents, payload, headers)
API_ROUTES = [
    ("GET", "/api/v1/user/me", 200, "application/json", ["username", "email", "id"], None, None),
    (
        "POST",
        "/api/v1/user/login",
        200,
        "application/json",
        ["access_token", "token_type"],
        {"username": "testuser", "password": "secret"},
        None,
    ),
    (
        "POST",
        "/api/v1/users",
        201,
        "application/json",
        ["id", "username", "email"],
        {"username": "newuser", "email": "new@example.com", "password": "secret"},
        None,
    ),
    (
        "PUT",
        "/api/v1/users/1",
        200,
        "application/json",
        ["id", "username", "email"],
        {"username": "updateduser"},
        {"Authorization": "Bearer faketoken"},
    ),
    (
        "PATCH",
        "/api/v1/users/1",
        200,
        "application/json",
        ["id", "username"],
        {"username": "patcheduser"},
        {"Authorization": "Bearer faketoken"},
    ),
    ("DELETE", "/api/v1/users/1", 204, None, [], None, {"Authorization": "Bearer faketoken"}),
    ("GET", "/api/v1/nonexistent", 404, "application/json", ["detail", "Not Found"], None, None),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method, route, expected_status, expected_content_type, expected_contents, payload, headers",
    API_ROUTES,
)
async def test_api_routes(
    client,
    method,
    route,
    expected_status,
    expected_content_type,
    expected_contents,
    payload,
    headers,
):
    request_func = getattr(client, method.lower())

    kwargs = {}
    if payload:
        kwargs["json"] = payload
    if headers:
        kwargs["headers"] = headers

    response = await request_func(route, **kwargs)

    # ✅ Status check
    assert (
        response.status_code == expected_status
    ), f"{method} {route} returned {response.status_code}, expected {expected_status}"

    # ✅ Content-Type check
    if expected_content_type:
        assert (
            expected_content_type in response.headers["content-type"]
        ), f"{route} returned wrong content-type {response.headers['content-type']}, expected {expected_content_type}"

    # ✅ Body content checks
    if expected_content_type and expected_status != 204:  # no body for 204
        data = response.json()
        for content in expected_contents:
            assert content in data, f"{route} missing expected content: {content}"
