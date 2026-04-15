import pytest
from django.test import Client
from django.contrib.auth.models import User
from app.models import Usuario, Personaje, Batalla
from datetime import date, datetime


@pytest.fixture
def usuario_regular(db):
    """Usuario sin privilegios de administrador."""
    user = User.objects.create_user(username="user_regular", password="testpass123")
    return Usuario.objects.create(
        user=user,
        DNI="00000001A",
        email="regular@test.com",
        fecha_nacimiento=date(1990, 1, 1),
        es_admin=False,
    )


@pytest.fixture
def usuario_admin(db):
    """Usuario con privilegios de administrador."""
    user = User.objects.create_user(username="user_admin", password="testpass123")
    return Usuario.objects.create(
        user=user,
        DNI="00000002B",
        email="admin@test.com",
        fecha_nacimiento=date(1985, 1, 1),
        es_admin=True,
    )


@pytest.fixture
def personaje_admin(db, usuario_admin):
    """Personaje del usuario administrador."""
    return Personaje.objects.create(
        id_usuario=usuario_admin,
        tipo="GUERRERO",
        nombre="GuerreroAdmin",
        nivel=5,
        vida=100,
        vida_max=100,
        armadura=10,
        vivo=True,
    )


@pytest.fixture
def cliente_regular(db, usuario_regular):
    """Cliente autenticado como usuario regular."""
    client = Client()
    client.login(username="user_regular", password="testpass123")
    return client


@pytest.fixture
def cliente_admin(db, usuario_admin):
    """Cliente autenticado como administrador."""
    client = Client()
    client.login(username="user_admin", password="testpass123")
    return client


@pytest.fixture
def cliente_anonimo(db):
    """Cliente sin autenticar."""
    return Client()


@pytest.mark.django_db
class TestEstadisticasPage:
    """Tests E2E para la pagina de estadisticas."""

    def test_estadisticas_redirect_anonimo(self, cliente_anonimo):
        """Usuario anonimo debe ser redirigido."""
        response = cliente_anonimo.get("/estadisticas/")
        assert response.status_code in [302, 301]

    def test_estadisticas_redirect_usuario_regular(self, cliente_regular):
        """Usuario regular sin privilegios debe ser redirigido."""
        response = cliente_regular.get("/estadisticas/")
        assert response.status_code == 302

    def test_estadisticas_carga_admin(self, cliente_admin):
        """Administrador puede acceder a la pagina."""
        response = cliente_admin.get("/estadisticas/")
        assert response.status_code == 200

    def test_estadisticas_tiene_contexto(self, cliente_admin):
        """La pagina debe tener el contexto de estadisticas."""
        response = cliente_admin.get("/estadisticas/")
        assert "estadisticas" in response.context

    def test_estadisticas_tiene_clases_seleccionadas(
        self, cliente_admin, personaje_admin
    ):
        """La pagina debe incluir clases_seleccionadas."""
        response = cliente_admin.get("/estadisticas/")
        assert "clases_seleccionadas" in response.context["estadisticas"]

    def test_estadisticas_tiene_ranking(self, cliente_admin):
        """La pagina debe incluir ranking_personajes."""
        response = cliente_admin.get("/estadisticas/")
        assert "ranking_personajes" in response.context["estadisticas"]

    def test_estadisticas_tiene_usuarios_por_edad(self, cliente_admin):
        """La pagina debe incluir usuarios_por_edad."""
        response = cliente_admin.get("/estadisticas/")
        assert "usuarios_por_edad" in response.context["estadisticas"]

    def test_estadisticas_tiene_distribucion_niveles(self, cliente_admin):
        """La pagina debe incluir distribucion_niveles."""
        response = cliente_admin.get("/estadisticas/")
        assert "distribucion_niveles" in response.context["estadisticas"]

    def test_estadisticas_tiene_promedio_batallas(self, cliente_admin):
        """La pagina debe incluir promedio_batallas."""
        response = cliente_admin.get("/estadisticas/")
        assert "promedio_batallas" in response.context["estadisticas"]

    def test_estadisticas_tiene_clases_entrenadas(self, cliente_admin):
        """La pagina debe incluir clases_entrenadas."""
        response = cliente_admin.get("/estadisticas/")
        assert "clases_entrenadas" in response.context["estadisticas"]

    def test_estadisticas_tiene_clases_ganadoras(self, cliente_admin):
        """La pagina debe incluir clases_ganadoras."""
        response = cliente_admin.get("/estadisticas/")
        assert "clases_ganadoras" in response.context["estadisticas"]


@pytest.mark.django_db
class TestEstadisticasConDatos:
    """Tests E2E para estadisticas con datos en la base de datos."""

    def test_estadisticas_muestra_datos_con_personajes(
        self, cliente_admin, usuario_admin, personaje_admin
    ):
        """Las estadisticas deben mostrar datos cuando hay personajes."""
        response = cliente_admin.get("/estadisticas/")
        estadisticas = response.context["estadisticas"]
        assert estadisticas["clases_seleccionadas"] is not None
        assert estadisticas["distribucion_niveles"] is not None

    def test_estadisticas_calcular_promedio_batallas(
        self, cliente_admin, usuario_admin, personaje_admin
    ):
        """El promedio de batallas debe calcularse correctamente."""
        response = cliente_admin.get("/estadisticas/")
        promedio = response.context["estadisticas"]["promedio_batallas"]
        assert "promedio" in promedio
        assert "total_batallas" in promedio
        assert "total_usuarios" in promedio


@pytest.mark.django_db
class TestEstadisticasSinDatos:
    """Tests E2E para estadisticas sin datos."""

    def test_estadisticas_sin_usuarios(self, cliente_admin):
        """Las estadisticas deben manejar caso sin usuarios."""
        response = cliente_admin.get("/estadisticas/")
        estadisticas = response.context["estadisticas"]
        assert estadisticas["clases_entrenadas"] == []
        assert estadisticas["promedio_batallas"]["promedio"] == 0
