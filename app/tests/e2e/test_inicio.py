import pytest
from django.test import Client


@pytest.mark.django_db
class TestInicio:
    """Tests de la página principal."""

    def test_home_carga(self):
        """La página principal carga correctamente."""
        client = Client()
        response = client.get("/")
        assert response.status_code == 200

    def test_menu_tiene_enlaces(self):
        """El menú contiene los enlaces a las secciones principales."""
        client = Client()
        response = client.get("/")
        content = response.content.decode().lower()
        assert "personajes" in content
        assert "combate" in content
