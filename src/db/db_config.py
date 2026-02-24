from __future__ import annotations
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "academia.db"

def get_connection() -> sqlite3.Connection:
    """
    Establece y configura una nueva sesión con el motor de SQLite.
    
    Activa por defecto las llaves foráneas e instructores de configuración
    como el empaquetado directo de las filas en formato diccionarios 
    mediante sqlite3.Row.

    Returns:
        sqlite3.Connection: Instancia configurada y lista para lanzar peticiones.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
