import sqlite3
from typing import List, Optional
from models import Personaje, personaje_from_dict

def insertar(conn: sqlite3.Connection, p: Personaje) -> int:
    """
    Registra un nuevo personaje en la base de datos persistente.

    Args:
        conn (sqlite3.Connection): Conexión activa a la base de datos de SQLite.
        p (Personaje): Objeto Personaje (o subclase) a ser insertado.

    Returns:
        int: El identificador único (ID) asignado al personaje post-inserción.
    """
    data = p.to_dict()
    query = """
    INSERT INTO personajes (tipo, nombre, nivel, vida, vida_max, armadura, mana, precision)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor = conn.cursor()
    cursor.execute(query, (
        p.to_dict()["tipo"],
        p.nombre,
        p.nivel,
        p.vida,
        p.vida_max,
        data.get("armadura"),
        data.get("mana"),
        data.get("precision")
    ))
    conn.commit()
    p.id = cursor.lastrowid
    return p.id

def actualizar(conn: sqlite3.Connection, p: Personaje):
    """
    Sobrescribe la información de un personaje pre-existente con nuevos valores.

    Args:
        conn (sqlite3.Connection): Conexión abierta hacia la base de datos.
        p (Personaje): Personaje con estado actualizado que ya posee un ID válido.

    Raises:
        ValueError: Si el personaje proporcionado carece de un atributo 'id' válido.
    """
    if p.id is None:
        raise ValueError("No se puede sincronizar o actualizar un personaje carente de ID.")
    
    data = p.to_dict()
    query = """
    UPDATE personajes 
    SET nombre = ?, nivel = ?, vida = ?, vida_max = ?, armadura = ?, mana = ?, precision = ?
    WHERE id = ?
    """
    conn.execute(query, (
        p.nombre,
        p.nivel,
        p.vida,
        p.vida_max,
        data.get("armadura"),
        data.get("mana"),
        data.get("precision"),
        p.id
    ))
    conn.commit()

def borrar(conn: sqlite3.Connection, personaje_id: int):
    """
    Elimina físicamente el registro de un personaje de la base de datos.

    Args:
        conn (sqlite3.Connection): Conexión estructurada de base de datos.
        personaje_id (int): ID correspondiente al personaje que será borrado.
    """
    conn.execute("DELETE FROM personajes WHERE id = ?", (personaje_id,))
    conn.commit()

def obtener_por_id(conn: sqlite3.Connection, personaje_id: int) -> Optional[Personaje]:
    """
    Busca, recopila y reconstruye a un personaje según su identificador único.

    Args:
        conn (sqlite3.Connection): Interfaz de conexión con SQLite.
        personaje_id (int): El ID numérico del personaje que se requiere encontrar.

    Returns:
        Optional[Personaje]: Una instancia con los datos recuperados, o None si no existe.
    """
    cursor = conn.execute("SELECT * FROM personajes WHERE id = ?", (personaje_id,))
    row = cursor.fetchone()
    if row:
        return personaje_from_dict(dict(row))
    return None

def listar(conn: sqlite3.Connection) -> List[Personaje]:
    """
    Retorna una colección iterable conteniendo todos los personajes almacenados.

    Args:
        conn (sqlite3.Connection): Transacción de conexión abierta.

    Returns:
        List[Personaje]: Una lista con múltiples instancias de la clase Personaje (o derivados).
    """
    cursor = conn.execute("SELECT * FROM personajes")
    return [personaje_from_dict(dict(row)) for row in cursor.fetchall()]
