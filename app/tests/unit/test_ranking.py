import pytest
from django.contrib.auth.models import User
from app.models import Usuario, Personaje, Batalla
from app.services.ranking_service import (
    es_mayor_de_edad,
    es_mayor_de_edad_fecha,
    obtener_usuarios_mayores,
    ranking_usuarios,
    ranking_personajes,
)
from datetime import date


@pytest.fixture
def usuario_mayor(db):
    """Usuario mayor de edad."""
    user = User.objects.create_user(username="mayor_test", password="pass123")
    return Usuario.objects.create(
        user=user,
        DNI="11111111A",
        email="mayor@test.com",
        fecha_nacimiento=date(1990, 1, 1),
    )


@pytest.fixture
def usuario_menor(db):
    """Usuario menor de edad."""
    user = User.objects.create_user(username="menor_test", password="pass123")
    return Usuario.objects.create(
        user=user,
        DNI="22222222B",
        email="menor@test.com",
        fecha_nacimiento=date(2010, 1, 1),
    )


@pytest.fixture
def personaje_mayor(db, usuario_mayor):
    """Personaje de usuario mayor."""
    return Personaje.objects.create(
        id_usuario=usuario_mayor,
        tipo="GUERRERO",
        nombre="GuerreroMayor",
        nivel=1,
        vida=100,
        vida_max=100,
        armadura=10,
        vivo=True,
    )


@pytest.fixture
def personaje_menor(db, usuario_menor):
    """Personaje de usuario menor."""
    return Personaje.objects.create(
        id_usuario=usuario_menor,
        tipo="MAGO",
        nombre="MagoMenor",
        nivel=1,
        vida=100,
        vida_max=100,
        mana=50,
        vivo=True,
    )


@pytest.mark.django_db
class TestEsMayorDeEdad:
    """Tests para la funcion es_mayor_de_edad."""

    def test_usuario_mayor_de_edad(self, usuario_mayor):
        """Usuario mayor de edad devuelve True."""
        assert es_mayor_de_edad(usuario_mayor) is True

    def test_usuario_menor_de_edad(self, usuario_menor):
        """Usuario menor de edad devuelve False."""
        assert es_mayor_de_edad(usuario_menor) is False

    def test_usuario_sin_fecha_nacimiento(self):
        """Usuario sin fecha de nacimiento devuelve False."""
        user = User.objects.create_user(username="sin_fecha", password="pass123")
        usuario = Usuario.objects.create(
            user=user,
            DNI="33333333C",
            email="sinfecha@test.com",
            fecha_nacimiento=None,
        )
        assert es_mayor_de_edad(usuario) is False


@pytest.mark.django_db
class TestEsMayorDeEdadFecha:
    """Tests para la funcion es_mayor_de_edad_fecha."""

    def test_fecha_mayor_de_edad(self):
        """Fecha de nacimiento mayor de edad."""
        assert es_mayor_de_edad_fecha(date(1990, 1, 1)) is True

    def test_fecha_menor_de_edad(self):
        """Fecha de nacimiento menor de edad."""
        assert es_mayor_de_edad_fecha(date(2010, 1, 1)) is False

    def test_fecha_none(self):
        """Fecha None devuelve False."""
        assert es_mayor_de_edad_fecha(None) is False


@pytest.mark.django_db
class TestObtenerUsuariosMayores:
    """Tests para obtener_usuarios_mayores."""

    def test_solo_mayores(self, usuario_mayor, usuario_menor):
        """Solo devuelve usuarios mayores de edad."""
        resultado = obtener_usuarios_mayores()
        assert usuario_mayor.id in resultado
        assert usuario_menor.id not in resultado


