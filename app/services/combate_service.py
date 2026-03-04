"""
Servicio para gestionar las simulaciones de combate entre personajes.
Proporciona la lógica de combate por turnos y recolección de logs.
"""

from app.models import Personaje


class TurnoCombate:
    """Representa un turno individual del combate."""

    def __init__(
        self,
        numero,
        atacante,
        defensor,
        danio,
        tipo_ataque,
        vida_defensor_restante,
        mana_usado=0,
    ):
        self.numero = numero
        self.atacante = atacante
        self.defensor = defensor
        self.danio = danio
        self.tipo_ataque = tipo_ataque
        self.vida_defensor_restante = vida_defensor_restante
        self.mana_usado = mana_usado

    def a_dict(self):
        return {
            "numero": self.numero,
            "atacante": self.atacante,
            "defensor": self.defensor,
            "danio": self.danio,
            "tipo_ataque": self.tipo_ataque,
            "vida_defensor_restante": self.vida_defensor_restante,
            "mana_usado": self.mana_usado,
        }


class ResultadoCombate:
    """Representa el resultado completo de un combate."""

    def __init__(self, p1, p2, turnos, ganador, perdedor):
        self.p1 = p1
        self.p2 = p2
        self.turnos = turnos
        self.ganador = ganador
        self.perdedor = perdedor

    @property
    def turnos_json(self):
        import json

        return json.dumps([t.a_dict() for t in self.turnos])

    def a_dict(self):
        return {
            "personaje1": self.p1,
            "personaje2": self.p2,
            "turnos": [t.a_dict() for t in self.turnos],
            "ganador": self.ganador,
            "perdedor": self.perdedor,
        }


def simular_combate(
    personaje1_id, personaje2_id, usar_especial_p1=True, usar_especial_p2=False
):
    """
    Simula un combate entre dos personajes.

    Args:
        personaje1_id: ID del primer personaje (atacante inicial).
        personaje2_id: ID del segundo personaje (defensor inicial).
        usar_especial_p1: Si el personaje 1 debe usar ataque especial (Mago).
        usar_especial_p2: Si el personaje 2 debe usar ataque especial (Mago).

    Returns:
        ResultadoCombate con todos los detalles del combate.

    Raises:
        ValueError: Si alguno de los personajes no existe.
    """
    p1 = Personaje.objects.obtener_por_id(personaje1_id)
    p2 = Personaje.objects.obtener_por_id(personaje2_id)

    if not p1:
        raise ValueError(f"Personaje con ID {personaje1_id} no encontrado")
    if not p2:
        raise ValueError(f"Personaje con ID {personaje2_id} no encontrado")

    turnos = []
    numero_turno = 1

    while p1.esta_vivo() and p2.esta_vivo():
        danio = 0
        tipo_ataque = "normal"
        mana_usado = 0

        if (
            isinstance(p1, Personaje)
            and p1.tipo == "MAGO"
            and p1.mana >= 10
            and usar_especial_p1
        ):
            danio = p1.ataque_especial()
            tipo_ataque = "especial"
            mana_usado = 10
        else:
            danio = p1.ataque()

        if danio > 0:
            p2.recibir_danio(danio)

        turno = TurnoCombate(
            numero=numero_turno,
            atacante=p1.nombre,
            defensor=p2.nombre,
            danio=danio,
            tipo_ataque=tipo_ataque,
            vida_defensor_restante=p2.vida,
            mana_usado=mana_usado,
        )
        turnos.append(turno)

        if not p2.esta_vivo():
            break

        danio2 = p2.ataque()
        tipo_ataque2 = "normal"
        mana_usado2 = 0

        if (
            isinstance(p2, Personaje)
            and p2.tipo == "MAGO"
            and p2.mana >= 10
            and usar_especial_p2
        ):
            danio2 = p2.ataque_especial()
            tipo_ataque2 = "especial"
            mana_usado2 = 10

        if danio2 > 0:
            p1.recibir_danio(danio2)

        turno2 = TurnoCombate(
            numero=numero_turno,
            atacante=p2.nombre,
            defensor=p1.nombre,
            danio=danio2,
            tipo_ataque=tipo_ataque2,
            vida_defensor_restante=p1.vida,
            mana_usado=mana_usado2,
        )
        turnos.append(turno2)

        if not p1.esta_vivo():
            break

        numero_turno += 1

    if p1.esta_vivo():
        return ResultadoCombate(
            p1={
                "id": p1.id,
                "nombre": p1.nombre,
                "vida": p1.vida,
                "vida_max": p1.vida_max,
            },
            p2={
                "id": p2.id,
                "nombre": p2.nombre,
                "vida": p2.vida,
                "vida_max": p2.vida_max,
            },
            turnos=turnos,
            ganador={"id": p1.id, "nombre": p1.nombre},
            perdedor={"id": p2.id, "nombre": p2.nombre},
        )
    else:
        return ResultadoCombate(
            p1={
                "id": p1.id,
                "nombre": p1.nombre,
                "vida": p1.vida,
                "vida_max": p1.vida_max,
            },
            p2={
                "id": p2.id,
                "nombre": p2.nombre,
                "vida": p2.vida,
                "vida_max": p2.vida_max,
            },
            turnos=turnos,
            ganador={"id": p2.id, "nombre": p2.nombre},
            perdedor={"id": p1.id, "nombre": p1.nombre},
        )


def guardar_resultado_combate(personaje1_id, personaje2_id):
    """
    Guarda los cambios de los personajes después de un combate.

    Args:
        personaje1_id: ID del primer personaje.
        personaje2_id: ID del segundo personaje.
    """
    p1 = Personaje.objects.obtener_por_id(personaje1_id)
    p2 = Personaje.objects.obtener_por_id(personaje2_id)

    if p1:
        p1.save()
    if p2:
        p2.save()
