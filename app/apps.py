from django.apps import AppConfig
import sqlite3
from pathlib import Path


class AcademiaHeroesConfig(AppConfig):
    """
    Configuración de la aplicación Django "app".

    Esta clase extiende `AppConfig` y permite ejecutar lógica personalizada
    cuando la aplicación es cargada por Django. En este caso, se encarga de
    inicializar la base de datos SQLite ejecutando un script SQL externo
    si este existe.

    Attributes
    ----------
    name : str
        Nombre interno de la aplicación dentro del proyecto Django.
    """

    name = 'app'

    def ready(self):
        """
        Método que se ejecuta automáticamente cuando la aplicación
        está completamente cargada por Django.
        """
        self.iniciar_db()

    @staticmethod
    def iniciar_db():
        """
        Inicializa la base de datos SQLite ejecutando un script SQL externo.
        El nombre del script sql es schema.sql

        Raises
        ------
        sqlite3.DatabaseError
            Si ocurre un error durante la ejecución del script SQL.
        IOError
            Si ocurre un problema al leer el archivo `schema.sql`.
        """
        from django.conf import settings

        db_path = settings.BASE_DIR / 'db.sqlite3'
        schema_path = Path(__file__).parent / 'schema.sql'

        if schema_path.exists():
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON;")
            schema = schema_path.read_text(encoding='utf-8')
            conn.executescript(schema)
            conn.commit()
            conn.close()