from app.models import Personaje
import json
import random


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
        mana_restante_atacante=None,
        mana_restante_defensor=None,
    ):
        self.numero = numero
        self.atacante = atacante
        self.defensor = defensor
        self.danio = danio
        self.tipo_ataque = tipo_ataque
        self.vida_defensor_restante = vida_defensor_restante
        self.mana_usado = mana_usado
        self.mana_restante_atacante = mana_restante_atacante
        self.mana_restante_defensor = mana_restante_defensor

    def a_dict(self):
        """Convierte el turno en un diccionario para serialización."""
        return {
            "numero": self.numero,
            "atacante": self.atacante,
            "defensor": self.defensor,
            "danio": self.danio,
            "tipo_ataque": self.tipo_ataque,
            "vida_defensor_restante": self.vida_defensor_restante,
            "mana_usado": self.mana_usado,
            "mana_restante_atacante": self.mana_restante_atacante,
            "mana_restante_defensor": self.mana_restante_defensor,
        }


class ResultadoCombate:
    """Representa el resultado completo de un combate."""

    def __init__(
        self, p1, p2, turnos, ganador, perdedor, vida1_final=None, vida2_final=None
    ):
        self.p1 = p1
        self.p2 = p2
        self.turnos = turnos
        self.ganador = ganador
        self.perdedor = perdedor
        self.vida1_final = vida1_final
        self.vida2_final = vida2_final

    @property
    def turnos_json(self):
        """Devuelve los turnos en formato JSON para uso en frontend."""
        return json.dumps([t.a_dict() for t in self.turnos])

    def a_dict(self):
        """Convierte todo el resultado del combate a diccionario."""
        return {
            "personaje1": self.p1,
            "personaje2": self.p2,
            "turnos": [t.a_dict() for t in self.turnos],
            "ganador": self.ganador,
            "perdedor": self.perdedor,
            "vida1_final": self.vida1_final,
            "vida2_final": self.vida2_final,
        }


