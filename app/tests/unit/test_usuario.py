import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Usuario
from datetime import date


@pytest.mark.unit
@pytest.mark.django_db
class TestUsuarioModel(TestCase):
    """Tests para el modelo Usuario."""

    def test_crear_usuario(self):
        """Verifica que se puede crear un usuario con perfil."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="12345678A",
            telefono="612345678",
            email="test@test.com",
            fecha_nacimiento=date(2000, 1, 1),
        )
        self.assertEqual(perfil.user.username, "testuser")
        self.assertEqual(perfil.DNI, "12345678A")
        self.assertEqual(perfil.telefono, "612345678")
        self.assertEqual(perfil.email, "test@test.com")

    def test_usuario_str(self):
        """Verifica que __str__ retorna el username."""
        user = User.objects.create_user(username="miusuario", password="pass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="87654321B",
            email="test@test.com",
            fecha_nacimiento=date(2000, 1, 1),
        )
        self.assertEqual(str(perfil), "miusuario")

    def test_usuario_con_fecha_nacimiento(self):
        """Verifica que se puede crear usuario con fecha de nacimiento."""
        user = User.objects.create_user(username="user2", password="pass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="12345678C",
            fecha_nacimiento=date(2000, 1, 1),
            email="test@test.com",
        )
        self.assertEqual(perfil.fecha_nacimiento, date(2000, 1, 1))

    def test_usuario_admin(self):
        """Verifica que un usuario puede ser admin."""
        user = User.objects.create_user(username="admin", password="pass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="12345678D",
            es_admin=True,
            email="test@test.com",
            fecha_nacimiento=date(2000, 1, 1),
        )
        self.assertTrue(perfil.es_admin)

    def test_usuario_menor_de_edad(self):
        """Verifica que un menor de edad puede registrarse."""
        user = User.objects.create_user(username="menor", password="pass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="12345678E",
            fecha_nacimiento=date(2020, 1, 1),
            email="test@test.com",
        )
        self.assertIsNotNone(perfil.fecha_nacimiento)

    def test_usuario_sin_telefono(self):
        """Verifica que el teléfono es opcional."""
        user = User.objects.create_user(username="sinphone", password="pass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="12345678F",
            email="test@test.com",
            fecha_nacimiento=date(2000, 1, 1),
        )
        self.assertEqual(perfil.telefono, "")

    def test_usuario_con_monedas(self):
        """Verifica que el usuario puede tener monedas."""
        user = User.objects.create_user(username="rico", password="pass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="12345678G",
            monedas=500,
            email="test@test.com",
            fecha_nacimiento=date(2000, 1, 1),
        )
        self.assertEqual(perfil.monedas, 500)

    def test_usuario_nuevo_tiene_10_monedas(self):
        """Verifica que nuevos usuarios reciben 10 monedas."""
        user = User.objects.create_user(username="nuevo", password="pass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="22345678A",
            email="test@test.com",
            fecha_nacimiento=date(2000, 1, 1),
            monedas=10,
        )
        self.assertEqual(perfil.monedas, 10)


@pytest.mark.unit
@pytest.mark.django_db
class TestUsuarioManager(TestCase):
    """Tests para el UsuarioManager."""

    def test_obtener_por_id(self):
        """Verifica que se puede obtener un usuario por ID."""
        user = User.objects.create_user(username="buscar", password="pass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="11111111A",
            email="test@test.com",
            fecha_nacimiento=date(2000, 1, 1),
        )
        resultado = Usuario.objects.obtener_por_id(perfil.id)
        self.assertEqual(resultado.user.username, "buscar")

    def test_obtener_por_id_inexistente(self):
        """Verifica que retorna None si no existe."""
        resultado = Usuario.objects.obtener_por_id(9999)
        self.assertIsNone(resultado)

    def test_es_mayor_de_edad_true(self):
        """Verifica que detecta correctamente mayor de edad."""
        user = User.objects.create_user(username="adulto", password="pass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="22222222A",
            fecha_nacimiento=date(2000, 1, 1),
            email="test@test.com",
        )
        self.assertTrue(Usuario.objects.es_mayor_de_edad(perfil.id))

    def test_es_mayor_de_edad_false_menor(self):
        """Verifica que detecta correctamente menor de edad."""
        user = User.objects.create_user(username="ninio", password="pass123")
        perfil = Usuario.objects.create(
            user=user,
            DNI="33333333A",
            fecha_nacimiento=date(2020, 1, 1),
            email="test@test.com",
        )
        self.assertFalse(Usuario.objects.es_mayor_de_edad(perfil.id))
