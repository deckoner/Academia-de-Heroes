from django.db.models import Count, Avg
from datetime import date
from app.models import Usuario, Personaje, Batalla


def clases_mas_seleccionadas():
    """
    Obtiene las clases mas seleccionadas por los usuarios.

    Returns
    -------
    list
        Lista de tuplas (clase, cantidad) ordenadas por cantidad descendente.
    """
    tipos_count = (
        Personaje.objects.exclude(tipo="PERSONAJE")
        .values("tipo")
        .annotate(cantidad=Count("id"))
        .order_by("-cantidad")
    )

    result = []
    for item in tipos_count:
        tipo_display = dict(Personaje.TIPO_CHOICES).get(item["tipo"], item["tipo"])
        result.append((tipo_display, item["cantidad"]))

    return result


def clases_ganadoras_mas_combates():
    """
    Obtiene las clases que han ganado mas combates.

    Returns
    -------
    list
        Lista de tuplas (clase, victorias) ordenadas por victorias descendente.
    """
    usuarios_mayores = _obtener_usuarios_mayores()
    usuario_ids = [u.id for u in usuarios_mayores]

    if not usuario_ids:
        return []

    victories = {tipo: 0 for tipo in ["GUERRERO", "MAGO", "ARQUERO"]}

    batallas = Batalla.objects.filter(
        resultado__isnull=False, id_atacante_id__in=usuario_ids
    ).select_related("personaje_atacante", "personaje_defensor")

    for batalla in batallas:
        tipo_atacante = batalla.personaje_atacante.tipo
        tipo_defensor = batalla.personaje_defensor.tipo

        if tipo_atacante == "PERSONAJE" or tipo_defensor == "PERSONAJE":
            continue

        if batalla.resultado:
            victories[tipo_atacante] += 1
        else:
            victories[tipo_defensor] += 1

    result = [
        (dict(Personaje.TIPO_CHOICES).get(tipo, tipo), int(cantidad))
        for tipo, cantidad in victories.items()
    ]
    result.sort(key=lambda x: x[1], reverse=True)
    return result


def clases_mas_entrenadas():
    """
    Obtiene las clases mas entrenadas (mayor nivel promedio por clase).

    Returns
    -------
    list
        Lista de tuplas (clase, nivel_promedio) ordenadas por nivel descendente.
    """
    usuarios_mayores = _obtener_usuarios_mayores()
    usuario_ids = [u.id for u in usuarios_mayores]

    if not usuario_ids:
        return []

    tipos_nivel = (
        Personaje.objects.exclude(tipo="PERSONAJE")
        .filter(id_usuario_id__in=usuario_ids)
        .values("tipo")
        .annotate(nivel_promedio=Avg("nivel"))
        .order_by("-nivel_promedio")
    )

    return [
        (
            dict(Personaje.TIPO_CHOICES).get(item["tipo"], item["tipo"]),
            int(item["nivel_promedio"]),
        )
        for item in tipos_nivel
    ]


def ranking_personajes_estadisticas():
    """
    Obtiene el ranking de personajes basado en las batallas.

    Returns
    -------
    list
        Lista de diccionarios con datos serializables del personaje (maximo 10).
    """
    usuarios_mayores = _obtener_usuarios_mayores()
    usuario_ids = {u.id for u in usuarios_mayores}

    if not usuario_ids:
        return []

    personajes = Personaje.objects.filter(id_usuario_id__in=usuario_ids)
    personaje_ids = list(personajes.values_list("id", flat=True))

    if not personaje_ids:
        return []

    victories = {pid: 0 for pid in personaje_ids}

    batallas = Batalla.objects.filter(
        resultado__isnull=False, id_atacante_id__in=usuario_ids
    ).select_related("personaje_atacante", "personaje_defensor")

    for batalla in batallas:
        if batalla.resultado:
            victories[batalla.personaje_atacante_id] = (
                victories.get(batalla.personaje_atacante_id, 0) + 1
            )
        else:
            victories[batalla.personaje_defensor_id] = (
                victories.get(batalla.personaje_defensor_id, 0) + 1
            )

    ranking_list = [
        {
            "nombre": p.nombre,
            "usuario": p.id_usuario.user.username,
            "tipo": dict(Personaje.TIPO_CHOICES).get(p.tipo, p.tipo),
            "nivel": p.nivel,
            "victorias": victories.get(p.id, 0),
        }
        for p in personajes
    ]
    ranking_list.sort(key=lambda x: x["victorias"], reverse=True)
    return ranking_list[:10]


