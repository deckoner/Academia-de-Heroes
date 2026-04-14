import pytest
from django.test import Client
from django.contrib.auth.models import User
from app.models import Personaje, Usuario
from datetime import date


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
        user = User.objects.get(username="testuser")
        perfil = Usuario.objects.get(user=user)

        Personaje.objects.create(
            id_usuario=perfil,
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
        """Entrenar aumenta el nivel del personaje usando mercenarios."""
        user = User.objects.get(username="testuser")
        perfil = Usuario.objects.get(user=user)
        perfil.mercenarios = 1
        perfil.save()

        p = Personaje.objects.create(
            id_usuario=perfil,
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

        perfil.refresh_from_db()
        assert perfil.mercenarios == 0
