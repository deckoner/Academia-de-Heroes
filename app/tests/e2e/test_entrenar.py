import pytest
from django.test import Client
from app.models import Personaje


@pytest.mark.django_db
class TestEntrenar:
    """Tests de la página de entrenamiento."""

    def test_entrenar_sin_personajes(self, client):
        """Si no hay personajes muestra mensaje."""
        response = client.get("/entrenar/")
        assert response.status_code == 200
        assert "No hay" in response.content.decode()
        assert "disponibles" in response.content.decode()

    def test_entrenar_muestra_personajes(self, client):
        """Muestra los personajes disponibles."""
        Personaje.objects.create(
            tipo="GUERRERO",
            nombre="G1",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )

        response = client.get("/entrenar/")
        assert response.status_code == 200
        assert "G1" in response.content.decode()

    def test_entrenar_aumenta_nivel(self, client):
        """Entrenar aumenta el Nivel del personaje."""
        p = Personaje.objects.create(
            tipo="GUERRERO",
            nombre="G2",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )

        response = client.post(
            "/entrenar/",
            {
                "personaje_id": p.id,
            },
        )
        assert response.status_code == 302

        p.refresh_from_db()
        assert p.nivel == 2