def promedio_batallas_por_usuario():
    """
    Obtiene el promedio de batallas por usuario.

    Returns
    -------
    dict
        Diccionario con el promedio de batallas por usuario.
    """
    usuarios_mayores = _obtener_usuarios_mayores()
    usuario_ids = [u.id for u in usuarios_mayores]

    if not usuario_ids:
        return {"promedio": 0, "total_batallas": 0, "total_usuarios": 0}

    total_batallas = Batalla.objects.filter(id_atacante_id__in=usuario_ids).count()
    total_usuarios = len(usuario_ids)
    promedio = round(total_batallas / total_usuarios, 1) if total_usuarios > 0 else 0

    return {
        "promedio": promedio,
        "total_batallas": total_batallas,
        "total_usuarios": total_usuarios,
    }


def usuarios_por_edad():
    """
    Obtiene el porcentaje de usuarios por rango de edad.

    Returns
    -------
    list
        Lista de diccionarios con rango de edad y cantidad.
    """
    usuarios = Usuario.objects.filter(fecha_nacimiento__isnull=False)

    rangos = {"Menores": 0, "18-25": 0, "26-35": 0, "36-50": 0, "Mayores de 50": 0}

    for usuario in usuarios:
        edad = _calcular_edad(usuario.fecha_nacimiento)
        if edad < 18:
            rangos["Menores"] += 1
        elif edad <= 25:
            rangos["18-25"] += 1
        elif edad <= 35:
            rangos["26-35"] += 1
        elif edad <= 50:
            rangos["36-50"] += 1
        else:
            rangos["Mayores de 50"] += 1

    total = sum(rangos.values())
    return [
        {
            "rango": rango,
            "cantidad": cantidad,
            "porcentaje": round((cantidad / total * 100), 1) if total > 0 else 0,
        }
        for rango, cantidad in rangos.items()
    ]


def distribucion_niveles():
    """
    Obtiene la distribucion de niveles de los personajes por clase.
    Muestra los niveles de cada clase para comparar.

    Returns
    -------
    dict
        Diccionario con niveles por clase y outliers.
    """
    usuarios_mayores = _obtener_usuarios_mayores()
    usuario_ids = [u.id for u in usuarios_mayores]

    if not usuario_ids:
        return {"por_clase": {}, "outliers": []}

    personajes = Personaje.objects.filter(id_usuario_id__in=usuario_ids).select_related(
        "id_usuario"
    )

    por_clase = {"GUERRERO": [], "MAGO": [], "ARQUERO": []}
    outliers = []

    for p in personajes:
        if p.tipo in por_clase:
            por_clase[p.tipo].append(p.nivel)

    for tipo, niveles in por_clase.items():
        if not niveles:
            continue

        niveles.sort()
        n = len(niveles)

        if n < 4:
            continue

        q1_index = n // 4
        q3_index = (3 * n) // 4
        q1, q3 = niveles[q1_index], niveles[q3_index]
        iqr = q3 - q1
        limite_inferior = max(0, q1 - 1.5 * iqr)
        limite_superior = q3 + 1.5 * iqr

        por_clase[tipo] = [
            n for n in niveles if limite_inferior <= n <= limite_superior
        ]

    return {
        "por_clase": {
            dict(Personaje.TIPO_CHOICES).get(k, k): v for k, v in por_clase.items() if v
        },
        "outliers": outliers,
    }


def _calcular_edad(fecha_nacimiento):
    """
    Calcula la edad a partir de la fecha de nacimiento.

    Parameters
    ----------
    fecha_nacimiento : date
        Fecha de nacimiento del usuario.

    Returns
    -------
    int
        Edad del usuario en anos.
    """
    today = date.today()
    edad = (
        today.year
        - fecha_nacimiento.year
        - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    )
    return edad


def _obtener_usuarios_mayores():
    """
    Obtiene los usuarios mayores de edad usando el manager del modelo.

    Returns
    -------
    list
        Lista de instancias de Usuario mayores de edad.
    """
    usuarios = Usuario.objects.filter(fecha_nacimiento__isnull=False)
    return [u for u in usuarios if Usuario.objects.es_mayor_de_edad(u.id)]


def todas_las_estadisticas():
    """
    Obtiene todas las estadisticas para mostrar en la pagina.

    Returns
    -------
    dict
        Diccionario con todas las estadisticas.
    """
    return {
        "clases_seleccionadas": clases_mas_seleccionadas(),
        "clases_ganadoras": clases_ganadoras_mas_combates(),
        "ranking_personajes": ranking_personajes_estadisticas(),
        "promedio_batallas": promedio_batallas_por_usuario(),
        "clases_entrenadas": clases_mas_entrenadas(),
        "usuarios_por_edad": usuarios_por_edad(),
        "distribucion_niveles": distribucion_niveles(),
    }
