# app/tests/test_root.py
# Test the root endpoint of the FastAPI application.
import pytest

@pytest.mark.asyncio
async def test_root_returns_html(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<h1>Welcome to Forizec</h1>" in response.text
