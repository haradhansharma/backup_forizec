# app/tests/test_html_routes.py
import pytest

HTML_ROUTES = [
    (
        "/",
        200,
        "text/html",
        ["<h1>Welcome to Forizec</h1>", "<title>Forizec</title>", "Forizec", "<footer>"],
    ),
    (
        "/about",
        200,
        "text/html",
        ["<h1>About Forizec</h1>", "<title>About</title>", "About", "<footer>"],
    ),
    (
        "/contact",
        200,
        "text/html",
        ["<h1>Contact Us</h1>", "<title>Contact</title>", "Contact", "<footer>"],
    ),
    ("/nonexistent", 404, "text/html", ["<h1>404 Not Found</h1>", "404", "Error", "<footer>"]),
    ("/forbidden", 403, "text/html", ["<h1>403 Forbidden</h1>", "403", "Forbidden", "<footer>"]),
    (
        "/internal-error",
        500,
        "text/html",
        ["<h1>500 Internal Server Error</h1>", "500", "Error", "<footer>"],
    ),
    # Add more HTML routes as needed
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route, expected_status, expected_content_type, expected_contents", HTML_ROUTES
)
async def test_html_routes(
    client, route, expected_status, expected_content_type, expected_contents
):
    response = await client.get(route)
    assert (
        response.status_code == expected_status
    ), f"{route} returned {response.status_code}, expected {expected_status}"
    assert (
        expected_content_type in response.headers["content-type"]
    ), f"{route} returned wrong content-type {response.headers['content-type']}, expected {expected_content_type}"
    for content in expected_contents:
        assert content in response.text, f"{route} missing expected content: {content}"


# Test various HTML routes of the FastAPI application.
