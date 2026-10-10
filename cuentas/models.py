from decimal import Decimal
from django.conf import settings
from django.db import models

# Create your models here.


class CuentaBancaria(models.Model):
    class TipoCuenta(models.TextChoices):
        AHORRO = "AHORRO", "Cuenta de Ahorro"
        CORRIENTE = "CORRIENTE", "Cuenta Corriente"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="cuentas_bancarias",
    )
    numero_cuenta = models.CharField(max_length=20, unique=True)
    tipo_cuenta = models.CharField(
        max_length=20, choices=TipoCuenta.choices, default=TipoCuenta.AHORRO
    )
    balance = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cuentas_bancarias"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=Decimal("0.00")),
                name="chk_balance_no_negativo",
            )
        ]

    def __str__(self) -> str:
        return f"{self.numero_cuenta} - {self.balance}"


class Transaccion(models.Model):
    class TipoTransaccion(models.TextChoices):
        DEPOSITO = "DEPOSITO", "Depósito"
        RETIRO = "RETIRO", "Retiro"

    cuenta = models.ForeignKey(
        CuentaBancaria,
        on_delete=models.CASCADE,
        related_name="transacciones",
    )
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    tipo = models.CharField(
        max_length=20,
        choices=TipoTransaccion.choices,
        default=TipoTransaccion.RETIRO,
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transacciones"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(monto__gt=Decimal("0.00")),
                name="chk_monto_mayor_a_cero",
            )
        ]

    def __str__(self) -> str:
        return f"Tx {self.id} | {self.tipo} | {self.monto}"
