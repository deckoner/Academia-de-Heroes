import pytest
from django.test.utils import setup_test_environment, teardown_test_environment
from playwright.sync_api import Browser
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session", autouse=True)
def django_test_environment():
    setup_test_environment()
    yield
    teardown_test_environment()


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
