import pytest
import subprocess
import time
import os
import signal
from playwright.sync_api import sync_playwright, Page, Browser


@pytest.fixture(scope='session')
def django_server():
    proc = subprocess.Popen(
        ['python', 'manage.py', 'runserver', '8765', '--noreload'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)
    yield 'http://127.0.0.1:8765'
    proc.terminate()
    proc.wait()


@pytest.fixture(scope='session')
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


@pytest.mark.e2e
def test_home_page_loads(django_server, page):
    page.goto(f'{django_server}/')
    assert page.title() is not None
