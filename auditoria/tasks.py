from decimal import Decimal
import time
from celery import shared_task
from cuentas.models import Transaccion
from .models import RegistroAuditoria


@shared_task(bind=True, max_retries=3)
def auditar_transaccion_async(self, transaccion_id: int) -> dict:
    try:
        tx = Transaccion.objects.select_related("cuenta__usuario").get(
            id=transaccion_id
        )

        time.sleep(1)

        if tx.monto >= Decimal("10000.00"):
            nivel = RegistroAuditoria.NivelRiesgo.ALTO
            detalle = f"Alerta: Monto elevado ({tx.monto}). Requiere validación de oficial de cumplimiento."
        elif tx.monto >= Decimal("3000.00"):
            nivel = RegistroAuditoria.NivelRiesgo.MEDIO
            detalle = (
                f"Advertencia: Operación por encima del umbral regular ({tx.monto})."
            )
        else:
            nivel = RegistroAuditoria.NivelRiesgo.BAJO
            detalle = "Operación rutinaria dentro de los parámetros esperados."

        registro = RegistroAuditoria.objects.create(
            transaccion=tx,
            nivel_riesgo=nivel,
            detalle=detalle,
        )

        return {
            "auditoria_id": registro.id,
            "transaccion_id": tx.id,
            "nivel_riesgo": registro.nivel_riesgo,
        }
    except Transaccion.DoesNotExist:
        return {"error": f"Transacción {transaccion_id} no encontrada."}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
