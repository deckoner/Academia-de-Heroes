import pytest
from django.test import Client
from app.models import Personaje


@pytest.mark.django_db
class TestCombate:
    """Tests de la página de combate."""

    def test_combate_sin_personajes(self):
        """Si no hay personajes muestra mensaje."""
        client = Client()
        response = client.get("/combate/")
        assert response.status_code == 200
        assert "Se necesitan al menos dos personajes" in response.content.decode()

    def test_combate_muestra_formulario(self):
        """Con personajes muestra el formulario."""
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
        Personaje.objects.create(
            tipo="MAGO",
            nombre="M1",
            nivel=1,
            vida=80,
            vida_max=80,
            armadura=None,
            mana=50,
            precision=None,
        )

        client = Client()
        response = client.get("/combate/")
        assert response.status_code == 200
        assert "Atacante" in response.content.decode()
        assert "Defensor" in response.content.decode()
        assert "VS" in response.content.decode()

    def test_checkbox_guardar(self):
        """Tiene el checkbox para guardar."""
        Personaje.objects.create(
            tipo="GUERRERO",
            nombre="G2",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )
        Personaje.objects.create(
            tipo="ARQUERO",
            nombre="A1",
            nivel=1,
            vida=80,
            vida_max=80,
            armadura=None,
            mana=None,
            precision=80,
        )

        client = Client()
        response = client.get("/combate/")
        content = response.content.decode()
        assert "Guardar cambios en la base de datos" in content
        assert 'name="guardar"' in content

    def test_no_permite_mismo_personaje(self):
        """No permite seleccionar el mismo personaje."""
        p1 = Personaje.objects.create(
            tipo="GUERRERO",
            nombre="G3",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )

        client = Client()
        response = client.post(
            "/combate/",
            {
                "personaje1": str(p1.id),
                "personaje2": str(p1.id),
            },
        )
        assert response.status_code == 302
