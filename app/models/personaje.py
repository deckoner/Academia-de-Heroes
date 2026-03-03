from django.db import models


class PersonajeManager(models.Manager):
    """
    Gestor personalizado para el modelo Personaje.
    Proporciona metodos de utilidad para interacturar con la base de datos.
    """

    def obtener_por_id(self, personaje_id):
        """
        Obtiene un personaje por su identificador unico.

        Args:
            personaje_id: Identificador numerico del personaje.

        Returns:
            Instancia de Personaje o None si no existe.
        """
        try:
            return self.get(id=personaje_id)
        except self.model.DoesNotExist:
            return None

    def listar_todos(self):
        """
        Lista todos los personajes ordenados por nombre.

        Returns:
            QuerySet con todos los personajes.
        """
        return self.all().order_by("nombre")


class Personaje(models.Model):
    """
    Clase base que representa a un personaje dentro del juego.

    Proporciona los atributos y metodos fundamentales para el sistema de combate,
    experiencia y persistencia de datos en la base de datos.
    """

    VIDA_MAX_BASE = 100

    TIPO_CHOICES = [
        ("PERSONAJE", "Personaje"),
        ("GUERRERO", "Guerrero"),
        ("MAGO", "Mago"),
        ("ARQUERO", "Arquero"),
    ]

    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES, default="PERSONAJE", db_index=True
    )
    nombre = models.CharField(max_length=100, unique=True, db_index=True)
    nivel = models.PositiveIntegerField(default=1)
    vida = models.PositiveIntegerField(default=VIDA_MAX_BASE)
    vida_max = models.PositiveIntegerField(default=VIDA_MAX_BASE)
    armadura = models.PositiveIntegerField(null=True, blank=True)
    mana = models.PositiveIntegerField(null=True, blank=True)
    precision = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PersonajeManager()

    class Meta:
        db_table = "personajes"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["tipo"]),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.nivel < 1:
            raise ValidationError({"nivel": "El nivel debe ser al menos 1."})
        if self.vida < 0:
            raise ValidationError({"vida": "La vida no puede ser negativa."})
        if self.armadura is not None and self.armadura < 0:
            raise ValidationError({"armadura": "La armadura no puede ser negativa."})
        if self.mana is not None and self.mana < 0:
            raise ValidationError({"mana": "El mana no puede ser negativo."})
        if self.precision is not None and not (0 <= self.precision <= 100):
            raise ValidationError(
                {"precision": "La precision debe estar entre 0 y 100."}
            )

    def save(self, *args, **kwargs):
        if not self.vida_max:
            self.vida_max = self.VIDA_MAX_BASE + (self.nivel - 1) * 10
        if not self.vida:
            self.vida = self.vida_max
        super().save(*args, **kwargs)

    def esta_vivo(self):
        """
        Verifica el estado actual del personaje.

        Returns:
            bool: True si la vida es mayor a cero, False en caso contrario.
        """
        return self.vida > 0

    def recibir_danio(self, cantidad):
        """
        Aplica dano directo a los puntos de vida del personaje.

        Args:
            cantidad: Puntos de dano a restar de la vida actual.
        """
        if cantidad < 0:
            raise ValueError("La cantidad de dano no puede ser negativa.")
        dano = cantidad
        if self.tipo == "GUERRERO" and self.armadura:
            dano = max(0, cantidad - self.armadura)
        self.vida = max(0, self.vida - dano)

    def curar(self, cantidad):
        """
        Restaura puntos de vida del personaje hasta el maximo permitido.

        Args:
            cantidad: Puntos de vida a restaurar.
        """
        if cantidad < 0:
            raise ValueError("La cantidad de curacion no puede ser negativa.")
        if not self.esta_vivo():
            return
        self.vida = min(self.vida_max, self.vida + cantidad)

    def subir_nivel(self):
        """
        Incrementa el Nivel del personaje.

        Sube el nivel en 1 unidad, aumenta la vida maxima en 10 puntos fijos
        y cura al personaje parcialmente (50% de su vida maxima).
        """
        self.nivel += 1
        incremento_vida = 10
        self.vida_max += incremento_vida
        self.vida = min(self.vida_max, self.vida + (self.vida_max // 2))

    def ataque(self):
        """
        Calcula el dano base que inflige el personaje.

        Returns:
            int: Puntos de dano calculados como 10 mas el nivel del personaje.
        """
        dano_base = 10 + self.nivel

        if self.tipo == "ARQUERO" and self.precision is not None:
            import random

            probabilidad = random.randint(1, 100)
            if probabilidad > self.precision:
                return 0

        return dano_base

    def ataque_especial(self):
        """
        Ejecuta una habilidad especial con dano critico.
        Consume 10 unidades de mana para efectuar un dano equivalente al doble del ataque normal.

        Returns:
            int: Cantidad de dano generado. Si no dispone de mana suficiente retorna 0.
        """
        if self.tipo != "MAGO" or not self.mana or self.mana < 10:
            return 0

        self.mana -= 10
        return self.ataque() * 2

    def __str__(self):
        return f"{self.nombre} (Nivel {self.nivel}) - Vida: {self.vida}/{self.vida_max}"

    def __repr__(self):
        return f"<Personaje(id={self.id}, nombre='{self.nombre}', nivel={self.nivel}, vida={self.vida}/{self.vida_max}, tipo={self.tipo})>"
