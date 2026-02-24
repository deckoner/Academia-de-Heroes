from __future__ import annotations
from .personaje import Personaje

class Guerrero(Personaje):
    """
    Subclase especializada de Personaje centrada en resistencia y armadura.
    
    A diferencia del personaje base, un Guerrero mitigará el daño entrante
    dependiendo de su nivel de armadura.
    """
    def __init__(self, nombre: str, nivel: int = 1, vida: int = None, vida_max: int = None, armadura: int = 5, id: int = None):
        """
        Inicializa una nueva instancia de Guerrero.

        Args:
            nombre (str): Nombre del guerrero.
            nivel (int, opcional): Nivel del guerrero. Por defecto 1.
            vida (int, opcional): Vida actual. Si no se provee, asume vida máxima.
            vida_max (int, opcional): Límite superior de vida.
            armadura (int, opcional): Puntos de daño reducidos por cada ataque entrante. Por defecto 5.
            id (int, opcional): Identificador único en base de datos.
            
        Raises:
            ValueError: Si la armadura ingresada es negativa.
        """
        super().__init__(nombre, nivel, vida, vida_max, id)
        if armadura < 0:
            raise ValueError("La armadura no puede ser un valor negativo.")
        self.armadura = armadura

    def recibir_danio(self, cantidad: int):
        """
        Procesa el daño entrante, restando la armadura del daño total a recibir.
        El daño no puede ser mitigado por debajo de 0.

        Args:
            cantidad (int): Puntos de daño entrantes brutos del atacante.
        """
        danio_efectivo = max(0, cantidad - self.armadura)
        super().recibir_danio(danio_efectivo)

    def to_dict(self) -> dict:
        """
        Serializa al Guerrero, incluyendo su característica específica (armadura).

        Returns:
            dict: Representación del guerrero en diccionario, útil para bases de datos.
        """
        data = super().to_dict()
        data["tipo"] = "GUERRERO"
        data["armadura"] = self.armadura
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Guerrero:
        """
        Genera una instancia de Guerrero utilizando su representación en diccionario.

        Args:
            data (dict): Información del guerrero, generalmente proveniente de base de datos.

        Returns:
            Guerrero: Una nueva instancia parametrizada.
        """
        return cls(
            id=data.get("id"),
            nombre=data.get("nombre"),
            nivel=data.get("nivel", 1),
            vida=data.get("vida"),
            vida_max=data.get("vida_max"),
            armadura=data.get("armadura", 5)
        )
