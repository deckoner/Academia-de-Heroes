from django.db import models
from django.core.exceptions import ValidationError
from datetime import date


class UsuarioManager(models.Manager):
    def obtener_por_id(self, usuario_id):
        try:
            return self.get(id=usuario_id)
        except self.model.DoesNotExist:
            return None

    def listar_todos(self):
        return self.all().order_by("nombre_usuario")

    def es_mayor_de_edad(self, usuario_id):
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
    nombre_usuario = models.CharField(max_length=100, unique=True, db_index=True)
    contraseña = models.CharField(max_length=255)
    DNI = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    telefono = models.CharField(max_length=20, blank=True)
    monedas = models.PositiveIntegerField(default=0)
    mercenarios = models.PositiveIntegerField(default=0)
    es_admin = models.BooleanField(default=False)

    objects = UsuarioManager()

    class Meta:
        db_table = "usuarios"
        ordering = ["nombre_usuario"]

    def clean(self):
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
        return self.nombre_usuario

    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre_usuario='{self.nombre_usuario}')>"
