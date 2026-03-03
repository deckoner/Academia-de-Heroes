"""
Servicio para gestionar las operaciones CRUD de personajes.
Proporciona una capa de abstraccion sobre los modelos de Django.
"""
from app.models import Personaje, get_personaje_tipo


def crear_personaje(tipo, nombre, nivel=1, vida=None, vida_max=None, **kwargs):
    """
    Crea un nuevo personaje en la base de datos.
    
    Args:
        tipo: Tipo de personaje ('PERSONAJE', 'GUERRERO', 'MAGO', 'ARQUERO').
        nombre: Nombre identificativo del personaje.
        nivel: Nivel inicial del personaje (por defecto 1).
        vida: Puntos de vida actuales.
        vida_max: Puntos de vida maximos.
        **kwargs: Argumentos adicionales segun el tipo de personaje.
            - Guerrero: armadura
            - Mago: mana
            - Arquero: precision
            
    Returns:
        Instancia del personaje creado.
        
    Raises:
        ValueError: Si el tipo no es valido o los datos son invalidos.
    """
    tipo = get_personaje_tipo(tipo)
    
    if tipo == 'GUERRERO':
        return Personaje.objects.create(
            tipo='GUERRERO',
            nombre=nombre,
            nivel=nivel,
            vida=vida,
            vida_max=vida_max,
            armadura=kwargs.get('armadura', 5),
            mana=None,
            precision=None
        )
    elif tipo == 'MAGO':
        return Personaje.objects.create(
            tipo='MAGO',
            nombre=nombre,
            nivel=nivel,
            vida=vida,
            vida_max=vida_max,
            armadura=None,
            mana=kwargs.get('mana', 50),
            precision=None
        )
    elif tipo == 'ARQUERO':
        return Personaje.objects.create(
            tipo='ARQUERO',
            nombre=nombre,
            nivel=nivel,
            vida=vida,
            vida_max=vida_max,
            armadura=None,
            mana=None,
            precision=kwargs.get('precision', 80)
        )
    elif tipo == 'PERSONAJE':
        return Personaje.objects.create(
            tipo='PERSONAJE',
            nombre=nombre,
            nivel=nivel,
            vida=vida,
            vida_max=vida_max,
            armadura=None,
            mana=None,
            precision=None
        )
    else:
        raise ValueError(f"Tipo de personaje desconocido: {tipo}")


def obtener_personaje(personaje_id):
    """
    Obtiene un personaje por su identificador unico.
    
    Args:
        personaje_id: Identificador numerico del personaje.
        
    Returns:
        Instancia de Personaje o None si no existe.
    """
    return Personaje.objects.obtener_por_id(personaje_id)


def listar_personajes():
    """
    Lista todos los personajes de la base de datos.
    
    Returns:
        QuerySet con todos los personajes ordenados por nombre.
    """
    return Personaje.objects.listar_todos()


def actualizar_personaje(personaje_id, **kwargs):
    """
    Actualiza los datos de un personaje existente.
    
    Args:
        personaje_id: Identificador del personaje a actualizar.
        **kwargs: Campos a actualizar.
        
    Returns:
        Instancia del personaje actualizado o None si no existe.
    """
    personaje = obtener_personaje(personaje_id)
    if not personaje:
        return None
    
    for key, value in kwargs.items():
        if hasattr(personaje, key):
            setattr(personaje, key, value)
    
    personaje.save()
    return personaje


def borrar_personaje(personaje_id):
    """
    Elimina un personaje de la base de datos.
    
    Args:
        personaje_id: Identificador del personaje a eliminar.
        
    Returns:
        True si se elimino correctamente, False si no existia.
    """
    personaje = obtener_personaje(personaje_id)
    if not personaje:
        return False
    
    personaje.delete()
    return True


def personaje_a_dict(personaje):
    """
    Convierte una instancia de personaje a un diccionario.
    
    Args:
        personaje: Instancia del modelo Personaje.
        
    Returns:
        Diccionario con los datos del personaje.
    """
    data = {
        'id': personaje.id,
        'tipo': personaje.tipo,
        'nombre': personaje.nombre,
        'nivel': personaje.nivel,
        'vida': personaje.vida,
        'vida_max': personaje.vida_max,
    }
    
    if personaje.tipo == 'GUERRERO':
        data['armadura'] = personaje.armadura
    elif personaje.tipo == 'MAGO':
        data['mana'] = personaje.mana
    elif personaje.tipo == 'ARQUERO':
        data['precision'] = personaje.precision
    
    return data


def dict_a_personaje(data):
    """
    Crea una instancia de personaje a partir de un diccionario.
    
    Args:
        data: Diccionario con los datos del personaje.
        
    Returns:
        Instancia del modelo correspondiente.
    """
    tipo = get_personaje_tipo(data.get('tipo', 'PERSONAJE'))
    
    return Personaje(
        id=data.get('id'),
        tipo=tipo,
        nombre=data.get('nombre'),
        nivel=data.get('nivel', 1),
        vida=data.get('vida'),
        vida_max=data.get('vida_max'),
        armadura=data.get('armadura') if tipo == 'GUERRERO' else None,
        mana=data.get('mana') if tipo == 'MAGO' else None,
        precision=data.get('precision') if tipo == 'ARQUERO' else None,
    )
