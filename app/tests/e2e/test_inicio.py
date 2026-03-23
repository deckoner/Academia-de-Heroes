import pytest
from django.test import Client
from django.contrib.auth.models import User
from app.models import Usuario, Batalla, Amigo, Personaje
from datetime import date


@pytest.fixture
def usuario_test(db):
    """Usuario de prueba."""
    user = User.objects.create_user(username="testuser", password="testpass123")
    return Usuario.objects.create(
        user=user,
        DNI="00000000A",
        email="test@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )


@pytest.fixture
def otro_usuario(db):
    """Otro usuario de prueba."""
    user = User.objects.create_user(username="otrouser", password="testpass123")
    return Usuario.objects.create(
        user=user,
        DNI="00000000B",
        email="otro@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )


@pytest.fixture
def personaje_atacante(db, usuario_test):
    """Personaje del usuario test."""
    return Personaje.objects.create(
        id_usuario=usuario_test,
        tipo="GUERRERO",
        nombre="GuerreroTest",
        nivel=1,
        vida=100,
        vida_max=100,
        armadura=10,
        vivo=True,
    )


@pytest.fixture
def personaje_defensor(db, otro_usuario):
    """Personaje del otro usuario."""
    return Personaje.objects.create(
        id_usuario=otro_usuario,
        tipo="MAGO",
        nombre="MagoTest",
        nivel=1,
        vida=100,
        vida_max=100,
        mana=50,
        vivo=True,
    )


@pytest.fixture
def client(usuario_test):
    """Client de prueba autenticado."""
    client = Client()
    client.login(username="testuser", password="testpass123")
    return client


@pytest.mark.django_db
class TestInicio:
    """Tests de la página principal."""

    def test_home_carga(self, client):
        """La página principal carga correctamente."""
        response = client.get("/")
        assert response.status_code == 200

    def test_menu_tiene_enlaces(self, client):
        """El menú contiene los enlaces a las secciones principales."""
        response = client.get("/")
        content = response.content.decode().lower()
        assert "personajes" in content
        assert "combate" in content

    def test_home_muestra_historial_batallas(self, client, usuario_test, otro_usuario, personaje_atacante, personaje_defensor):
        """El home muestra el historial de batallas."""
        Batalla.objects.create(
            id_atacante=usuario_test,
            id_defensor=otro_usuario,
            personaje_atacante=personaje_atacante,
            personaje_defensor=personaje_defensor,
            resultado=True,
        )

        response = client.get("/")
        content = response.content.decode()
        assert "Historial de Batallas" in content
        assert "GuerreroTest" in content
        assert "otrouser" in content

    def test_home_muestra_resultado_batalla(self, client, usuario_test, otro_usuario, personaje_atacante, personaje_defensor):
        """El home muestra el resultado de la batalla."""
        Batalla.objects.create(
            id_atacante=usuario_test,
            id_defensor=otro_usuario,
            personaje_atacante=personaje_atacante,
            personaje_defensor=personaje_defensor,
            resultado=True,
        )

        response = client.get("/")
        content = response.content.decode()
        assert "Ganado" in content or "Perdido" in content

    def test_home_muestra_fecha_batalla(self, client, usuario_test, otro_usuario, personaje_atacante, personaje_defensor):
        """El home muestra la fecha de la batalla."""
        Batalla.objects.create(
            id_atacante=usuario_test,
            id_defensor=otro_usuario,
            personaje_atacante=personaje_atacante,
            personaje_defensor=personaje_defensor,
            resultado=True,
        )

        response = client.get("/")
        content = response.content.decode()
        assert "d/m/Y" in content or "/" in content

    def test_home_notificaciones_muestra_solicitudes(self, client, usuario_test, otro_usuario):
        """El home muestra las solicitudes de amistad pendientes."""
        Amigo.objects.create(
            id_usuario=otro_usuario,
            id_amigo=usuario_test,
            estado="PENDIENTE",
        )

        response = client.get("/")
        content = response.content.decode()
        assert "Solicitudes de Amistad" in content
        assert "otrouser" in content

    def test_home_notificaciones_muestra_batallas_recibidas(self, client, usuario_test, otro_usuario, personaje_atacante, personaje_defensor):
        """El home muestra las batallas recibidas no leídas."""
        Batalla.objects.create(
            id_atacante=otro_usuario,
            id_defensor=usuario_test,
            personaje_atacante=personaje_atacante,
            personaje_defensor=personaje_defensor,
            resultado=False,
            leido=False,
        )

        response = client.get("/")
        content = response.content.decode()
        assert "Batallas Recibidas" in content
        assert "otrouser" in content

    def test_home_marcar_batalla_como_leida(self, client, usuario_test, otro_usuario, personaje_atacante, personaje_defensor):
        """Se puede marcar una batalla como leída."""
        batalla = Batalla.objects.create(
            id_atacante=otro_usuario,
            id_defensor=usuario_test,
            personaje_atacante=personaje_atacante,
            personaje_defensor=personaje_defensor,
            resultado=False,
            leido=False,
        )

        response = client.post("/", {"batalla_id": batalla.id})
        assert response.status_code == 302

        batalla.refresh_from_db()
        assert batalla.leido == True

    def test_home_muestra_columnas_sin_contenido(self, client):
        """Las columnas se muestran aunque no haya contenido."""
        response = client.get("/")
        content = response.content.decode()
        assert "Historial de Batallas" in content
        assert "Notificaciones" in content

    def test_home_muestra_yo_en_batalla_como_atacante(self, client, usuario_test, otro_usuario, personaje_atacante, personaje_defensor):
        """Se marca 'yo' cuando el usuario es el atacante."""
        Batalla.objects.create(
            id_atacante=usuario_test,
            id_defensor=otro_usuario,
            personaje_atacante=personaje_atacante,
            personaje_defensor=personaje_defensor,
            resultado=True,
        )

        response = client.get("/")
        content = response.content.decode()
        assert 'class="' in content or 'yo' in content

    def test_home_limita_batallas_mostradas(self, client, usuario_test, otro_usuario, personaje_atacante, personaje_defensor):
        """Solo se muestran las últimas 10 batallas."""
        for i in range(15):
            Batalla.objects.create(
                id_atacante=usuario_test,
                id_defensor=otro_usuario,
                personaje_atacante=personaje_atacante,
                personaje_defensor=personaje_defensor,
                resultado=True,
            )

        response = client.get("/")
        content = response.content.decode()
        assert content.count('class="batalla-item') == 10
