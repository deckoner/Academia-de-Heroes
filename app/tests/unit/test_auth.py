import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from app.models import Usuario
from datetime import date


@pytest.mark.unit
@pytest.mark.django_db
class TestLoginView(TestCase):
    """Tests para la vista de login."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.perfil = Usuario.objects.create(
            user=self.user,
            DNI="12345678A",
            telefono="612345678",
            email="test@test.com",
            fecha_nacimiento=date(2000, 1, 1),
        )
        self.login_url = reverse("login")

    def test_login_get_muestra_formulario(self):
        """Verifica que el formulario de login se muestra."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.content.decode())
        self.assertIn("password", response.content.decode())

    def test_login_exitoso(self):
        """Verifica que el login funciona con credenciales correctas."""
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_login_password_incorrecto(self):
        """Verifica que muestra error con contraseña incorrecta."""
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("incorrectos", response.content.decode())

    def test_login_usuario_inexistente(self):
        """Verifica que muestra error con usuario inexistente."""
        response = self.client.post(
            self.login_url, {"username": "noexiste", "password": "pass123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("incorrectos", response.content.decode())

    def test_login_redirect_next(self):
        """Verifica que redirige a la página next."""
        response = self.client.post(
            self.login_url + "?next=" + reverse("combate"),
            {"username": "testuser", "password": "testpass123"},
        )
        self.assertRedirects(response, reverse("combate"))


@pytest.mark.unit
@pytest.mark.django_db
class TestRegisterView(TestCase):
    """Tests para la vista de registro."""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")

    def test_register_get_muestra_formulario(self):
        """Verifica que el formulario de registro se muestra."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.content.decode())
        self.assertIn("password", response.content.decode())

    def test_register_exitoso(self):
        """Verifica que el registro funciona correctamente."""
        response = self.client.post(
            self.register_url,
            {
                "username": "nuevouser",
                "password": "password123",
                "confirm_password": "password123",
                "dni": "12345678Z",
                "telefono": "612345679",
                "email": "nuevo@test.com",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="nuevouser").exists())
        self.assertTrue(Usuario.objects.filter(DNI="12345678Z").exists())

    def test_register_nuevo_usuario_recibe_10_monedass(self):
        """Verifica que nuevos usuarios reciben 10 monedas."""
        response = self.client.post(
            self.register_url,
            {
                "username": "nuevouser2",
                "password": "password123",
                "confirm_password": "password123",
                "dni": "22345678Z",
                "telefono": "612345679",
                "email": "nuevo2@test.com",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        usuario = Usuario.objects.get(user__username="nuevouser2")
        self.assertEqual(usuario.monedas, 10)

    def test_register_passwords_diferentes(self):
        """Verifica que las contraseñas diferentes muestran error."""
        response = self.client.post(
            self.register_url,
            {
                "username": "testuser2",
                "password": "pass123",
                "confirm_password": "pass456",
                "dni": "12345678Y",
                "email": "test2@test.com",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("coinciden", response.content.decode())

    def test_register_password_corta(self):
        """Verifica que contraseña corta muestra error."""
        response = self.client.post(
            self.register_url,
            {
                "username": "testuser3",
                "password": "123",
                "confirm_password": "123",
                "dni": "12345678X",
                "email": "test3@test.com",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("8 caracteres", response.content.decode())

    def test_register_usuario_existente(self):
        """Verifica que usuario existente muestra error."""
        User.objects.create_user(username="existe", password="password123")
        response = self.client.post(
            self.register_url,
            {
                "username": "existe",
                "password": "password123",
                "confirm_password": "password123",
                "dni": "11111111A",
                "email": "test@test.com",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("ya existe", response.content.decode())

    def test_register_dni_existente(self):
        """Verifica que DNI duplicado muestra error."""
        user = User.objects.create_user(username="user1", password="password123")
        Usuario.objects.create(
            user=user,
            DNI="11111111A",
            email="test@test.com",
            fecha_nacimiento=date(2000, 1, 1),
        )

        response = self.client.post(
            self.register_url,
            {
                "username": "user2",
                "password": "password123",
                "confirm_password": "password123",
                "dni": "11111111A",
                "email": "test2@test.com",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("DNI", response.content.decode())

    def test_register_dni_obligatorio(self):
        """Verifica que DNI obligatorio muestra error."""
        response = self.client.post(
            self.register_url,
            {
                "username": "testuser4",
                "password": "password123",
                "confirm_password": "password123",
                "email": "test4@test.com",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("DNI", response.content.decode())

    def test_register_email_obligatorio(self):
        """Verifica que email obligatorio muestra error."""
        response = self.client.post(
            self.register_url,
            {
                "username": "testuser5",
                "password": "password123",
                "confirm_password": "password123",
                "dni": "52345678A",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.content.decode())

    def test_register_fecha_nacimiento_obligatoria(self):
        """Verifica que fecha de nacimiento obligatoria muestra error."""
        response = self.client.post(
            self.register_url,
            {
                "username": "testuser6",
                "password": "password123",
                "confirm_password": "password123",
                "dni": "62345678A",
                "email": "test6@test.com",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("fecha", response.content.decode())

    def test_register_dni_formato_invalido(self):
        """Verifica que DNI con formato inválido muestra error."""
        response = self.client.post(
            self.register_url,
            {
                "username": "testuser7",
                "password": "password123",
                "confirm_password": "password123",
                "dni": "invalido",
                "email": "test7@test.com",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("DNI", response.content.decode())

    def test_register_telefono_invalido(self):
        """Verifica que teléfono inválido muestra error."""
        response = self.client.post(
            self.register_url,
            {
                "username": "testuser8",
                "password": "password123",
                "confirm_password": "password123",
                "dni": "82345678A",
                "telefono": "abc",
                "email": "test8@test.com",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("teléfono", response.content.decode())

    def test_register_email_formato_invalido(self):
        """Verifica que email con formato inválido muestra error."""
        response = self.client.post(
            self.register_url,
            {
                "username": "testuser9",
                "password": "password123",
                "confirm_password": "password123",
                "dni": "92345678A",
                "email": "noesemail",
                "fecha_nacimiento": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.content.decode())


@pytest.mark.unit
@pytest.mark.django_db
class TestLogoutView(TestCase):
    """Tests para la vista de logout."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.perfil = Usuario.objects.create(
            user=self.user,
            DNI="12345678A",
            email="test@test.com",
            fecha_nacimiento=date(2000, 1, 1),
        )

    def test_logout_cierra_sesion(self):
        """Verifica que el logout cierra la sesión."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
