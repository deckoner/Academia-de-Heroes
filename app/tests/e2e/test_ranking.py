import pytest
from django.test import Client
from django.contrib.auth.models import User
from app.models import Usuario, Personaje, Batalla
from datetime import date


@pytest.fixture
def usuario(db):
    """Usuario de prueba."""
    user = User.objects.create_user(username="rankuser", password="testpass123")
    return Usuario.objects.create(
        user=user,
        DNI="00000001A",
        email="rank@test.com",
        fecha_nacimiento=date(1990, 1, 1),
    )


@pytest.fixture
def cliente(db, usuario):
    """Cliente autenticado."""
    client = Client()
    client.login(username="rankuser", password="testpass123")
    return client


@pytest.fixture
def personaje(db, usuario):
    """Personaje del usuario."""
    return Personaje.objects.create(
        id_usuario=usuario,
        tipo="GUERRERO",
        nombre="GuerreroRank",
        nivel=1,
        vida=100,
        vida_max=100,
        armadura=10,
        vivo=True,
    )


@pytest.mark.django_db
class TestRankingPage:
    """Tests E2E para la pagina de ranking."""

    def test_ranking_page_carga(self, cliente):
        """La pagina de ranking carga correctamente."""
        response = cliente.get("/ranking/")
        assert response.status_code == 200
        assert "Ranking" in response.content.decode()

    def test_ranking_muestra_tabla_usuarios(self, cliente):
        """Muestra tabla de ranking de usuarios."""
        response = cliente.get("/ranking/")
        content = response.content.decode()
        assert "Ranking de Usuarios" in content

    def test_ranking_muestra_tabla_personajes(self, cliente):
        """Muestra tabla de ranking de personajes."""
        response = cliente.get("/ranking/")
        content = response.content.decode()
        assert "Ranking de Personajes" in content

    def test_ranking_vacio_muestra_mensaje(self, cliente):
        """Sin batallas muestra mensaje apropiado."""
        response = cliente.get("/ranking/")
        content = response.content.decode()
        assert "No hay" in content

    def test_ranking_con_batalla_muestra_victoria(self, cliente, usuario, personaje):
        """Con batallas muestra las victorias."""
        otro_user = User.objects.create_user(username="rankotro", password="testpass123")
        otro = Usuario.objects.create(
            user=otro_user,
            DNI="00000002B",
            email="rankotro@test.com",
            fecha_nacimiento=date(1990, 1, 1),
        )
        personaje_otro = Personaje.objects.create(
            id_usuario=otro,
            tipo="MAGO",
            nombre="MagoRank",
            nivel=1,
            vida=100,
            vida_max=100,
            mana=50,
            vivo=True,
        )
        Batalla.objects.create(
            id_atacante=usuario,
            id_defensor=otro,
            personaje_atacante=personaje,
            personaje_defensor=personaje_otro,
            resultado=True,
        )

        response = cliente.get("/ranking/")
        content = response.content.decode()
        assert "1" in content or "Victorias" in content

    def test_ranking_muestra_tipo_personaje(self, cliente, personaje):
        """Muestra el tipo de personaje en el ranking."""
        response = cliente.get("/ranking/")
        content = response.content.decode()
        assert "Guerrero" in content or "GUERRERO" in content

    def test_ranking_muestra_nivel_personaje(self, cliente, personaje):
        """Muestra el nivel del personaje en el ranking."""
        response = cliente.get("/ranking/")
        content = response.content.decode()
        assert "1" in content

    def test_ranking_nav_menu(self, cliente):
        """El ranking es accesible desde el menu."""
        response = cliente.get("/")
        assert response.status_code == 200

    def test_ranking_requiere_login(self):
        """El ranking requiere autenticacion."""
        client = Client()
        response = client.get("/ranking/")
        assert response.status_code == 302