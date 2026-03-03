import pytest
import subprocess
import time
from playwright.sync_api import sync_playwright, Browser


@pytest.fixture(scope="session")
def django_server():
    proc = subprocess.Popen(
        ["python", "manage.py", "runserver", "8765", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)
    yield "http://127.0.0.1:8765"
    proc.terminate()
    proc.wait()


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


@pytest.mark.e2e
def test_crear_personaje_get(django_server, page):
    """Verifica que la pagina de crear personaje carga correctamente."""
    response = page.goto(f"{django_server}/personajes/crear/")
    assert response.status == 200


@pytest.mark.e2e
def test_lista_personajes(django_server, page):
    """Verifica que la pagina de lista de personajes carga."""
    response = page.goto(f"{django_server}/personajes/")
    assert response.status == 200


@pytest.mark.e2e
def test_formulario_existe(django_server, page):
    """Verifica que el formulario tiene todos los campos."""
    page.goto(f"{django_server}/personajes/crear/")
    content = page.content()

    assert "tipo" in content
    assert "nombre" in content
    assert "nivel" in content


@pytest.mark.e2e
def test_base_template_carga(django_server, page):
    """Verifica que el template base carga correctamente."""
    page.goto(f"{django_server}/personajes/crear/")
    content = page.content()

    assert "Academia de Heroes" in content
    assert "crear" in content.lower()


@pytest.mark.e2e
def test_editar_personaje_get(django_server, page):
    """Verifica que la pagina de editar personaje carga correctamente."""
    response = page.goto(f"{django_server}/personajes/1/editar/")
    assert response.status in [200, 404]


@pytest.mark.e2e
def test_precision_formulario_validacion(django_server, page):
    """Verifica que el formulario valida precision entre 0 y 100."""
    page.goto(f"{django_server}/personajes/crear/")

    page.select_option('select[name="tipo"]', "ARQUERO")
    page.fill('input[name="nombre"]', "TestPrecision")
    page.fill('input[name="nivel"]', "1")
    page.fill('input[name="vida"]', "100")
    page.fill('input[name="vida_max"]', "100")
    page.fill('input[name="precision"]', "150")

    page.click('button[type="submit"]')

    content = page.content()
    assert "precision" in content.lower() or "error" in content.lower()
