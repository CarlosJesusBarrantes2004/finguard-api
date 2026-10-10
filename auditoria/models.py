from django.db import models
from cuentas.models import Transaccion

# Create your models here.


class RegistroAuditoria(models.Model):
    class NivelRiesgo(models.TextChoices):
        BAJO = "BAJO", "Bajo"
        MEDIO = "MEDIO", "Medio"
        ALTO = "ALTO", "Alto"

    transaccion = models.ForeignKey(
        Transaccion, on_delete=models.CASCADE, related_name="auditorias"
    )
    nivel_riesgo = models.CharField(
        max_length=10, choices=NivelRiesgo.choices, default=NivelRiesgo.BAJO
    )
    detalle = models.TextField()
    analizado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "registros_auditoria"

    def __str__(self) -> str:
        return f"Auditoría Tx {self.transaccion_id} - {self.nivel_riesgo}"
