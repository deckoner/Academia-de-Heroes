from django.db import models
from django.core.exceptions import ValidationError


class AmigoManager(models.Manager):
    def obtener_por_id(self, amigo_id):
        try:
            return self.get(id=amigo_id)
        except self.model.DoesNotExist:
            return None

    def listar_amigos(self, usuario_id):
        return self.filter(id_usuario=usuario_id).select_related("id_amigo")

    def son_amigos(self, usuario_id, amigo_id):
        return self.filter(
            models.Q(id_usuario=usuario_id, id_amigo=amigo_id)
            | models.Q(id_usuario=amigo_id, id_amigo=usuario_id)
        ).exists()

    def agregar_amigo(self, usuario, amigo):
        if usuario.id == amigo.id:
            raise ValidationError("No puedes ser amigo de ti mismo.")
        if self.son_amigos(usuario.id, amigo.id):
            raise ValidationError("Ya son amigos.")
        return self.create(id_usuario=usuario, id_amigo=amigo)


class Amigo(models.Model):
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
        if self.id_usuario_id == self.id_amigo_id:
            raise ValidationError("No puedes ser amigo de ti mismo.")

    def __str__(self):
        return f"{self.id_usuario} - Amigo: {self.id_amigo}"

    def __repr__(self):
        return f"<Amigo(usuario={self.id_usuario}, amigo={self.id_amigo})>"
