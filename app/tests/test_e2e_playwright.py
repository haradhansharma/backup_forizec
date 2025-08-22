# app/tests/test_e2e_playwright.py
# End-to-end tests using Playwright to simulate user interactions.

import pytest
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8017"

@pytest.mark.asyncio
async def test_homepage_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # visit homepage
        await page.goto(BASE_URL+"/")
        assert await page.title() == "Welcome to Forizec"
        assert "Welcome to Forizec" in await page.content()

        # click login link
        await page.click("text=Login")
        assert "/auth/login" in page.url

        await browser.close()

@pytest.mark.asyncio
async def test_login_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # visit login page
        await page.goto(BASE_URL+"/auth/login")
        assert "Login" in await page.title()

        # fill login form
        await page.fill("input[name='username']", "testuser")
        await page.fill("input[name='password']", "secret")
        await page.click("button[type='submit']")

        # assert redirection to dashboard
        assert "/dashboard" in page.url 
        assert "Welcome back, testuser" in await page.content()

        await browser.close()