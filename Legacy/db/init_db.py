from __future__ import annotations
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]   # .../academia_heroes
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "academia.db"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")

def init_db() -> Path:
    """
    Prepara e inicializa la base de datos estructural del juego.
    
    Verifica los directorios de datos y despliega el esquema SQL primario,
    creando las tablas subyacentes necesarias para el sistema de personajes si 
    estas aún no existieran en la ejecución actual.

    Returns:
        Path: Una ruta local absolutizada señalando hacia el archivo de la base de datos.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema)
        conn.commit()

    return DB_PATH

if __name__ == "__main__":
    path = init_db()
    print(f"Base de datos inicializada de manera exitosa en: {path}")
