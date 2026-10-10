from decimal import Decimal
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db import transaction
from .models import CuentaBancaria, Transaccion
from auditoria.tasks import auditar_transaccion_async


class SaldoInsuficienteError(Exception):
    pass


class CuentaNoEncontradaError(Exception):
    pass


class OperacionNoPermitidaError(Exception):
    pass


def transferir_fondos(
    usuario_solicitante: AbstractBaseUser | AnonymousUser,
    cuenta_origen_id: int,
    cuenta_destino_id: int,
    monto: Decimal,
) -> tuple[Transaccion, Transaccion]:
    if monto <= Decimal("0.00"):
        raise ValueError("El monto a transferir debe ser mayor a 0.00.")

    if cuenta_origen_id == cuenta_destino_id:
        raise ValueError("La cuenta de origen y destino no pueden ser la misma.")

    with transaction.atomic():
        ids_a_bloquear = sorted([cuenta_origen_id, cuenta_destino_id])
        cuentas_bloqueadas = {
            c.id: c
            for c in CuentaBancaria.objects.select_for_update().filter(
                id__in=ids_a_bloquear
            )
        }

        if len(cuentas_bloqueadas) < 2:
            raise CuentaNoEncontradaError("Una o ambas cuentas no existen.")

        cuenta_origen = cuentas_bloqueadas[cuenta_origen_id]
        cuenta_destino = cuentas_bloqueadas[cuenta_destino_id]

        if cuenta_origen.usuario != usuario_solicitante:
            raise OperacionNoPermitidaError(
                "No tiene autorización para debitar fondos de esta cuenta."
            )

        if cuenta_origen.balance < monto:
            raise SaldoInsuficienteError(
                f"Saldo insuficiente en cuenta {cuenta_origen.numero_cuenta}. "
                f"Disponible: {cuenta_origen.balance}, Solicitado: {monto}"
            )

        cuenta_origen.balance -= monto
        cuenta_destino.balance += monto

        cuenta_origen.save(update_fields=["balance"])
        cuenta_destino.save(update_fields=["balance"])

        tx_retiro = Transaccion.objects.create(
            cuenta=cuenta_origen,
            monto=monto,
            tipo=Transaccion.TipoTransaccion.RETIRO,
        )
        tx_deposito = Transaccion.objects.create(
            cuenta=cuenta_destino,
            monto=monto,
            tipo=Transaccion.TipoTransaccion.DEPOSITO,
        )

        transaction.on_commit(lambda: auditar_transaccion_async.delay(tx_retiro.id))

        return tx_retiro, tx_deposito
