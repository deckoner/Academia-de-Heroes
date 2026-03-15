import pytest
from playwright.sync_api import Browser
from playwright.sync_api import sync_playwright
from django.test import Client
from django.contrib.auth.models import User
from app.models import Usuario
from datetime import date
import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture
def client():
    """Client de prueba autenticado."""
    client = Client()
    user = User.objects.create_user(username="testuser", password="testpass123")
    Usuario.objects.create(
        user=user,
        DNI="00000000A",
        email="test@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )
    client.login(username="testuser", password="testpass123")
    return client
