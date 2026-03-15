from django.db import models
from django.core.exceptions import ValidationError


class AmigoManager(models.Manager):
    """
    Manager para gestionar las amistades entre los users.
    """

    def obtener_por_id(self, amigo_id):
        """
        Obtiene una relación de amistad a partir de su id.

        Parameters
        ----------
        amigo_id : int
            id del registro de amistad.

        Returns
        -------
        Amigo | None
            Instancia del modelo Amigo si existe, en caso contrario None.
        """
        try:
            return self.get(id=amigo_id)
        except self.model.DoesNotExist:
            return None

    def listar_amigos(self, usuario):
        """
        Obtiene todas las relaciones de amistad aceptadas de un usuario.

        Parameters
        ----------
        usuario : Usuario
            Usuario del cual obtener sus amigos.

        Returns
        -------
        QuerySet
            Conjunto de amistad aceptadas del usuario.
        """
        return self.filter(
            models.Q(id_usuario=usuario, estado="ACEPTADA")
            | models.Q(id_amigo=usuario, estado="ACEPTADA")
        ).select_related("id_usuario", "id_amigo")

    def listar_solicitudes_pendientes(self, usuario):
        """
        Obtiene las solicitudes de amistad pendientes recibidas por el usuario.

        Parameters
        ----------
        usuario : Usuario
            Usuario que recibe las solicitudes.

        Returns
        -------
        QuerySet
            Conjunto de solicitudes pendientes.
        """
        return self.filter(
            id_amigo=usuario, estado="PENDIENTE"
        ).select_related("id_usuario", "id_amigo")

    def listar_solicitudes_enviadas(self, usuario):
        """
        Obtiene las solicitudes de amistad enviadas por el usuario.

        Parameters
        ----------
        usuario : Usuario
            Usuario que envía las solicitudes.

        Returns
        -------
        QuerySet
            Conjunto de solicitudes enviadas pendientes.
        """
        return self.filter(
            id_usuario=usuario, estado="PENDIENTE"
        ).select_related("id_usuario", "id_amigo")

    def son_amigos(self, usuario, amigo):
        """
        Verifica si dos usuarios ya tienen una relación de amistad aceptada.

        Parameters
        ----------
        usuario : Usuario
            Primer usuario.
        amigo : Usuario
            Segundo usuario.

        Returns
        -------
        bool
            True si los usuarios ya son amigos, False en caso contrario.
        """
        return self.filter(
            models.Q(id_usuario=usuario, id_amigo=amigo, estado="ACEPTADA")
            | models.Q(id_usuario=amigo, id_amigo=usuario, estado="ACEPTADA")
        ).exists()

    def tiene_solicitud_pendiente(self, usuario, amigo):
        """
        Verifica si existe una solicitud de amistad pendiente entre dos usuarios.

        Parameters
        ----------
        usuario : Usuario
            Usuario que envió o recibirá la solicitud.
        amigo : Usuario
            Usuario receptor o emisor de la solicitud.

        Returns
        -------
        Amigo | None
            Retorna la solicitud si existe, None en caso contrario.
        """
        return self.filter(
            models.Q(id_usuario=usuario, id_amigo=amigo, estado="PENDIENTE")
            | models.Q(id_usuario=amigo, id_amigo=usuario, estado="PENDIENTE")
        ).first()

    def solicitud_existente(self, usuario, amigo):
        """
        Verifica si existe cualquier tipo de relación entre dos usuarios.

        Parameters
        ----------
        usuario : Usuario
            Primer usuario.
        amigo : Usuario
            Segundo usuario.

        Returns
        -------
        bool
            True si existe alguna relación, False en caso contrario.
        """
        return self.filter(
            models.Q(id_usuario=usuario, id_amigo=amigo)
            | models.Q(id_usuario=amigo, id_amigo=usuario)
        ).exists()

    def agregar_amigo(self, usuario, amigo):
        """
        Crea una nueva relación de amistad entre dos usuarios.

        Antes de crear la relación se valida que:
        - El usuario no intente agregarse a sí mismo.
        - La relación de amistad no exista previamente.

        Si ya existe una solicitud pendiente de amigo hacia usuario,
        se acepta automáticamente.

        Parameters
        ----------
        usuario : Usuario
            Usuario que inicia la relación de amistad.
        amigo : Usuario
            Usuario que será agregado como amigo.

        Returns
        -------
        Amigo
            Instancia del modelo Amigo creada en la base de datos.

        Raises
        ------
        ValidationError
            Si el usuario intenta agregarse a sí mismo o si la relación
            de amistad ya existe.
        """
        if usuario.id == amigo.id:
            raise ValidationError("No puedes ser amigo de ti mismo.")

        solicitud_existente = self.tiene_solicitud_pendiente(amigo, usuario)
        if solicitud_existente:
            solicitud_existente.estado = "ACEPTADA"
            solicitud_existente.save()
            return solicitud_existente

        if self.son_amigos(usuario, amigo):
            raise ValidationError("Ya son amigos.")

        return self.create(id_usuario=usuario, id_amigo=amigo, estado="PENDIENTE")


class Amigo(models.Model):
    """
    Modelo que representa la relación de amistad entre dos usuarios.

    Cada registro indica que un usuario ha enviado una solicitud de amistad
    a otro. La relación puede estar en estado pendiente, aceptada o rechazada.

    Attributes
    ----------
    id_usuario : ForeignKey
        Usuario que envía la solicitud de amistad.
    id_amigo : ForeignKey
        Usuario que recibe la solicitud de amistad.
    estado : CharField
        Estado de la solicitud (PENDIENTE, ACEPTADA, RECHAZADA).
    fecha_creacion : DateTimeField
        Fecha en que se creó la solicitud.
    """

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ACEPTADA = "ACEPTADA", "Aceptada"
        RECHAZADA = "RECHAZADA", "Rechazada"

    id_usuario = models.ForeignKey(
        "app.Usuario",
        on_delete=models.CASCADE,
        related_name="solicitudes_enviadas",
    )
    id_amigo = models.ForeignKey(
        "app.Usuario",
        on_delete=models.CASCADE,
        related_name="solicitudes_recibidas",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    objects = AmigoManager()

    class Meta:
        db_table = "amigos"
        ordering = ["-fecha_creacion"]

    def clean(self):
        """
        Realiza validaciones adicionales antes de guardar el modelo.

        Raises
        ------
        ValidationError
            Si el usuario y el amigo corresponden al mismo registro.
        """
        if self.id_usuario_id == self.id_amigo_id:
            raise ValidationError("No puedes ser amigo de ti mismo.")

    def __str__(self):
        """
        Devuelve una representación legible de la relación de amistad.

        Returns
        -------
        str
            Cadena con el usuario, amigo y estado.
        """
        return f"{self.id_usuario} -> {self.id_amigo} ({self.get_estado_display()})"

    def __repr__(self):
        """
        Devuelve una representación técnica del objeto.

        Returns
        -------
        str
            Representación interna del objeto Amigo.
        """
        return f"<Amigo(usuario={self.id_usuario}, amigo={self.id_amigo}, estado={self.estado})>"
