from .personaje import Personaje, PersonajeManager


def get_personaje_tipo(tipo):
    """
    Obtiene el tipo de personaje correspondiente al tipo especificado.

    Args:
        tipo: Cadena con el tipo de personaje ('PERSONAJE', 'GUERRERO', 'MAGO', 'ARQUERO').

    Returns:
        Tipo de personaje en mayusculas.

    Raises:
        ValueError: Si el tipo no es valido.
    """
    tipos_validos = ["PERSONAJE", "GUERRERO", "MAGO", "ARQUERO"]
    tipo_upper = tipo.upper() if tipo else "PERSONAJE"
    if tipo_upper not in tipos_validos:
        raise ValueError(f"Tipo de personaje desconocido: {tipo}")
    return tipo_upper
