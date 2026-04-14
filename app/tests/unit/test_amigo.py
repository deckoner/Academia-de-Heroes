import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from app.models import Usuario, Amigo
from datetime import date


@pytest.fixture
def usuario_a(db):
    """Usuario de prueba A."""
    user = User.objects.create_user(username="user_a", password="pass123")
    return Usuario.objects.create(
        user=user,
        DNI="11111111A",
        email="usera@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )


@pytest.fixture
def usuario_b(db):
    """Usuario de prueba B."""
    user = User.objects.create_user(username="user_b", password="pass123")
    return Usuario.objects.create(
        user=user,
        DNI="22222222B",
        email="userb@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )


@pytest.fixture
def usuario_c(db):
    """Usuario de prueba C."""
    user = User.objects.create_user(username="user_c", password="pass123")
    return Usuario.objects.create(
        user=user,
        DNI="33333333C",
        email="userc@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )


@pytest.mark.django_db
class TestAmigoModel:
    """Tests del modelo Amigo."""

    def test_crear_amistad(self, usuario_a, usuario_b):
        """Se puede crear una relación de amistad."""
        amigo = Amigo.objects.agregar_amigo(usuario_a, usuario_b)
        assert amigo.estado == Amigo.Estado.PENDIENTE
        assert amigo.id_usuario == usuario_a
        assert amigo.id_amigo == usuario_b

    def test_no_puede_agregarse_a_si_mismo(self, usuario_a):
        """No se puede agregar uno mismo como amigo."""
        with pytest.raises(ValidationError):
            Amigo.objects.agregar_amigo(usuario_a, usuario_a)

    def test_no_puede_ser_amigo_dos_veces(self, usuario_a, usuario_b):
        """No se puede agregar dos veces al mismo amigo (si ya es amigo)."""
        Amigo.objects.create(
            id_usuario=usuario_a, id_amigo=usuario_b, estado=Amigo.Estado.ACEPTADA
        )
        with pytest.raises(ValidationError):
            Amigo.objects.agregar_amigo(usuario_a, usuario_b)


@pytest.mark.django_db
class TestAmigoManager:
    """Tests del manager de Amigo."""

    def test_son_amigos(self, usuario_a, usuario_b):
        """Verifica si dos usuarios son amigos."""
        assert not Amigo.objects.son_amigos(usuario_a, usuario_b)
        Amigo.objects.create(
            id_usuario=usuario_a, id_amigo=usuario_b, estado=Amigo.Estado.ACEPTADA
        )
        assert Amigo.objects.son_amigos(usuario_a, usuario_b)
        assert Amigo.objects.son_amigos(usuario_b, usuario_a)

    def test_tiene_solicitud_pendiente(self, usuario_a, usuario_b):
        """Verifica si hay solicitud pendiente."""
        assert not Amigo.objects.tiene_solicitud_pendiente(usuario_a, usuario_b)

        Amigo.objects.create(
            id_usuario=usuario_a, id_amigo=usuario_b, estado=Amigo.Estado.PENDIENTE
        )

        solicitud = Amigo.objects.tiene_solicitud_pendiente(usuario_a, usuario_b)
        assert solicitud is not None

        solicitud_inv = Amigo.objects.tiene_solicitud_pendiente(usuario_b, usuario_a)
        assert solicitud_inv is not None

    def test_listar_amigos(self, usuario_a, usuario_b, usuario_c):
        """Lista los amigos aceptados de un usuario."""
        Amigo.objects.create(
            id_usuario=usuario_a, id_amigo=usuario_b, estado=Amigo.Estado.ACEPTADA
        )
        Amigo.objects.create(
            id_usuario=usuario_c, id_amigo=usuario_a, estado=Amigo.Estado.ACEPTADA
        )
        Amigo.objects.create(
            id_usuario=usuario_a, id_amigo=usuario_c, estado=Amigo.Estado.PENDIENTE
        )

        amigos = Amigo.objects.listar_amigos(usuario_a)
        assert amigos.count() == 2

    def test_listar_solicitudes_pendientes(self, usuario_a, usuario_b, usuario_c):
        """Lista las solicitudes pendientes recibidas."""
        Amigo.objects.create(
            id_usuario=usuario_b, id_amigo=usuario_a, estado=Amigo.Estado.PENDIENTE
        )
        Amigo.objects.create(
            id_usuario=usuario_c, id_amigo=usuario_a, estado=Amigo.Estado.PENDIENTE
        )
        Amigo.objects.create(
            id_usuario=usuario_a, id_amigo=usuario_b, estado=Amigo.Estado.ACEPTADA
        )

        pendientes = Amigo.objects.listar_solicitudes_pendientes(usuario_a)
        assert pendientes.count() == 2

    def test_listar_solicitudes_enviadas(self, usuario_a, usuario_b, usuario_c):
        """Lista las solicitudes enviadas por el usuario."""
        Amigo.objects.create(
            id_usuario=usuario_a, id_amigo=usuario_b, estado=Amigo.Estado.PENDIENTE
        )
        Amigo.objects.create(
            id_usuario=usuario_a, id_amigo=usuario_c, estado=Amigo.Estado.PENDIENTE
        )
        Amigo.objects.create(
            id_usuario=usuario_b, id_amigo=usuario_a, estado=Amigo.Estado.PENDIENTE
        )

        enviadas = Amigo.objects.listar_solicitudes_enviadas(usuario_a)
        assert enviadas.count() == 2


@pytest.mark.django_db
class TestAceptacionAutomatica:
    """Tests de aceptación automática de solicitudes."""

    def test_aceptacion_automatica_cuando_existe_solicitud_inversa(
        self, usuario_a, usuario_b
    ):
        """Si ya existe solicitud pendiente y se envía otra, se acepta automáticamente."""
        Amigo.objects.create(
            id_usuario=usuario_a, id_amigo=usuario_b, estado=Amigo.Estado.PENDIENTE
        )

        resultado = Amigo.objects.agregar_amigo(usuario_b, usuario_a)

        assert resultado.estado == Amigo.Estado.ACEPTADA

        solicitudes_aceptadas = Amigo.objects.filter(estado=Amigo.Estado.ACEPTADA)
        assert solicitudes_aceptadas.count() == 1

    def test_no_se_crea_duplicado_al_aceptar(self, usuario_a, usuario_b):
        """Al aceptar automáticamente no se crea un duplicado."""
        Amigo.objects.create(
            id_usuario=usuario_a, id_amigo=usuario_b, estado=Amigo.Estado.PENDIENTE
        )

        Amigo.objects.agregar_amigo(usuario_b, usuario_a)

        total = Amigo.objects.filter(
            models.Q(id_usuario=usuario_a, id_amigo=usuario_b)
            | models.Q(id_usuario=usuario_b, id_amigo=usuario_a)
        ).count()

        assert total == 1


from django.db import models
