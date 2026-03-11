from app.models import Personaje, get_personaje_tipo


def crear_personaje(tipo, nombre, nivel=1, vida=None, vida_max=None, **kwargs):
    """
    Crea un nuevo personaje en la base de datos según su tipo.

    Parameters
    ----------
    tipo : str
        Tipo de personaje ('PERSONAJE', 'GUERRERO', 'MAGO', 'ARQUERO').
    nombre : str
        Nombre identificativo del personaje.
    nivel : int, optional
        Nivel inicial del personaje (por defecto 1).
    vida : int, optional
        Puntos de vida actuales.
    vida_max : int, optional
        Puntos de vida máximos.
    **kwargs : dict
        Argumentos adicionales según el tipo de personaje:
        - Guerrero: armadura
        - Mago: mana
        - Arquero: precision

    Returns
    -------
    Personaje
        Instancia del personaje creado.

    Raises
    ------
    ValueError
        Si el tipo no es válido.
    """
    tipo = get_personaje_tipo(tipo)

    # Crear el personaje según su tipo, usando valores por defecto si no se proporcionan
    if tipo == "GUERRERO":
        return Personaje.objects.create(
            tipo="GUERRERO",
            nombre=nombre,
            nivel=nivel,
            vida=vida,
            vida_max=vida_max,
            armadura=kwargs.get("armadura", 5),
            mana=None,
            precision=None,
        )
    elif tipo == "MAGO":
        return Personaje.objects.create(
            tipo="MAGO",
            nombre=nombre,
            nivel=nivel,
            vida=vida,
            vida_max=vida_max,
            armadura=None,
            mana=kwargs.get("mana", 50),
            precision=None,
        )
    elif tipo == "ARQUERO":
        return Personaje.objects.create(
            tipo="ARQUERO",
            nombre=nombre,
            nivel=nivel,
            vida=vida,
            vida_max=vida_max,
            armadura=None,
            mana=None,
            precision=kwargs.get("precision", 80),
        )
    elif tipo == "PERSONAJE":
        return Personaje.objects.create(
            tipo="PERSONAJE",
            nombre=nombre,
            nivel=nivel,
            vida=vida,
            vida_max=vida_max,
            armadura=None,
            mana=None,
            precision=None,
        )
    else:
        raise ValueError(f"Tipo de personaje desconocido: {tipo}")


def obtener_personaje(personaje_id):
    """
    Obtiene un personaje por su ID.

    Parameters
    ----------
    personaje_id : int
        id del personaje.

    Returns
    -------
    Personaje | None
        Instancia del personaje o None si no existe.
    """
    return Personaje.objects.obtener_por_id(personaje_id)


def listar_personajes():
    """
    Lista todos los personajes de la base de datos.

    Returns
    -------
    QuerySet
        Conjunto de todos los personajes ordenados por nombre.
    """
    return Personaje.objects.listar_todos()


def actualizar_personaje(personaje_id, **kwargs):
    """
    Actualiza los atributos de un personaje existente.

    Parameters
    ----------
    personaje_id : int
        id del personaje a actualizar.
    **kwargs : dict
        Campos y valores a actualizar.

    Returns
    -------
    Personaje | None
        Instancia actualizada del personaje, o None si no existe.
    """
    personaje = obtener_personaje(personaje_id)
    if not personaje:
        return None

    # Asignar los valores proporcionados solo si existen como atributos
    for key, value in kwargs.items():
        if hasattr(personaje, key):
            setattr(personaje, key, value)

    personaje.save()
    return personaje


def borrar_personaje(personaje_id):
    """
    Elimina un personaje de la base de datos.

    Parameters
    ----------
    personaje_id : int
        id del personaje a eliminar.

    Returns
    -------
    bool
        True si se eliminó correctamente, False si no existía.
    """
    personaje = obtener_personaje(personaje_id)
    if not personaje:
        return False

    personaje.delete()
    return True


def personaje_a_dict(personaje):
    """
    Convierte una instancia de personaje en un diccionario.

    Incluye atributos específicos según el tipo de personaje.

    Parameters
    ----------
    personaje : Personaje
        Instancia del modelo Personaje.

    Returns
    -------
    dict
        Diccionario con los atributos del personaje.
    """
    data = {
        "id": personaje.id,
        "tipo": personaje.tipo,
        "nombre": personaje.nombre,
        "nivel": personaje.nivel,
        "vida": personaje.vida,
        "vida_max": personaje.vida_max,
    }

    if personaje.tipo == "GUERRERO":
        data["armadura"] = personaje.armadura
    elif personaje.tipo == "MAGO":
        data["mana"] = personaje.mana
    elif personaje.tipo == "ARQUERO":
        data["precision"] = personaje.precision

    return data


def dict_a_personaje(data):
    """
    Crea una instancia de Personaje a partir de un diccionario.

    Parameters
    ----------
    data : dict
        Diccionario con los atributos del personaje.

    Returns
    -------
    Personaje
        Instancia del modelo Personaje (no guardada en BD).
    """
    tipo = get_personaje_tipo(data.get("tipo", "PERSONAJE"))

    return Personaje(
        id=data.get("id"),
        tipo=tipo,
        nombre=data.get("nombre"),
        nivel=data.get("nivel", 1),
        vida=data.get("vida"),
        vida_max=data.get("vida_max"),
        armadura=data.get("armadura") if tipo == "GUERRERO" else None,
        mana=data.get("mana") if tipo == "MAGO" else None,
        precision=data.get("precision") if tipo == "ARQUERO" else None,
    )
