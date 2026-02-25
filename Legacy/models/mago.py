from __future__ import annotations
from .personaje import Personaje

class Mago(Personaje):
    """
    Subclase especializada de Personaje basada en daño mágico.
    
    El Mago posee un atributo adicional llamado 'mana' que, cuando es consumido,
    permite lanzar ataques especiales que multiplican su daño natural.
    """
    def __init__(self, nombre: str, nivel: int = 1, vida: int = None, vida_max: int = None, mana: int = 50, id: int = None):
        """
        Inicializa un personaje Mago.

        Args:
            nombre (str): Nombre identificativo.
            nivel (int, opcional): Nivel base, inicializa en 1.
            vida (int, opcional): Puntos de vida actuales de la entidad.
            vida_max (int, opcional): Límite superior de vida.
            mana (int, opcional): Energía mágica que rige los ataques especiales. Por defecto 50.
            id (int, opcional): Identificador para la persistencia de datos.

        Raises:
            ValueError: En caso de recibir un mana base negativo.
        """
        super().__init__(nombre, nivel, vida, vida_max, id)
        if mana < 0:
            raise ValueError("El mana inicial o actual no puede ser un número negativo.")
        self.mana = mana

    def ataque_especial(self) -> int:
        """
        Ejecuta una habilidad especial con daño crítico.
        Consume 10 unidades de mana para efectuar un daño equivalente al doble del ataque normal.

        Returns:
            int: Cantidad de daño generado. Si no dispone de mana suficiente retorna 0.
        """
        if self.mana >= 10:
            self.mana -= 10
            danio = self.ataque() * 2
            print(f"{self.nombre} lanza un hechizo! Daño crítico: {danio}. Mana restante: {self.mana}")
            return danio
        else:
            print(f"El personaje {self.nombre} no dispone de mana para este ataque.")
            return 0

    def to_dict(self) -> dict:
        """
        Prepara los datos del Mago en un formato exportable estándar.

        Returns:
            dict: Objeto convertida para uso rápido en JSON o Base de datos.
        """
        data = super().to_dict()
        data["tipo"] = "MAGO"
        data["mana"] = self.mana
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Mago:
        """
        Decodifica un diccionario de vuelta hacia una clase funcional Mago.

        Args:
            data (dict): Información guardada del Mago en forma de diccionario simple.

        Returns:
            Mago: Representación íntegra de la clase cargada.
        """
        return cls(
            id=data.get("id"),
            nombre=data.get("nombre"),
            nivel=data.get("nivel", 1),
            vida=data.get("vida"),
            vida_max=data.get("vida_max"),
            mana=data.get("mana", 50)
        )
