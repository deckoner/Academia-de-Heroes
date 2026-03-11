from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.auth.models import User


class UsuarioManager(models.Manager):
    """
    Manager para gestionar los usuarios del sistema.
    """

    def obtener_por_id(self, usuario_id):
        """
        Obtiene un usuario a partir de su id.

        Parameters
        ----------
        usuario_id : int
            id del usuario.

        Returns
        -------
        Usuario | None
            Instancia del modelo Usuario si existe, en caso contrario None.
        """
        try:
            return self.get(id=usuario_id)
        except self.model.DoesNotExist:
            return None

    def listar_todos(self):
        """
        Lista todos los usuarios ordenados por username.

        Returns
        -------
        QuerySet
            Conjunto de usuarios ordenados por nombre de usuario.
        """
        return self.all().order_by("user__username")

    def es_mayor_de_edad(self, usuario_id):
        """
        Comprueba si un usuario es mayor de edad.

        Calcula la edad a partir de la fecha de nacimiento
        y verifica si es mayor o igual a 18 años.

        Parameters
        ----------
        usuario_id : int
            id del usuario.

        Returns
        -------
        bool
            True si el usuario tiene al menos 18 años, False en caso contrario.
        """

        usuario = self.obtener_por_id(usuario_id)

        if not usuario or not usuario.fecha_nacimiento:
            return False

        today = date.today()

        age = (
            today.year
            - usuario.fecha_nacimiento.year
            - (
                (today.month, today.day)
                < (usuario.fecha_nacimiento.month, usuario.fecha_nacimiento.day)
            )
        )

        return age >= 18


class Usuario(models.Model):
    """
    Modelo que representa a un usuario del sistema.

    Almacena la informacion principal del perfil del usuario
    y su relacion con el modelo de autenticacion de Django.

    Attributes
    ----------
    user : OneToOneField
        Relacion con el modelo de autenticacion de Django.
    DNI : CharField
        Documento identificador unico del usuario (guardar esto asi a europa no le gusta).
    fecha_nacimiento : DateField
        Fecha de nacimiento del usuario.
    fecha_registro : DateTimeField
        Fecha en la que el usuario se registro en el sistema.
    telefono : CharField
        Numero de telefono del usuario.
    email : EmailField
        Correo electronico del usuario.
    monedas : PositiveIntegerField
        Cantidad de monedas disponibles en el juego.
    mercenarios : PositiveIntegerField
        Numero de mercenarios que posee el usuario.
    es_admin : BooleanField
        Indica si el usuario tiene privilegios de administrador.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil", null=True, blank=True
    )

    DNI = models.CharField(max_length=20, unique=True)

    fecha_nacimiento = models.DateField(null=True, blank=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    telefono = models.CharField(max_length=20, blank=True)

    email = models.EmailField(blank=True, null=True)

    monedas = models.PositiveIntegerField(default=10)

    mercenarios = models.PositiveIntegerField(default=0)

    es_admin = models.BooleanField(default=False)

    objects = UsuarioManager()

    class Meta:
        db_table = "usuarios"
        ordering = ["user__username"]

    def clean(self):
        """
        Realiza validaciones antes de guardar el usuario.

        Verifica que la fecha de nacimiento no sea futura.

        Raises
        ------
        ValidationError
            Si la fecha de nacimiento es posterior a la fecha actual.
        """

        if self.fecha_nacimiento:

            today = date.today()

            age = (
                today.year
                - self.fecha_nacimiento.year
                - (
                    (today.month, today.day)
                    < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
                )
            )

            if age < 0:
                raise ValidationError(
                    {"fecha_nacimiento": "La fecha de nacimiento no puede ser futura."}
                )

    def __str__(self):
        """
        Devuelve una representacion legible del usuario.

        Returns
        -------
        str
            Nombre de usuario asociado al perfil.
        """
        return self.user.username

    def __repr__(self):
        """
        Devuelve una representacion tecnica del objeto.

        Returns
        -------
        str
            Representacion interna del objeto Usuario.
        """
        return f"<Usuario(id={self.id}, username='{self.user.username}')>"
