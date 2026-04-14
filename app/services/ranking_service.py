from datetime import date
from app.models import Usuario, Personaje, Batalla


def es_mayor_de_edad(usuario):
    """
    Verifica si un usuario es mayor de edad.

    Parameters
    ----------
    usuario : Usuario
        Instancia del modelo Usuario.

    Returns
    -------
    bool
        True si el usuario tiene al menos 18 años, False en caso contrario.
    """
    if not usuario or not usuario.fecha_nacimiento:
        return False

    today = date.today()
    age = (
        today.year
        - usuario.fecha_nacimiento.year
        - (
            (today.month, today.day)
            < (usuario.fecha_nacimiento.month, usuario.fecha_nacimiento.day)
        )
    )

    return age >= 18


def es_mayor_de_edad_fecha(fecha_nacimiento):
    """
    Verifica si una fecha de nacimiento corresponde a un usuario mayor de edad.

    Parameters
    ----------
    fecha_nacimiento : date
        Fecha de nacimiento del usuario.

    Returns
    -------
    bool
        True si la fecha corresponde a alguien mayor de 18 años.
    """
    if not fecha_nacimiento:
        return False

    today = date.today()
    age = (
        today.year
        - fecha_nacimiento.year
        - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    )

    return age >= 18


def obtener_usuarios_mayores():
    """
    Obtiene todos los usuarios mayores de edad.

    Returns
    -------
    list
        Lista de ids de usuarios mayores de edad.
    """
    usuarios = Usuario.objects.select_related("user").filter(
        fecha_nacimiento__isnull=False
    )

    resultado = []
    for usuario in usuarios:
        if es_mayor_de_edad(usuario):
            resultado.append(usuario.id)

    return resultado


def ranking_usuarios():
    """
    Calcula el ranking de usuarios basado en las batallas.

    Solo se consideran usuarios mayores de edad para aparecer en el ranking.
    Las victorias se cuentan si el ganador (atacante o defensor) es mayor de edad.

    Returns
    -------
    list
        Lista de tuplas (usuario, victorias) ordenadas por victorias descendentes.
    """
    usuario_ids_mayores = set(obtener_usuarios_mayores())

    if not usuario_ids_mayores:
        return []

    victories = {uid: 0 for uid in usuario_ids_mayores}

    batallas = Batalla.objects.filter(resultado__isnull=False).select_related(
        "id_atacante", "id_defensor"
    )

    for batalla in batallas:
        attacker = batalla.id_atacante_id
        defender = batalla.id_defensor_id
        winner = attacker if batalla.resultado else defender

        if winner in usuario_ids_mayores:
            victories[winner] += 1

    usuarios = Usuario.objects.select_related("user").filter(id__in=usuario_ids_mayores)

    ranking_list = []
    for usuario in usuarios:
        ranking_list.append((usuario, victories.get(usuario.id, 0)))

    ranking_list.sort(key=lambda x: x[1], reverse=True)

    return ranking_list


def ranking_personajes():
    """
    Calcula el ranking de personajes basado en las batallas.

    Solo se consideran personajes de usuarios mayores de edad.
    Las victorias se cuentan si el personaje ganó (como atacante o defensor).

    Returns
    -------
    list
        Lista de tuplas (personaje, victorias) ordenadas por victorias descendentes.
    """
    usuario_ids_mayores = set(obtener_usuarios_mayores())

    if not usuario_ids_mayores:
        return []

    personajes = Personaje.objects.filter(id_usuario_id__in=usuario_ids_mayores)

    personaje_ids = list(personajes.values_list("id", flat=True))

    if not personaje_ids:
        return []

    victories = {pid: 0 for pid in personaje_ids}

    batallas = Batalla.objects.filter(resultado__isnull=False).select_related(
        "personaje_atacante", "personaje_defensor", "id_atacante", "id_defensor"
    )

    for batalla in batallas:
        attacker_user = batalla.id_atacante_id
        defender_user = batalla.id_defensor_id
        personaje_atacante_id = batalla.personaje_atacante_id
        personaje_defensor_id = batalla.personaje_defensor_id

        if batalla.resultado:
            if personaje_atacante_id in personaje_ids:
                victories[personaje_atacante_id] += 1
        else:
            if personaje_defensor_id in personaje_ids:
                victories[personaje_defensor_id] += 1

    ranking_list = []
    for personaje in personajes:
        ranking_list.append((personaje, victories.get(personaje.id, 0)))

    ranking_list.sort(key=lambda x: x[1], reverse=True)

    return ranking_list
