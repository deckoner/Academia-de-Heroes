import pytest
from django.test import Client
from django.contrib.auth.models import User
from app.models import Usuario
from datetime import date


@pytest.mark.django_db
class TestLoginE2E:
    """Tests E2E para el flujo de login."""

    def test_login_page_loads(self):
        """La página de login carga correctamente."""
        client = Client()
        response = client.get("/login/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Iniciar Sesión" in content
        assert "Nombre de usuario" in content

    def test_login_with_valid_credentials(self):
        """Login con credenciales válidas."""
        user = User.objects.create_user(username='testuser', password='testpass123')
        Usuario.objects.create(
            user=user, 
            DNI='12345678A',
            email='test@test.com'
        )
        
        client = Client()
        response = client.post("/login/", {
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == 302

    def test_login_with_invalid_password(self):
        """Login con contraseña incorrecta."""
        user = User.objects.create_user(username='testuser', password='testpass123')
        Usuario.objects.create(
            user=user, 
            DNI='12345678B',
            email='test@test.com'
        )
        
        client = Client()
        response = client.post("/login/", {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        assert response.status_code == 200
        assert "incorrectos" in response.content.decode()

    def test_login_redirects_to_home(self):
        """Después de login redirige al home."""
        user = User.objects.create_user(username='testuser', password='testpass123')
        Usuario.objects.create(
            user=user, 
            DNI='12345678C',
            email='test@test.com'
        )
        
        client = Client()
        response = client.post("/login/", {
            'username': 'testuser',
            'password': 'testpass123'
        }, follow=True)
        assert response.status_code == 200


@pytest.mark.django_db
class TestRegisterE2E:
    """Tests E2E para el flujo de registro."""

    def test_register_page_loads(self):
        """La página de registro carga correctamente."""
        client = Client()
        response = client.get("/register/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Crear Cuenta" in content

    def test_register_new_user_with_all_fields(self):
        """Registro de nuevo usuario con todos los campos."""
        client = Client()
        response = client.post("/register/", {
            'username': 'nuevouser',
            'password': 'password123',
            'confirm_password': 'password123',
            'dni': '12345678Z',
            'telefono': '612345678',
            'email': 'test@test.com',
            'fecha_nacimiento': '2000-01-01'
        })
        assert response.status_code == 302
        assert User.objects.filter(username='nuevouser').exists()

    def test_register_gives_10_monedas(self):
        """Registro da 10 monedas al nuevo usuario."""
        client = Client()
        response = client.post("/register/", {
            'username': 'nuevouser2',
            'password': 'password123',
            'confirm_password': 'password123',
            'dni': '22345678Z',
            'telefono': '612345678',
            'email': 'test2@test.com',
            'fecha_nacimiento': '2000-01-01'
        })
        usuario = Usuario.objects.get(user__username='nuevouser2')
        assert usuario.monedas == 10

    def test_register_password_mismatch(self):
        """Registro con contraseñas diferentes."""
        client = Client()
        response = client.post("/register/", {
            'username': 'testuser',
            'password': 'pass123',
            'confirm_password': 'pass456',
            'dni': '32345678A',
            'email': 'test@test.com',
            'fecha_nacimiento': '2000-01-01'
        })
        assert response.status_code == 200
        assert "coinciden" in response.content.decode()

    def test_register_short_password(self):
        """Registro con contraseña corta."""
        client = Client()
        response = client.post("/register/", {
            'username': 'testuser2',
            'password': '123',
            'confirm_password': '123',
            'dni': '42345678A',
            'email': 'test2@test.com',
            'fecha_nacimiento': '2000-01-01'
        })
        assert response.status_code == 200
        assert "8 caracteres" in response.content.decode()

    def test_register_missing_dni(self):
        """Registro sin DNI muestra error."""
        client = Client()
        response = client.post("/register/", {
            'username': 'testuser3',
            'password': 'password123',
            'confirm_password': 'password123',
            'email': 'test3@test.com',
            'fecha_nacimiento': '2000-01-01'
        })
        assert response.status_code == 200
        assert "DNI" in response.content.decode()

    def test_register_missing_email(self):
        """Registro sin email muestra error."""
        client = Client()
        response = client.post("/register/", {
            'username': 'testuser4',
            'password': 'password123',
            'confirm_password': 'password123',
            'dni': '52345678A',
            'fecha_nacimiento': '2000-01-01'
        })
        assert response.status_code == 200
        assert "email" in response.content.decode()

    def test_register_missing_fecha_nacimiento(self):
        """Registro sin fecha de nacimiento muestra error."""
        client = Client()
        response = client.post("/register/", {
            'username': 'testuser5',
            'password': 'password123',
            'confirm_password': 'password123',
            'dni': '62345678A',
            'email': 'test5@test.com'
        })
        assert response.status_code == 200
        assert "fecha" in response.content.decode()


@pytest.mark.django_db
class TestAuthFlowE2E:
    """Tests E2E para el flujo completo de autenticación."""

    def test_complete_auth_flow(self):
        """Flujo completo: registro -> logout -> login."""
        client = Client()
        
        # Registro
        response = client.post("/register/", {
            'username': 'flowuser',
            'password': 'password123',
            'confirm_password': 'password123',
            'dni': '72345678F',
            'email': 'flow@test.com',
            'fecha_nacimiento': '2000-01-01'
        })
        assert response.status_code == 302
        
        # Logout
        response = client.get("/logout/")
        assert response.status_code == 302
        
        # Login
        response = client.post("/login/", {
            'username': 'flowuser',
            'password': 'password123'
        })
        assert response.status_code == 302

    def test_unauthenticated_redirect(self):
        """Usuario no autenticado es redirigido a login."""
        client = Client()
        response = client.get("/")
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_menu_shows_login_when_logged_out(self):
        """El menú muestra opciones de login cuando está desconectado."""
        client = Client()
        response = client.get("/login/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Regístrate" in content

    def test_menu_shows_logout_when_logged_in(self):
        """El menú muestra cerrar sesión cuando está conectado."""
        user = User.objects.create_user(username='testuser', password='testpass123')
        Usuario.objects.create(
            user=user, 
            DNI='82345678G',
            email='test@test.com',
            fecha_nacimiento=date(2000,1,1)
        )
        
        client = Client()
        client.login(username='testuser', password='testpass123')
        response = client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Cerrar sesión" in content
