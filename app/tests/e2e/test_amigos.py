import pytest
from django.test import Client
from django.contrib.auth.models import User
from django.db import models
from app.models import Usuario, Amigo
from datetime import date


@pytest.fixture
def usuario1(db):
    """Usuario de prueba 1."""
    user = User.objects.create_user(username="usuario1", password="password123")
    return Usuario.objects.create(
        user=user,
        DNI="11111111A",
        email="usuario1@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )


@pytest.fixture
def usuario2(db):
    """Usuario de prueba 2."""
    user = User.objects.create_user(username="usuario2", password="password123")
    return Usuario.objects.create(
        user=user,
        DNI="22222222B",
        email="usuario2@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )


@pytest.fixture
def usuario3(db):
    """Usuario de prueba 3."""
    user = User.objects.create_user(username="usuario3", password="password123")
    return Usuario.objects.create(
        user=user,
        DNI="33333333C",
        email="usuario3@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )


@pytest.fixture
def client1(db, usuario1):
    """Cliente autenticado como usuario1."""
    client = Client()
    client.login(username="usuario1", password="password123")
    return client


@pytest.fixture
def client2(db, usuario2):
    """Cliente autenticado como usuario2."""
    client = Client()
    client.login(username="usuario2", password="password123")
    return client


@pytest.mark.django_db
class TestListaAmigos:
    """Tests de la lista de amigos."""

    def test_lista_amigos_carga(self, client1):
        """La página de lista de amigos carga."""
        response = client1.get("/amigos/")
        assert response.status_code == 200

    def test_lista_amigos_vacia(self, client1):
        """La página muestra estado vacío cuando no hay amigos."""
        response = client1.get("/amigos/")
        content = response.content.decode()
        assert "No tienes amigos" in content


@pytest.mark.django_db
class TestBuscarAmigos:
    """Tests de búsqueda de amigos."""

    def test_buscar_amigos_carga(self, client1):
        """La página de buscar amigos carga."""
        response = client1.get("/amigos/buscar/")
        assert response.status_code == 200

    def test_buscar_usuarios(self, client1, usuario2, usuario3):
        """Se pueden buscar usuarios."""
        response = client1.get("/amigos/buscar/?q=usuario")
        assert response.status_code == 200
        content = response.content.decode()
        assert "usuario2" in content
        assert "usuario3" in content

    def test_buscar_no_muestra_propio_usuario(self, client1, usuario1, usuario2):
        """El propio usuario no aparece en la búsqueda."""
        response = client1.get("/amigos/buscar/?q=usuario1")
        assert response.status_code == 200
        content = response.content.decode()
        assert (
            "usuario1" not in content
            or "usuario1" in content
            and "Agregar" not in content
        )


@pytest.mark.django_db
class TestEnviarSolicitud:
    """Tests de envío de solicitudes de amistad."""

    def test_enviar_solicitud(self, client1, usuario1, usuario2):
        """Se puede enviar una solicitud de amistad."""
        response = client1.post(f"/amigos/enviar/{usuario2.id}/")
        assert response.status_code == 302
        assert "/amigos/" in response.url

        solicitud = Amigo.objects.filter(
            id_usuario=usuario1, id_amigo=usuario2, estado="PENDIENTE"
        ).exists()
        assert solicitud

    def test_no_puede_enviarse_a_si_mismo(self, client1, usuario1):
        """No se puede enviar solicitud a uno mismo."""
        response = client1.post(f"/amigos/enviar/{usuario1.id}/", follow=True)
        assert response.status_code == 200
        content = response.content.decode()
        assert "No puedes" in content or "mismo" in content


@pytest.mark.django_db
class TestAceptarRechazarSolicitud:
    """Tests de aceptación y rechazo de solicitudes."""

    def test_aceptar_solicitud(self, client1, client2, usuario1, usuario2):
        """Se puede aceptar una solicitud de amistad."""
        solicitud = Amigo.objects.create(
            id_usuario=usuario1, id_amigo=usuario2, estado="PENDIENTE"
        )

        response = client2.post(f"/amigos/aceptar/{solicitud.id}/")
        assert response.status_code == 302

        solicitud.refresh_from_db()
        assert solicitud.estado == "ACEPTADA"

    def test_rechazar_solicitud(self, client1, client2, usuario1, usuario2):
        """Se puede rechazar una solicitud de amistad."""
        solicitud = Amigo.objects.create(
            id_usuario=usuario1, id_amigo=usuario2, estado="PENDIENTE"
        )

        response = client2.post(f"/amigos/rechazar/{solicitud.id}/")
        assert response.status_code == 302

        solicitud.refresh_from_db()
        assert solicitud.estado == "RECHAZADA"


@pytest.mark.django_db
class TestAmistadBidireccional:
    """Tests de amistad automática cuando hay solicitud inversa."""

    def test_solicitud_inversa_se_acepta(self, client1, client2, usuario1, usuario2):
        """Si ya existe solicitud pendiente y se envía otra, se acepta automáticamente."""
        Amigo.objects.create(id_usuario=usuario1, id_amigo=usuario2, estado="PENDIENTE")

        response = client2.post(f"/amigos/enviar/{usuario1.id}/")
        assert response.status_code == 302

        solicitud = Amigo.objects.filter(
            models.Q(id_usuario=usuario1, id_amigo=usuario2)
            | models.Q(id_usuario=usuario2, id_amigo=usuario1),
            estado="ACEPTADA",
        ).exists()
        assert solicitud


@pytest.mark.django_db
class TestEliminarAmigo:
    """Tests de eliminación de amigos."""

    def test_eliminar_amigo(self, client1, usuario1, usuario2):
        """Se puede eliminar un amigo."""
        Amigo.objects.create(id_usuario=usuario1, id_amigo=usuario2, estado="ACEPTADA")

        amigo_id = Amigo.objects.first().id
        response = client1.post(f"/amigos/eliminar/{amigo_id}/")
        assert response.status_code == 302

        assert not Amigo.objects.filter(
            models.Q(id_usuario=usuario1, id_amigo=usuario2)
            | models.Q(id_usuario=usuario2, id_amigo=usuario1)
        ).exists()
