import pytest
from app.models import Personaje
from app.services.combate_service import (
    TurnoCombate,
    ResultadoCombate,
    simular_combate,
    guardar_resultado_combate,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestTurnoCombate:
    """Tests para la clase TurnoCombate."""

    def test_turno_combate_creacion(self):
        """Verifica la creación de un turno de combate."""
        turno = TurnoCombate(
            numero=1,
            atacante="Guerrero1",
            defensor="Mago1",
            danio=25,
            tipo_ataque="normal",
            vida_defensor_restante=75,
            mana_usado=0,
        )

        assert turno.numero == 1
        assert turno.atacante == "Guerrero1"
        assert turno.defensor == "Mago1"
        assert turno.danio == 25
        assert turno.tipo_ataque == "normal"
        assert turno.vida_defensor_restante == 75
        assert turno.mana_usado == 0

    def test_turno_combate_a_dict(self):
        """Verifica la conversión a diccionario."""
        turno = TurnoCombate(
            numero=1,
            atacante="Guerrero1",
            defensor="Mago1",
            danio=25,
            tipo_ataque="especial",
            vida_defensor_restante=75,
            mana_usado=10,
        )

        result = turno.a_dict()

        assert result["numero"] == 1
        assert result["atacante"] == "Guerrero1"
        assert result["defensor"] == "Mago1"
        assert result["danio"] == 25
        assert result["tipo_ataque"] == "especial"
        assert result["vida_defensor_restante"] == 75
        assert result["mana_usado"] == 10


@pytest.mark.unit
@pytest.mark.django_db
class TestResultadoCombate:
    """Tests para la clase ResultadoCombate."""

    def test_resultado_combate_creacion(self):
        """Verifica la creación de un resultado de combate."""
        turnos = [
            TurnoCombate(1, "Guerrero1", "Mago1", 20, "normal", 80, 0),
            TurnoCombate(1, "Mago1", "Guerrero1", 15, "normal", 85, 0),
        ]

        resultado = ResultadoCombate(
            p1={"id": 1, "nombre": "Guerrero1", "vida": 85, "vida_max": 100},
            p2={"id": 2, "nombre": "Mago1", "vida": 80, "vida_max": 100},
            turnos=turnos,
            ganador={"id": 1, "nombre": "Guerrero1"},
            perdedor={"id": 2, "nombre": "Mago1"},
        )

        assert resultado.p1["nombre"] == "Guerrero1"
        assert resultado.p2["nombre"] == "Mago1"
        assert len(resultado.turnos) == 2
        assert resultado.ganador["nombre"] == "Guerrero1"

    def test_resultado_combate_a_dict(self):
        """Verifica la conversión a diccionario."""
        turnos = [
            TurnoCombate(1, "Guerrero1", "Mago1", 20, "normal", 80, 0),
        ]

        resultado = ResultadoCombate(
            p1={"id": 1, "nombre": "Guerrero1", "vida": 85, "vida_max": 100},
            p2={"id": 2, "nombre": "Mago1", "vida": 80, "vida_max": 100},
            turnos=turnos,
            ganador={"id": 1, "nombre": "Guerrero1"},
            perdedor={"id": 2, "nombre": "Mago1"},
        )

        result = resultado.a_dict()

        assert "personaje1" in result
        assert "personaje2" in result
        assert "turnos" in result
        assert "ganador" in result
        assert "perdedor" in result


@pytest.mark.unit
@pytest.mark.django_db
class TestSimularCombate:
    """Tests para la función simular_combate."""

    def test_simular_combate_personaje_inexistente(self):
        """Verifica el error al usar un personaje que no existe."""
        with pytest.raises(ValueError) as exc_info:
            simular_combate(9999, 1)

        assert "no encontrado" in str(exc_info.value)

    def test_simular_combate_dos_personajes(self):
        """Verifica que el combate entre dos personajes funciona correctamente."""
        p1 = Personaje.objects.create(
            tipo="GUERRERO",
            nombre="GuerreroTest",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )
        p2 = Personaje.objects.create(
            tipo="ARQUERO",
            nombre="ArqueroTest",
            nivel=1,
            vida=80,
            vida_max=80,
            armadura=None,
            mana=None,
            precision=80,
        )

        resultado = simular_combate(p1.id, p2.id)

        assert resultado is not None
        assert len(resultado.turnos) > 0
        assert resultado.ganador is not None
        assert resultado.perdedor is not None
        assert resultado.p1["nombre"] in ["GuerreroTest", "ArqueroTest"]
        assert resultado.p2["nombre"] in ["GuerreroTest", "ArqueroTest"]

    def test_simular_combate_dos_guerreros(self):
        """Verifica el combate entre dos guerreros."""
        p1 = Personaje.objects.create(
            tipo="GUERRERO",
            nombre="Guerrero1",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )
        p2 = Personaje.objects.create(
            tipo="GUERRERO",
            nombre="Guerrero2",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )

        resultado = simular_combate(p1.id, p2.id)

        assert resultado is not None
        assert len(resultado.turnos) > 0
        assert resultado.ganador["nombre"] in ["Guerrero1", "Guerrero2"]
        assert resultado.perdedor["nombre"] in ["Guerrero1", "Guerrero2"]

    def test_simular_combate_dos_magos(self):
        """Verifica el combate entre dos magos."""
        p1 = Personaje.objects.create(
            tipo="MAGO",
            nombre="Mago1",
            nivel=1,
            vida=80,
            vida_max=80,
            armadura=None,
            mana=50,
            precision=None,
        )
        p2 = Personaje.objects.create(
            tipo="MAGO",
            nombre="Mago2",
            nivel=1,
            vida=80,
            vida_max=80,
            armadura=None,
            mana=50,
            precision=None,
        )

        resultado = simular_combate(p1.id, p2.id)

        assert resultado is not None
        assert len(resultado.turnos) > 0

    def test_simular_combate_mago_con_especial(self):
        """Verifica el combate donde el mago usa ataque especial."""
        p1 = Personaje.objects.create(
            tipo="MAGO",
            nombre="MagoCombat",
            nivel=1,
            vida=80,
            vida_max=80,
            armadura=None,
            mana=50,
            precision=None,
        )
        p2 = Personaje.objects.create(
            tipo="GUERRERO",
            nombre="GuerreroTarget",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )

        resultado = simular_combate(p1.id, p2.id, usar_especial_p1=True)

        assert resultado is not None
        assert len(resultado.turnos) > 0

    def test_simular_combate_turnos_tienen_informacion_correcta(self):
        """Verifica que los turnos contienen la información correcta."""
        p1 = Personaje.objects.create(
            tipo="GUERRERO",
            nombre="G1",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )
        p2 = Personaje.objects.create(
            tipo="GUERRERO",
            nombre="G2",
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )

        resultado = simular_combate(p1.id, p2.id)

        for turno in resultado.turnos:
            assert hasattr(turno, "numero")
            assert hasattr(turno, "atacante")
            assert hasattr(turno, "defensor")
            assert hasattr(turno, "danio")
            assert hasattr(turno, "tipo_ataque")
            assert hasattr(turno, "vida_defensor_restante")


@pytest.mark.unit
@pytest.mark.django_db
class TestGuardarResultadoCombate:
    """Tests para la función guardar_resultado_combate."""

    def test_guardar_resultado_combate(self):
        """Verifica que se guardan los cambios después de un combate."""
        p1 = Personaje.objects.create(
            tipo="GUERRERO",
            nombre="GuerreroSave1",
            nivel=1,
            vida=0,
            vida_max=100,
            armadura=5,
            mana=None,
            precision=None,
        )
        p2 = Personaje.objects.create(
            tipo="ARQUERO",
            nombre="ArqueroSave1",
            nivel=1,
            vida=80,
            vida_max=80,
            armadura=None,
            mana=None,
            precision=80,
        )

        vida_original_p1 = p1.vida
        vida_original_p2 = p2.vida

        resultado = simular_combate(p1.id, p2.id)
        
        guardar_resultado_combate(p1.id, p2.id, resultado.vida1_final, resultado.vida2_final)

        p1.refresh_from_db()
        p2.refresh_from_db()

        assert p1.vida <= vida_original_p1
        assert p2.vida <= vida_original_p2
