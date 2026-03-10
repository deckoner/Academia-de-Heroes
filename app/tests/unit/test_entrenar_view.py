import pytest
from django.test import Client
from django.urls import reverse
from app.models import Personaje


@pytest.mark.unit
@pytest.mark.django_db(transaction=True)
class TestEntrenarPersonajeView:
    """Tests para la vista de entrenar personajes."""

    def test_entrenar_vista_get(self):
        """Verifica que la vista GET muestra los personajes."""
        client = Client()

        p = Personaje.objects.create(
            tipo="GUERRERO",
            nombre="GuerreroTestEntrenar",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )

        response = client.get(reverse("entrenar"))

        assert response.status_code == 200
        assert "personajes" in response.context
        personajes = response.context["personajes"]
        assert any(pp.nombre == "GuerreroTestEntrenar" for pp in personajes)

    def test_entrenar_vista_sin_personajes(self):
        """Verifica que la vista muestra mensaje cuando no hay personajes."""
        client = Client()

        response = client.get(reverse("entrenar"))

        assert response.status_code == 200

    def test_entrenar_post_exitoso(self):
        """Verifica que entrenar un personaje aumenta su nivel."""
        client = Client()

        p = Personaje.objects.create(
            tipo="MAGO",
            nombre="MagoEntrenarTest",
            nivel=1,
            vida=50,
            vida_max=50,
            armadura=None,
            mana=100,
            precision=None,
        )

        vida_max_original = p.vida_max

        response = client.post(reverse("entrenar"), {"personaje_id": p.id})

        p.refresh_from_db()

        assert p.nivel == 2
        assert p.vida_max == vida_max_original + 10

    def test_entrenar_post_personaje_inexistente(self):
        """Verifica el error al entrenar un personaje inexistente."""
        client = Client()

        response = client.post(reverse("entrenar"), {"personaje_id": 9999})

        assert response.status_code == 302
        assert response.url == reverse("entrenar")

    def test_entrenar_post_sin_seleccionar(self):
        """Verifica el error al no seleccionar personaje."""
        client = Client()

        response = client.post(reverse("entrenar"), {})

        assert response.status_code == 302
        assert response.url == reverse("entrenar")

    def test_entrenar_multiple_niveles(self):
        """Verifica que se puede entrenar varias veces."""
        client = Client()

        p = Personaje.objects.create(
            tipo="ARQUERO",
            nombre="ArqueroMultiTest",
            nivel=1,
            vida=80,
            vida_max=80,
            armadura=None,
            mana=None,
            precision=90,
        )

        for i in range(3):
            client.post(reverse("entrenar"), {"personaje_id": p.id})
            p.refresh_from_db()

        assert p.nivel == 4
        assert p.vida_max == 110
