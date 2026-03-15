import pytest
from django.test import Client
from django.contrib.auth.models import User
from app.models import Personaje, Usuario
from datetime import date


@pytest.mark.django_db
class TestCombate:
    """Tests de la página de combate."""

    def test_combate_sin_personajes(self, client):
        """Si no hay personajes muestra mensaje."""
        response = client.get("/combate/")
        assert response.status_code == 200
        assert "Se necesitan al menos dos personajes" in response.content.decode()

    def test_combate_muestra_formulario(self, client):
        """Con personajes muestra el formulario."""
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
        Personaje.objects.create(
            id_usuario=perfil,
            tipo="MAGO",
            nombre="M1",
            nivel=1,
            vida=80,
            vida_max=80,
            armadura=None,
            mana=50,
            precision=None,
        )

        response = client.get("/combate/")
        assert response.status_code == 200
        assert "⚔️" in response.content.decode()
        assert "Simulación" in response.content.decode()

    def test_no_permite_mismo_personaje(self, client):
        """No permite seleccionar el mismo personaje."""
        user = User.objects.get(username="testuser")
        perfil = Usuario.objects.get(user=user)
        
        p1 = Personaje.objects.create(
            id_usuario=perfil,
            tipo="GUERRERO",
            nombre="G3",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )

        response = client.post(
            "/combate/",
            {
                "personaje1": str(p1.id),
                "personaje2": str(p1.id),
            },
        )
        assert response.status_code == 302
