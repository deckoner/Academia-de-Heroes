import pytest
from playwright.sync_api import Browser
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    django_db_blocker.unblock()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser: Browser):
    page = browser.new_page()
    yield page
    page.close()
