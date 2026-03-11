from django.db import models


class BatallaManager(models.Manager):
    """
    Manager para gestionar las batallas entre usuarios.
    """

    def obtener_por_id(self, batalla_id):
        """
        Obtiene una batalla a partir de su id.

        Parameters
        ----------
        batalla_id : int
            id del registro de batalla.

        Returns
        -------
        Batalla | None
            Instancia del modelo Batalla si existe, en caso contrario None.
        """
        try:
            return self.get(id=batalla_id)
        except self.model.DoesNotExist:
            return None

    def listar_por_usuario(self, usuario_id):
        """
        Lista todas las batallas en las que participa un usuario.

        Incluye tanto las batallas donde el usuario es atacante
        como aquellas donde es defensor.

        Parameters
        ----------
        usuario_id : int
            id del usuario.

        Returns
        -------
        QuerySet
            Conjunto de batallas ordenadas por fecha descendente.
        """
        return self.filter(
            models.Q(id_atacante=usuario_id) | models.Q(id_defensor=usuario_id)
        ).order_by("-fecha_batalla")

    def batallas_pendientes(self, usuario_id):
        """
        Obtiene las batallas no leídas de un usuario.

        Solo se consideran pendientes aquellas en las que el usuario
        es defensor y todavía no han sido marcadas como leídas.

        Parameters
        ----------
        usuario_id : int
            id del usuario.

        Returns
        -------
        QuerySet
            Conjunto de batallas pendientes del usuario.
        """
        return self.filter(id_defensor=usuario_id, leido=False)


class Batalla(models.Model):
    """
    Modelo que representa una batalla entre dos usuarios.

    Cada registro almacena el atacante, el defensor, los personajes
    utilizados en el combate y el resultado de la batalla.

    Attributes
    ----------
    id_atacante : ForeignKey
        Usuario que inicia el ataque.
    id_defensor : ForeignKey
        Usuario que recibe el ataque.
    personaje_atacante : ForeignKey
        Personaje utilizado por el atacante.
    personaje_defensor : ForeignKey
        Personaje utilizado por el defensor.
    resultado : BooleanField
        Resultado de la batalla, si es true se considera
        que el vencedor es el atacante
    fecha_batalla : DateTimeField
        Fecha en la que se registró la batalla.
    leido : BooleanField
        Indica si la batalla ha sido revisada por el usuario.
    """

    id_atacante = models.ForeignKey(
        "app.Usuario", on_delete=models.CASCADE, related_name="batallas_como_atacante"
    )
    id_defensor = models.ForeignKey(
        "app.Usuario", on_delete=models.CASCADE, related_name="batallas_como_defensor"
    )
    personaje_atacante = models.ForeignKey(
        "app.Personaje", on_delete=models.CASCADE, related_name="batallas_como_atacante"
    )
    personaje_defensor = models.ForeignKey(
        "app.Personaje", on_delete=models.CASCADE, related_name="batallas_como_defensor"
    )
    resultado = models.BooleanField(null=True, blank=True)
    fecha_batalla = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    objects = BatallaManager()

    class Meta:
        db_table = "batallas"
        ordering = ["-fecha_batalla"]

    def __str__(self):
        """
        Devuelve una representación legible de la batalla.

        Returns
        -------
        str
            Cadena con el id de la batalla y los usuarios
            que participaron.
        """
        return f"Batalla #{self.id}: {self.id_atacante} vs {self.id_defensor}"

    def __repr__(self):
        """
        Devuelve una representación técnica del objeto.

        Returns
        -------
        str
            Representación interna del objeto Batalla.
        """
        return f"<Batalla(id={self.id}, atacante={self.id_atacante}, defensor={self.id_defensor})>"
