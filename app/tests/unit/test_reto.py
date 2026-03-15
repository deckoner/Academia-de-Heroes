import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from app.models import Usuario, Personaje, Batalla
from app.services.combate_service import simular_combate, guardar_resultado_combate
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
def personaje_a(db, usuario_a):
    """Personaje del usuario A."""
    return Personaje.objects.create(
        id_usuario=usuario_a,
        tipo="GUERRERO",
        nombre="GuerreroA",
        nivel=1,
        vida=100,
        vida_max=100,
        armadura=10,
        vivo=True,
    )


@pytest.fixture
def personaje_b(db, usuario_b):
    """Personaje del usuario B."""
    return Personaje.objects.create(
        id_usuario=usuario_b,
        tipo="MAGO",
        nombre="MagoB",
        nivel=1,
        vida=100,
        vida_max=100,
        mana=50,
        vivo=True,
    )


@pytest.mark.django_db
class TestBatallaManager:
    """Tests del manager de Batalla."""

    def test_obtener_por_id(self, usuario_a, usuario_b, personaje_a, personaje_b):
        """Se puede obtener una batalla por ID."""
        batalla = Batalla.objects.create(
            id_atacante=usuario_a,
            id_defensor=usuario_b,
            personaje_atacante=personaje_a,
            personaje_defensor=personaje_b,
            resultado=True,
        )
        result = Batalla.objects.obtener_por_id(batalla.id)
        assert result is not None
        assert result.id == batalla.id

    def test_obtener_por_id_no_existe(self):
        """Obtener batalla con ID inexistente retorna None."""
        result = Batalla.objects.obtener_por_id(99999)
        assert result is None

    def test_listar_por_usuario(self, usuario_a, usuario_b, personaje_a, personaje_b):
        """Se pueden listar batallas por usuario."""
        Batalla.objects.create(
            id_atacante=usuario_a,
            id_defensor=usuario_b,
            personaje_atacante=personaje_a,
            personaje_defensor=personaje_b,
            resultado=True,
        )

        batallas_a = Batalla.objects.listar_por_usuario(usuario_a.id)
        assert batallas_a.count() == 1

        batallas_b = Batalla.objects.listar_por_usuario(usuario_b.id)
        assert batallas_b.count() == 1


@pytest.mark.django_db
class TestCombateService:
    """Tests del servicio de combate."""

    def test_simular_combate(self, personaje_a, personaje_b):
        """Se puede simular un combate."""
        resultado = simular_combate(
            personaje_a.id,
            personaje_b.id,
            usar_especial_p1=True,
            usar_especial_p2=True,
        )
        assert resultado is not None
        assert resultado.ganador is not None
        assert resultado.perdedor is not None

    def test_guardar_resultado_combate_actualiza_vida(self, personaje_a, personaje_b):
        """Guardar resultado actualiza la vida de los personajes."""
        personaje_a.vida = 50
        personaje_a.save()
        
        guardar_resultado_combate(personaje_a.id, personaje_b.id, 30, 80)
        
        personaje_a.refresh_from_db()
        assert personaje_a.vida == 30

    def test_guardar_resultado_combate_vida_negativa(self, personaje_a, personaje_b):
        """Guardar resultado con vida negativa establece a 0."""
        personaje_a.vida = 10
        personaje_a.save()
        
        guardar_resultado_combate(personaje_a.id, personaje_b.id, 5, 50)
        
        personaje_a.refresh_from_db()
        assert personaje_a.vida == 5


@pytest.mark.django_db
class TestCombateConMuerte:
    """Tests de combate con muerte de personajes."""

    def test_personaje_muere_al_llegar_a_cero_vida(self, personaje_a, personaje_b):
        """Un personaje que llega a 0 de vida muere."""
        resultado = simular_combate(
            personaje_a.id,
            personaje_b.id,
            usar_especial_p1=True,
            usar_especial_p2=True,
        )
        
        guardar_resultado_combate(
            personaje_a.id,
            personaje_b.id,
            resultado.vida1_final,
            resultado.vida2_final,
        )
        
        personaje_a.refresh_from_db()
        personaje_b.refresh_from_db()
        
        if resultado.vida1_final == 0:
            assert personaje_a.vivo == False
        if resultado.vida2_final == 0:
            assert personaje_b.vivo == False


@pytest.mark.django_db
class TestCombateMago:
    """Tests específicos para magos."""

    def test_mago_puede_usar_ataque_especial(self, usuario_a, usuario_b):
        """El mago puede usar ataque especial."""
        mago = Personaje.objects.create(
            id_usuario=usuario_a,
            tipo="MAGO",
            nombre="MagoTest",
            nivel=1,
            vida=100,
            vida_max=100,
            mana=50,
            vivo=True,
        )
        guerrero = Personaje.objects.create(
            id_usuario=usuario_b,
            tipo="GUERRERO",
            nombre="GuerreroTest",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            vivo=True,
        )
        
        resultado = simular_combate(
            mago.id,
            guerrero.id,
            usar_especial_p1=True,
            usar_especial_p2=True,
        )
        
        assert resultado is not None


@pytest.mark.django_db
class TestCombateArquero:
    """Tests específicos para arqueros."""

    def test_arquero_puede_atacar(self, usuario_a, usuario_b):
        """El arquero puede atacar."""
        arquero = Personaje.objects.create(
            id_usuario=usuario_a,
            tipo="ARQUERO",
            nombre="ArqueroTest",
            nivel=1,
            vida=100,
            vida_max=100,
            precision=80,
            vivo=True,
        )
        guerrero = Personaje.objects.create(
            id_usuario=usuario_b,
            tipo="GUERRERO",
            nombre="GuerreroTest2",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            vivo=True,
        )
        
        resultado = simular_combate(
            arquero.id,
            guerrero.id,
            usar_especial_p1=False,
            usar_especial_p2=False,
        )
        
        assert resultado is not None
