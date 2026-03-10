from django.db import models


class BatallaManager(models.Manager):
    def obtener_por_id(self, batalla_id):
        try:
            return self.get(id=batalla_id)
        except self.model.DoesNotExist:
            return None

    def listar_por_usuario(self, usuario_id):
        return self.filter(
            models.Q(id_atacante=usuario_id) | models.Q(id_defensor=usuario_id)
        ).order_by("-fecha_batalla")

    def batallas_pendientes(self, usuario_id):
        return self.filter(
            models.Q(id_atacante=usuario_id) | models.Q(id_defensor=usuario_id),
            leido=False,
        )


class Batalla(models.Model):
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
        return f"Batalla #{self.id}: {self.id_atacante} vs {self.id_defensor}"

    def __repr__(self):
        return f"<Batalla(id={self.id}, atacante={self.id_atacante}, defensor={self.id_defensor})>"
