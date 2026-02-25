from .personaje import Personaje
from .guerrero import Guerrero
from .mago import Mago
from .arquero import Arquero

def personaje_from_dict(data: dict) -> Personaje:
    """
    Despachador condicional que invoca el método deserializador apropiado 
    para las clases dependientes del ecosistema Personaje.
    
    Dependiendo de la variable 'tipo' en el origen 'data', construye
    la subclase correcta retornando siempre un objeto polimórfico.

    Args:
        data (dict): Diccionario con al menos el campo "tipo", además 
                     de todos los atributos correspondientes de la entidad.

    Returns:
        Personaje: Una clase hija (Mago, Guerrero, Arquero) o un Personaje genérico.

    Raises:
        ValueError: Si la variable de tipo es inconsistente o inmanejable.
    """
    tipo = data.get("tipo", "PERSONAJE").upper()
    
    if tipo == "GUERRERO":
        return Guerrero.from_dict(data)
    elif tipo == "MAGO":
        return Mago.from_dict(data)
    elif tipo == "ARQUERO":
        return Arquero.from_dict(data)
    elif tipo == "PERSONAJE":
        return Personaje.from_dict(data)
    else:
        raise ValueError(f"El motor de construcción halló un tipo desconocido: {tipo}")
