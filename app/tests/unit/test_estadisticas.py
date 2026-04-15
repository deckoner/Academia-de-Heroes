import pytest
from django.contrib.auth.models import User
from app.models import Usuario, Personaje, Batalla
from app.services.estadisticas_service import (
    clases_mas_seleccionadas,
    clases_ganadoras_mas_combates,
    clases_mas_entrenadas,
    ranking_personajes_estadisticas,
    promedio_batallas_por_usuario,
    usuarios_por_edad,
    distribucion_niveles,
    todas_las_estadisticas,
)
from datetime import date, datetime


@pytest.fixture
def usuario_admin(db):
    """Usuario con privilegios de administrador."""
    user = User.objects.create_user(username="admin_test", password="pass123")
    return Usuario.objects.create(
        user=user,
        DNI="11111111A",
        email="admin@test.com",
        fecha_nacimiento=date(1990, 1, 1),
        es_admin=True,
    )


@pytest.fixture
def usuario_mayor(db):
    """Usuario mayor de edad."""
    user = User.objects.create_user(username="mayor_test", password="pass123")
    return Usuario.objects.create(
        user=user,
        DNI="22222222B",
        email="mayor@test.com",
        fecha_nacimiento=date(1990, 1, 1),
    )


@pytest.fixture
def usuario_menor(db):
    """Usuario menor de edad."""
    user = User.objects.create_user(username="menor_test", password="pass123")
    return Usuario.objects.create(
        user=user,
        DNI="33333333C",
        email="menor@test.com",
        fecha_nacimiento=date(2010, 1, 1),
    )


@pytest.fixture
def personaje_guerrero(db, usuario_mayor):
    """Personaje tipo guerrero."""
    return Personaje.objects.create(
        id_usuario=usuario_mayor,
        tipo="GUERRERO",
        nombre="GuerreroTest",
        nivel=5,
        vida=100,
        vida_max=100,
        armadura=10,
        vivo=True,
    )


@pytest.fixture
def personaje_mago(db, usuario_mayor):
    """Personaje tipo mago."""
    return Personaje.objects.create(
        id_usuario=usuario_mayor,
        tipo="MAGO",
        nombre="MagoTest",
        nivel=3,
        vida=80,
        vida_max=80,
        armadura=5,
        vivo=True,
    )


@pytest.fixture
def batalla_entre_personajes(db, usuario_mayor, personaje_guerrero, personaje_mago):
    """Batalla entre dos personajes."""
    return Batalla.objects.create(
        id_atacante=usuario_mayor,
        id_defensor=usuario_mayor,
        personaje_atacante=personaje_guerrero,
        personaje_defensor=personaje_mago,
        resultado=True,
        fecha_batalla=datetime.now(),
    )


class TestClasesMasSeleccionadas:
    """Tests para la funcion clases_mas_seleccionadas."""

    def test_devuelve_lista_vacia_sin_personajes(self, db):
        """Debe devolver lista vacia si no hay personajes."""
        resultado = clases_mas_seleccionadas()
        assert resultado == []

    def test_devuelve_clases_seleccionadas(
        self, db, personaje_guerrero, personaje_mago
    ):
        """Debe devolver las clases con su cantidad."""
        resultado = clases_mas_seleccionadas()
        assert len(resultado) == 2
        assert any("Guerrero" in r[0] for r in resultado)
        assert any("Mago" in r[0] for r in resultado)


class TestClasesGanadorasMasCombates:
    """Tests para la funcion clases_ganadoras_mas_combates."""

    def test_devuelve_lista_vacia_sin_usuarios_mayores(self, db):
        """Debe devolver lista vacia si no hay usuarios mayores de edad."""
        resultado = clases_ganadoras_mas_combates()
        assert resultado == []

    def test_devuelve_victorias_por_clase(
        self,
        db,
        usuario_mayor,
        personaje_guerrero,
        personaje_mago,
        batalla_entre_personajes,
    ):
        """Debe contar las victorias por clase."""
        resultado = clases_ganadoras_mas_combates()
        assert len(resultado) > 0

    def test_devuelve_tres_clases(self, db, usuario_mayor):
        """Debe devolver las 3 clases siempre (incluso con 0 victorias)."""
        resultado = clases_ganadoras_mas_combates()
        assert len(resultado) == 3
        clases = [r[0] for r in resultado]
        assert "Guerrero" in clases
        assert "Mago" in clases
        assert "Arquero" in clases


