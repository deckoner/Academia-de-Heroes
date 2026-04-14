import pytest
from django.test import Client
from app.models import Personaje


@pytest.mark.django_db
class TestListaPersonajes:
    """Tests de la lista de personajes."""

    def test_lista_carga(self, client):
        """La página de lista de personajes carga."""
        response = client.get("/personajes/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestCrearPersonaje:
    """Tests de creación de personajes."""

    def test_formulario_carga(self, client):
        """El formulario de crear personaje carga."""
        response = client.get("/personajes/crear/")
        assert response.status_code == 200
        assert "Crear Nuevo Heroe" in response.content.decode()

    def test_crear_guerrero(self, client):
        """Se puede crear un guerrero."""
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

    def test_crear_mago(self, client):
        """Se puede crear un mago."""
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
