from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models import QuerySet
from .models import CuentaBancaria


def obtener_cuentas_usuario(
    usuario: AbstractBaseUser | AnonymousUser,
) -> QuerySet[CuentaBancaria]:
    return CuentaBancaria.objects.filter(usuario=usuario).prefetch_related(
        "transacciones"
    )