@pytest.mark.django_db
class TestRankingUsuarios:
    """Tests para ranking_usuarios."""

    def test_ranking_vacio(self):
        """Sin usuarios mayores devuelve lista vacía."""
        assert ranking_usuarios() == []

    def test_ranking_con_dos_usuarios(self, usuario_mayor, personaje_mayor):
        """Dos usuarios mayores con bataille corpo."""
        otro_user = User.objects.create_user(username="otro2", password="pass123")
        otro_usuario = Usuario.objects.create(
            user=otro_user,
            DNI="33333333C",
            email="otro2@test.com",
            fecha_nacimiento=date(1990, 1, 1),
        )
        personaje_otro = Personaje.objects.create(
            id_usuario=otro_usuario,
            tipo="MAGO",
            nombre="MagoOtro",
            nivel=1,
            vida=100,
            vida_max=100,
            mana=50,
            vivo=True,
        )

        Batalla.objects.create(
            id_atacante=usuario_mayor,
            id_defensor=otro_usuario,
            personaje_atacante=personaje_mayor,
            personaje_defensor=personaje_otro,
            resultado=True,
        )

        ranking = ranking_usuarios()

        assert len(ranking) == 2
        usuario_mayor_victorias = next(
            (v for u, v in ranking if u.id == usuario_mayor.id), 0
        )
        assert usuario_mayor_victorias == 1

    def test_ranking_excluye_menores(
        self, usuario_mayor, usuario_menor, personaje_mayor, personaje_menor
    ):
        """Usuario menor no aparece en el ranking, menor puede ganar contra mayor."""
        Batalla.objects.create(
            id_atacante=usuario_menor,
            id_defensor=usuario_mayor,
            personaje_atacante=personaje_menor,
            personaje_defensor=personaje_mayor,
            resultado=True,
        )

        ranking = ranking_usuarios()

        usuario_menor_en_ranking = any(u.id == usuario_menor.id for u, v in ranking)
        assert usuario_menor_en_ranking is False


@pytest.mark.django_db
class TestRankingPersonajes:
    """Tests para ranking_personajes."""

    def test_ranking_vacio(self):
        """Sin personajes devuelve lista vacía."""
        assert ranking_personajes() == []

    def test_ranking_con_victorias(
        self, usuario_mayor, personaje_mayor, personaje_menor
    ):
        """Calcula ranking de personajes correctamente."""
        personaje_mayor_2 = Personaje.objects.create(
            id_usuario=usuario_mayor,
            tipo="MAGO",
            nombre="MagoMayor",
            nivel=1,
            vida=100,
            vida_max=100,
            mana=50,
            vivo=True,
        )

        otro_usuario = User.objects.create_user(username="otro", password="pass123")
        otro_perfil = Usuario.objects.create(
            user=otro_usuario,
            DNI="44444444D",
            email="otro@test.com",
            fecha_nacimiento=date(1990, 1, 1),
        )
        personaje_otro = Personaje.objects.create(
            id_usuario=otro_perfil,
            tipo="ARQUERO",
            nombre="ArqueroOtro",
            nivel=1,
            vida=100,
            vida_max=100,
            precision=80,
            vivo=True,
        )

        Batalla.objects.create(
            id_atacante=usuario_mayor,
            id_defensor=otro_perfil,
            personaje_atacante=personaje_mayor,
            personaje_defensor=personaje_otro,
            resultado=True,
        )
        Batalla.objects.create(
            id_atacante=otro_perfil,
            id_defensor=usuario_mayor,
            personaje_atacante=personaje_otro,
            personaje_defensor=personaje_mayor_2,
            resultado=False,
        )

        ranking = ranking_personajes()

        assert len(ranking) == 3

    def test_ranking_excluye_personajes_menores(
        self, usuario_mayor, usuario_menor, personaje_mayor, personaje_menor
    ):
        """No incluye personajes de menores en el ranking."""
        Batalla.objects.create(
            id_atacante=usuario_mayor,
            id_defensor=usuario_menor,
            personaje_atacante=personaje_mayor,
            personaje_defensor=personaje_menor,
            resultado=True,
        )

        ranking = ranking_personajes()

        assert len(ranking) == 1
        assert ranking[0][0].id == personaje_mayor.id
