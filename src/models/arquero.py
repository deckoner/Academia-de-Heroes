from __future__ import annotations
import random
from .personaje import Personaje

class Arquero(Personaje):
    """
    Subclase enfocada en ataques precisos pero aleatorios.
    
    Un Arquero puede golpear o fallar su ataque por completo basándose 
    estrictamente en su probabilidad natural de precisión de rango.
    """
    def __init__(self, nombre: str, nivel: int = 1, vida: int = None, vida_max: int = None, precision: int = 80, id: int = None):
        """
        Método de construcción del Arquero.

        Args:
            nombre (str): Título con el cual se identifica al arquero.
            nivel (int, opcional): Nivel de impacto que condiciona daño y base de vida máxima.
            vida (int, opcional): Puntos de vida reales en tiempo vivo.
            vida_max (int, opcional): Límite infranqueable de puntos de vida de la clase.
            precision (int, opcional): Valor porcentual entre 0 y 100 de acertar un proyectil. Por defecto 80.
            id (int, opcional): Identificador de seguimiento para sistema CRUD.

        Raises:
            ValueError: Excepción lanzada si precisión no se ajusta entre el 0 y el 100.
        """
        super().__init__(nombre, nivel, vida, vida_max, id)
        if not (0 <= precision <= 100):
            raise ValueError("La cualidad de precisión debe comprender valores estrictos de 0 a 100.")
        self.precision = precision

    def ataque(self) -> int:
        """
        Ejecuta el daño general mediante el motor probabilístico basado en su propia precisión.

        Returns:
            int: Puntos totales de ataque que aplican daño al objetivo, o 0 si falla el tiro.
        """
        probabilidad = random.randint(1, 100)
        if probabilidad <= self.precision:
            return super().ataque()
        else:
            print(f"El arquero {self.nombre} falló críticamente el tiro.")
            return 0

    def to_dict(self) -> dict:
        """
        Transformación técnica de la clase actual a un objeto manipulable global.

        Returns:
            dict: Variables primordiales de la entidad en formato diccionario Python clásico.
        """
        data = super().to_dict()
        data["tipo"] = "ARQUERO"
        data["precision"] = self.precision
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Arquero:
        """
        Proceso inverso funcional: recrea una instancia validable Arquero.

        Args:
            data (dict): Diccionario simple con campos primitivos recuperados.

        Returns:
            Arquero: Objeto restaurado preparado para el entorno del software.
        """
        return cls(
            id=data.get("id"),
            nombre=data.get("nombre"),
            nivel=data.get("nivel", 1),
            vida=data.get("vida"),
            vida_max=data.get("vida_max"),
            precision=data.get("precision", 80)
        )
