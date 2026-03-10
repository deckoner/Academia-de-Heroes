import pytest
from django.test import Client
from app.models import Personaje


@pytest.mark.django_db
class TestListaPersonajes:
    """Tests de la lista de personajes."""

    def test_lista_carga(self):
        """La página de lista de personajes carga."""
        client = Client()
        response = client.get("/personajes/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestCrearPersonaje:
    """Tests de creación de personajes."""

    def test_formulario_carga(self):
        """El formulario de crear personaje carga."""
        client = Client()
        response = client.get("/personajes/crear/")
        assert response.status_code == 200
        assert "Crear Nuevo Personaje" in response.content.decode()

    def test_crear_guerrero(self):
        """Se puede crear un guerrero."""
        client = Client()
        response = client.post(
            "/personajes/crear/",
            {
                "tipo": "GUERRERO",
                "nombre": "GuerreroPrueba",
                "nivel": 1,
                "vida": 100,
                "vida_max": 100,
                "armadura": 10,
            },
        )
        assert response.status_code == 302
        assert "/personajes/" in response.url

    def test_crear_mago(self):
        """Se puede crear un mago."""
        client = Client()
        response = client.post(
            "/personajes/crear/",
            {
                "tipo": "MAGO",
                "nombre": "MagoPrueba",
                "nivel": 1,
                "vida": 80,
                "vida_max": 80,
                "mana": 100,
            },
        )
        assert response.status_code == 302
        assert "/personajes/" in response.url
