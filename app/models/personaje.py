from django.db import models
from django.core.exceptions import ValidationError
import random


class PersonajeManager(models.Manager):
    """
    Manager para gestionar los personajes del juego.
    """

    def obtener_por_id(self, personaje_id):
        """
        Obtiene un personaje a partir de su id.

        Parameters
        ----------
        personaje_id : int
            id del personaje.

        Returns
        -------
        Personaje | None
            Instancia del modelo Personaje si existe, en caso contrario None.
        """
        try:
            return self.get(id=personaje_id)
        except self.model.DoesNotExist:
            return None

    def listar_todos(self):
        """
        Lista todos los personajes ordenados por nombre.

        Returns
        -------
        QuerySet
            Conjunto de personajes ordenados por nombre.
        """
        return self.all().order_by("nombre")


class Personaje(models.Model):
    """
    Modelo que representa a un personaje dentro del juego.

    Define los atributos principales utilizados en el sistema de combate
    como nivel, vida, armadura, mana y precision.

    Attributes
    ----------
    id_usuario : ForeignKey
        Usuario propietario del personaje.
    tipo : CharField
        Tipo de personaje (Personaje, Guerrero, Mago o Arquero).
    nombre : CharField
        Nombre unico del personaje.
    nivel : PositiveIntegerField
        Nivel actual del personaje.
    vida : PositiveIntegerField
        Puntos de vida actuales.
    vida_max : PositiveIntegerField
        Puntos de vida maximos del personaje.
    armadura : PositiveIntegerField
        Valor de defensa utilizado para reducir dano recibido (guerreros).
    mana : PositiveIntegerField
        Recurso utilizado para ataques especiales (magos).
    precision : PositiveIntegerField
        Probabilidad de acierto (arqueros).
    vivo : BooleanField
        Indica si el personaje sigue con vida.
    created_at : DateTimeField
        Fecha de creacion del registro.
    updated_at : DateTimeField
        Fecha de la ultima actualizacion.
    """

    VIDA_MAX_BASE = 100

    TIPO_CHOICES = [
        ("PERSONAJE", "Personaje"),
        ("GUERRERO", "Guerrero"),
        ("MAGO", "Mago"),
        ("ARQUERO", "Arquero"),
    ]

    id_usuario = models.ForeignKey(
        "app.Usuario",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="personajes",
    )
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
    vivo = models.BooleanField(default=True)
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
        """
        Realiza validaciones antes de guardar el personaje.

        Raises
        ------
        ValidationError
            Si alguno de los valores del personaje no cumple las reglas
            definidas (nivel minimo, vida negativa, precision fuera de rango).
        """
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
        """
        Guarda el personaje en la base de datos.

        Si no existen valores de vida maxima o vida actual, se calculan
        automaticamente en funcion del nivel del personaje.
        """
        if not self.vida_max:
            self.vida_max = self.VIDA_MAX_BASE + (self.nivel - 1) * 10
        if not self.vida:
            self.vida = self.vida_max
        super().save(*args, **kwargs)

    def esta_vivo(self):
        """
        Verifica el estado actual del personaje.

        Returns
        -------
        bool
            True si la vida es mayor a cero, False en caso contrario.
        """
        return self.vida > 0

    def recibir_danio(self, cantidad):
        """
        Aplica dano directo a los puntos de vida del personaje.

        Si el personaje es un guerrero y tiene armadura, el dano
        recibido se reduce en funcion de ese valor.

        Parameters
        ----------
        cantidad : int
            Puntos de dano a restar de la vida actual.

        Raises
        ------
        ValueError
            Si la cantidad de dano es negativa.
        """
        if cantidad < 0:
            raise ValueError("La cantidad de dano no puede ser negativa.")

        dano = cantidad

        if self.tipo == "GUERRERO" and self.armadura:
            dano = max(0, cantidad - self.armadura)

        self.vida = max(0, self.vida - dano)

        if self.vida == 0:
            self.vivo = False

    def curar(self, cantidad):
        """
        Restaura puntos de vida del personaje hasta su limite maximo.

        Parameters
        ----------
        cantidad : int
            Puntos de vida a restaurar.

        Raises
        ------
        ValueError
            Si la cantidad de curacion es negativa.
        """
        if cantidad < 0:
            raise ValueError("La cantidad de curacion no puede ser negativa.")
        if not self.esta_vivo():
            return
        self.vida = min(self.vida_max, self.vida + cantidad)

    def subir_nivel(self):
        """
        Incrementa el nivel del personaje.

        Aumenta el nivel en una unidad, incrementa la vida maxima
        en 10 puntos y cura al personaje parcialmente.
        """
        self.nivel += 1
        incremento_vida = 10
        self.vida_max += incremento_vida
        self.vida = min(self.vida_max, self.vida + (self.vida_max // 2))

    def ataque(self):
        """
        Calcula el dano base que inflige el personaje.

        Los arqueros tienen una probabilidad de fallar el ataque
        dependiendo de su precision.

        Returns
        -------
        int
            Puntos de dano generados por el ataque.
        """
        dano_base = 10 + self.nivel

        if self.tipo == "ARQUERO" and self.precision is not None:
            probabilidad = random.randint(1, 100)
            if probabilidad > self.precision:
                return 0

        return dano_base

    def ataque_especial(self):
        """
        Ejecuta una habilidad especial con dano critico.

        Solo los magos pueden realizar este ataque y requiere
        consumir 10 puntos de mana.

        Returns
        -------
        int
            Cantidad de dano generado. Si no dispone de mana suficiente retorna 0.
        """
        if self.tipo != "MAGO" or not self.mana or self.mana < 10:
            return 0

        self.mana -= 10
        return self.ataque() * 2

    def __str__(self):
        """
        Devuelve una representacion legible del personaje.

        Returns
        -------
        str
            Cadena con el nombre, nivel y estado de vida.
        """
        return f"{self.nombre} (Nivel {self.nivel}) - Vida: {self.vida}/{self.vida_max}"

    def __repr__(self):
        """
        Devuelve una representacion tecnica del objeto.

        Returns
        -------
        str
            Representacion interna del objeto Personaje.
        """
        return f"<Personaje(id={self.id}, nombre='{self.nombre}', nivel={self.nivel}, vida={self.vida}/{self.vida_max}, tipo={self.tipo})>"