class TestClasesMasEntrenadas:
    """Tests para la funcion clases_mas_entrenadas."""

    def test_devuelve_lista_vacia_sin_personajes(self, db, usuario_mayor):
        """Debe devolver lista vacia si no hay personajes de usuarios mayores."""
        resultado = clases_mas_entrenadas()
        assert resultado == []

    def test_devuelve_nivel_promedio_por_clase(
        self, db, usuario_mayor, personaje_guerrero, personaje_mago
    ):
        """Debe devolver el nivel promedio por clase."""
        resultado = clases_mas_entrenadas()
        assert len(resultado) > 0
        assert all(isinstance(r[1], int) for r in resultado)


class TestRankingPersonajes:
    """Tests para la funcion ranking_personajes_estadisticas."""

    def test_devuelve_lista_vacia_sin_usuarios_mayores(self, db, usuario_menor):
        """Debe devolver lista vacia si no hay usuarios mayores de edad."""
        resultado = ranking_personajes_estadisticas()
        assert resultado == []

    def test_devuelve_ranking_limitado_a_10(
        self, db, usuario_mayor, personaje_guerrero
    ):
        """Debe devolver maximo 10 personajes."""
        resultado = ranking_personajes_estadisticas()
        assert len(resultado) <= 10


class TestPromedioBatallasPorUsuario:
    """Tests para la funcion promedio_batallas_por_usuario."""

    def test_devuelve_ceros_sin_usuarios_mayores(self, db):
        """Debe devolver ceros si no hay usuarios mayores."""
        resultado = promedio_batallas_por_usuario()
        assert resultado["promedio"] == 0
        assert resultado["total_batallas"] == 0
        assert resultado["total_usuarios"] == 0

    def test_calcula_promedio_correctamente(
        self,
        db,
        usuario_mayor,
        personaje_guerrero,
        personaje_mago,
        batalla_entre_personajes,
    ):
        """Debe calcular el promedio de batallas."""
        resultado = promedio_batallas_por_usuario()
        assert resultado["total_batallas"] == 1
        assert resultado["total_usuarios"] >= 1


class TestUsuariosPorEdad:
    """Tests para la funcion usuarios_por_edad."""

    def test_devuelve_rangos_de_edad(self, db, usuario_mayor, usuario_menor):
        """Debe devolver usuarios agrupados por rango de edad."""
        resultado = usuarios_por_edad()
        assert len(resultado) == 5
        rangos = [r["rango"] for r in resultado]
        assert "Menores" in rangos
        assert "18-25" in rangos


class TestDistribucionNiveles:
    """Tests para la funcion distribucion_niveles."""

    def test_devuelve_diccionario_vacio_sin_usuarios(self, db):
        """Debe devolver diccionario vacio sin usuarios mayores."""
        resultado = distribucion_niveles()
        assert resultado["por_clase"] == {}
        assert resultado["outliers"] == []

    def test_devuelve_niveles_por_clase(self, db, usuario_mayor, personaje_guerrero):
        """Debe devolver niveles agrupados por clase."""
        resultado = distribucion_niveles()
        assert "Guerrero" in resultado["por_clase"]


class TestTodasLasEstadisticas:
    """Tests para la funcion todas_las_estadisticas."""

    def test_devuelve_todas_las_estadisticas(self, db):
        """Debe devolver un diccionario con todas las estadisticas."""
        resultado = todas_las_estadisticas()
        assert "clases_seleccionadas" in resultado
        assert "clases_ganadoras" in resultado
        assert "ranking_personajes" in resultado
        assert "promedio_batallas" in resultado
        assert "clases_entrenadas" in resultado
        assert "usuarios_por_edad" in resultado
        assert "distribucion_niveles" in resultado