def simular_combate(
    personaje1_id, personaje2_id, usar_especial_p1=True, usar_especial_p2=True
):
    """
    Simula un combate entre dos personajes y genera un registro completo de turnos.
    La función mantiene exactamente el mismo formato de salida y nombres de atributos.
    """
    # Obtener personajes
    p1 = Personaje.objects.obtener_por_id(personaje1_id)
    p2 = Personaje.objects.obtener_por_id(personaje2_id)

    if not p1:
        raise ValueError(f"Personaje con ID {personaje1_id} no encontrado")
    if not p2:
        raise ValueError(f"Personaje con ID {personaje2_id} no encontrado")

    # Guardar valores iniciales
    def init_personaje(p):
        return {
            "vida_inicial": p.vida,
            "mana_inicial": p.mana if p.tipo == "MAGO" else None,
            "armadura_inicial": p.armadura if p.tipo == "GUERRERO" else None,
            "precision_inicial": p.precision if p.tipo == "ARQUERO" else None,
        }

    p1_data = init_personaje(p1)
    p2_data = init_personaje(p2)

    turnos = []
    numero_turno = 1

    # Función interna para procesar un turno
    def ejecutar_turno(atacante, defensor, usar_especial):
        """
        Devuelve TurnoCombate tras aplicar ataque y actualizar vida/mana.
        """
        tipo_ataque = "normal"
        mana_usado = 0

        # Determinar daño: ataque normal o especial
        if atacante.tipo == "MAGO" and atacante.mana >= 10 and usar_especial:
            danio = atacante.ataque_especial()
            tipo_ataque = "especial"
            mana_usado = 10
        else:
            danio = atacante.ataque()

        # Aplicar daño si es mayor a 0
        if danio > 0:
            defensor.recibir_danio(danio)
            if defensor.vida == 0:
                defensor.vivo = False

        # Crear registro de turno
        return TurnoCombate(
            numero=numero_turno,
            atacante=atacante.nombre,
            defensor=defensor.nombre,
            danio=danio,
            tipo_ataque=tipo_ataque,
            vida_defensor_restante=defensor.vida,
            mana_usado=mana_usado,
            mana_restante_atacante=atacante.mana if atacante.tipo == "MAGO" else None,
            mana_restante_defensor=defensor.mana if defensor.tipo == "MAGO" else None,
        )

    # Bucle principal de combate
    while p1.esta_vivo() and p2.esta_vivo():
        # Turno p1
        turnos.append(ejecutar_turno(p1, p2, usar_especial_p1))
        if not p2.esta_vivo():
            break

        # Turno p2
        turnos.append(ejecutar_turno(p2, p1, usar_especial_p2))
        if not p1.esta_vivo():
            break

        numero_turno += 1

    # Vida y mana final
    final_p1_vida, final_p2_vida = p1.vida, p2.vida
    final_p1_mana = p1.mana if p1.tipo == "MAGO" else None
    final_p2_mana = p2.mana if p2.tipo == "MAGO" else None

    # Determinar ganador/perdedor
    ganador, perdedor = (p1, p2) if p1.esta_vivo() else (p2, p1)

    # Retornar resultado completo
    def calc_mana_pct(mana, mana_max):
        if mana is None or mana_max is None or mana_max == 0:
            return 0
        return (mana / mana_max) * 100

    p1_mana_max = p1_data["mana_inicial"]
    p2_mana_max = p2_data["mana_inicial"]

    return ResultadoCombate(
        p1={
            "id": p1.id,
            "nombre": p1.nombre,
            "tipo": p1.tipo,
            "vida": p1_data["vida_inicial"],
            "vida_max": p1.vida_max,
            "mana": (
                p1_data["mana_inicial"] if p1_data["mana_inicial"] is not None else 0
            ),
            "mana_max": p1_mana_max if p1_mana_max is not None else 0,
            "mana_pct": calc_mana_pct(p1_data["mana_inicial"], p1_mana_max),
            "armadura": (
                p1_data["armadura_inicial"]
                if p1_data["armadura_inicial"] is not None
                else 0
            ),
            "precision": (
                p1_data["precision_inicial"]
                if p1_data["precision_inicial"] is not None
                else 0
            ),
        },
        p2={
            "id": p2.id,
            "nombre": p2.nombre,
            "tipo": p2.tipo,
            "vida": p2_data["vida_inicial"],
            "vida_max": p2.vida_max,
            "mana": (
                p2_data["mana_inicial"] if p2_data["mana_inicial"] is not None else 0
            ),
            "mana_max": p2_mana_max if p2_mana_max is not None else 0,
            "mana_pct": calc_mana_pct(p2_data["mana_inicial"], p2_mana_max),
            "armadura": (
                p2_data["armadura_inicial"]
                if p2_data["armadura_inicial"] is not None
                else 0
            ),
            "precision": (
                p2_data["precision_inicial"]
                if p2_data["precision_inicial"] is not None
                else 0
            ),
        },
        turnos=turnos,
        ganador={"id": ganador.id, "nombre": ganador.nombre},
        perdedor={"id": perdedor.id, "nombre": perdedor.nombre},
        vida1_final=final_p1_vida,
        vida2_final=final_p2_vida,
    )


def guardar_resultado_combate(p1_id, p2_id, vida1_final, vida2_final):
    """
    Guarda el resultado del combate en la base de datos.
    Actualiza la vida de los personajes después del combate.
    """
    p1 = Personaje.objects.obtener_por_id(p1_id)
    p2 = Personaje.objects.obtener_por_id(p2_id)

    if p1:
        p1.vida = vida1_final
        if p1.vida <= 0:
            p1.vivo = False
        p1.save()

    if p2:
        p2.vida = vida2_final
        if p2.vida <= 0:
            p2.vivo = False
        p2.save()
