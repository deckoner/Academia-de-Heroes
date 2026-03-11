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

    def listar_amigos(self, usuario_id):
        """
        Obtiene todas las relaciones de amistad asociadas a un usuario.

        Parameters
        ----------
        usuario_id : int
            id del usuario a listar sus amigos.

        Returns
        -------
        QuerySet
            Conjunto de amistad del usuario.
        """
        return self.filter(id_usuario=usuario_id).select_related("id_amigo")

    def son_amigos(self, usuario_id, amigo_id):
        """
        Verifica si dos usuarios ya tienen una relación de amistad registrada.

        La comprobación se realiza en ambos sentidos para evitar duplicados,
        ya que cualquiera de los usuarios pudo haber iniciado la relación.

        Parameters
        ----------
        usuario_id : int
            id del primer usuario.
        amigo_id : int
            id del segundo usuario.

        Returns
        -------
        bool
            True si los usuarios ya son amigos, False en caso contrario.
        """
        return self.filter(
            models.Q(id_usuario=usuario_id, id_amigo=amigo_id)
            | models.Q(id_usuario=amigo_id, id_amigo=usuario_id)
        ).exists()

    def agregar_amigo(self, usuario, amigo):
        """
        Crea una nueva relación de amistad entre dos usuarios.

        Antes de crear la relación se valida que:
        - El usuario no intente agregarse a sí mismo.
        - La relación de amistad no exista previamente.

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
        if self.son_amigos(usuario.id, amigo.id):
            raise ValidationError("Ya son amigos.")
        return self.create(id_usuario=usuario, id_amigo=amigo)


class Amigo(models.Model):
    """
    Modelo que representa la relación de amistad entre dos usuarios.

    Cada registro indica que un usuario ha agregado a otro como amigo.
    La combinación de usuario y amigo debe ser única para evitar
    duplicidades dentro de la tabla.

    Attributes
    ----------
    id_usuario : ForeignKey
        Usuario que establece la relación de amistad.
    id_amigo : ForeignKey
        Usuario que ha sido agregado como amigo.
    """

    id_usuario = models.ForeignKey(
        "app.Usuario", on_delete=models.CASCADE, related_name="amigos"
    )
    id_amigo = models.ForeignKey(
        "app.Usuario", on_delete=models.CASCADE, related_name="agregado_por"
    )

    objects = AmigoManager()

    class Meta:
        db_table = "amigos"
        unique_together = ["id_usuario", "id_amigo"]

    def clean(self):
        """
        Realiza validaciones adicionales antes de guardar el modelo.

        Comprueba que un usuario no pueda agregarse a sí mismo
        como amigo.

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
            Cadena con el usuario y su amigo asociado.
        """
        return f"{self.id_usuario} - Amigo: {self.id_amigo}"

    def __repr__(self):
        """
        Devuelve una representación técnica del objeto.

        Esta representación es útil para depuración y logging.

        Returns
        -------
        str
            Representación interna del objeto Amigo.
        """
        return f"<Amigo(usuario={self.id_usuario}, amigo={self.id_amigo})>"
