from __future__ import annotations
import random

class Personaje:
    """
    Clase base que representa a un personaje dentro del juego.
    
    Proporciona los atributos y métodos fundamentales para el sistema de combate,
    experiencia y persistencia básica de datos.
    
    Attributes:
        vida_max_base (int): Valor base de la vida máxima para un personaje de nivel 1.
    """
    vida_max_base = 100

    def __init__(self, nombre: str, nivel: int = 1, vida: int = None, vida_max: int = None, id: int = None):
        """
        Inicializa una nueva instancia de Personaje.

        Args:
            nombre (str): El nombre identificativo del personaje.
            nivel (int, opcional): Nivel del personaje que determina su daño y vida. Por defecto es 1.
            vida (int, opcional): Puntos de vida actuales. Si no se provee, asume la vida máxima.
            vida_max (int, opcional): Puntos de vida máximos calculados según el nivel. 
            id (int, opcional): Identificador único de base de datos.
            
        Raises:
            ValueError: Si el nombre está vacío o si el nivel es menor a 1.
        """
        if not nombre or not isinstance(nombre, str):
            raise ValueError("El nombre debe ser una cadena no vacía.")
        if nivel < 1:
            raise ValueError("El nivel debe ser al menos 1.")
        
        self.id = id
        self.nombre = nombre
        self.nivel = nivel
        self.vida_max = vida_max if vida_max is not None else self.vida_max_base + (nivel - 1) * 10
        self.vida = vida if vida is not None else self.vida_max
        
        if self.vida < 0:
            self.vida = 0
        if self.vida > self.vida_max:
            self.vida = self.vida_max

    def esta_vivo(self) -> bool:
        """
        Verifica el estado actual del personaje.

        Returns:
            bool: True si la vida es mayor a cero, False en caso contrario.
        """
        return self.vida > 0

    def recibir_danio(self, cantidad: int):
        """
        Aplica daño directo a los puntos de vida del personaje.

        Args:
            cantidad (int): Puntos de daño a restar de la vida actual.

        Raises:
            ValueError: Si la cantidad de daño es un número negativo.
        """
        if cantidad < 0:
            raise ValueError("La cantidad de daño no puede ser negativa.")
        self.vida = max(0, self.vida - cantidad)
        print(f"{self.nombre} recibe {cantidad} de daño. Vida restante: {self.vida}/{self.vida_max}")

    def curar(self, cantidad: int):
        """
        Restaura puntos de vida del personaje hasta el máximo permitido.

        Args:
            cantidad (int): Puntos de vida a restaurar.

        Raises:
            ValueError: Si la cantidad de curación es un número negativo.
        """
        if cantidad < 0:
            raise ValueError("La cantidad de curación no puede ser negativa.")
        if not self.esta_vivo():
            print(f"{self.nombre} está derrotado y no puede ser curado.")
            return
        self.vida = min(self.vida_max, self.vida + cantidad)
        print(f"{self.nombre} se cura {cantidad} puntos. Vida: {self.vida}/{self.vida_max}")

    def subir_nivel(self):
        """
        Incrementa el nivel del personaje.
        
        Sube el nivel en 1 unidad, aumenta la vida máxima en 10 puntos fijos 
        y cura al personaje parcialmente (50% de su vida máxima).
        """
        self.nivel += 1
        incremento_vida = 10
        self.vida_max += incremento_vida
        self.vida = min(self.vida_max, self.vida + (self.vida_max // 2))
        print(f"{self.nombre} ha subido al nivel {self.nivel}. Vida máxima actual: {self.vida_max}")

    def ataque(self) -> int:
        """
        Calcula el daño base que inflige el personaje.

        Returns:
            int: Puntos de daño calculados como 10 más el nivel del personaje.
        """
        return 10 + self.nivel

    @staticmethod
    def simular_turno(atacante: Personaje, defensor: Personaje):
        """
        Ejecuta un turno de combate donde un personaje ataca al otro.

        Args:
            atacante (Personaje): La instancia que realiza el ataque.
            defensor (Personaje): La instancia que recibe el impacto.
        """
        print(f"\n--- Turno de {atacante.nombre} ---")
        danio = atacante.ataque()
        defensor.recibir_danio(danio)

    def to_dict(self) -> dict:
        """
        Serializa los datos primarios del personaje a un diccionario.
        Utilizado para su almacenamiento en base de datos o envío en formato JSON.

        Returns:
            dict: Representación del personaje en formato de diccionario.
        """
        return {
            "id": self.id,
            "tipo": "PERSONAJE",
            "nombre": self.nombre,
            "nivel": self.nivel,
            "vida": self.vida,
            "vida_max": self.vida_max
        }

    @classmethod
    def from_dict(cls, data: dict) -> Personaje:
        """
        Crea una instancia de Personaje a partir de un diccionario de datos.

        Args:
            data (dict): Diccionario que contiene las variables iniciales del personaje.

        Returns:
            Personaje: Una nueva instancia con los datos proveídos.
        """
        return cls(
            id=data.get("id"),
            nombre=data.get("nombre"),
            nivel=data.get("nivel", 1),
            vida=data.get("vida"),
            vida_max=data.get("vida_max")
        )

    def __repr__(self):
        """ Representación técnica del objeto. """
        return f"<{self.__class__.__name__}(id={self.id}, nombre='{self.nombre}', nivel={self.nivel}, vida={self.vida}/{self.vida_max})>"

    def __str__(self):
        """ Representación amigable para la intefaz de usuario. """
        return f"{self.nombre} (Nivel {self.nivel}) - Vida: {self.vida}/{self.vida_max}"
