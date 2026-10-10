from decimal import Decimal
import pytest
from django.contrib.auth import get_user_model
from cuentas.models import CuentaBancaria
from cuentas.services import (
    transferir_fondos,
    SaldoInsuficienteError,
    OperacionNoPermitidaError,
)

Usuario = get_user_model()

# Create your tests here.


@pytest.mark.django_db
class TestTransferenciasBancarias:
    def setup_method(self):
        self.usuario1 = Usuario.objects.create_user(
            email="emisor@test.com", nombre="Emisor", password="password123"
        )
        self.usuario2 = Usuario.objects.create_user(
            email="receptor@test.com", nombre="Receptor", password="password123"
        )

        self.cuenta1 = CuentaBancaria.objects.create(
            usuario=self.usuario1,
            numero_cuenta="CTA-001",
            balance=Decimal("1000.00"),
        )
        self.cuenta2 = CuentaBancaria.objects.create(
            usuario=self.usuario2,
            numero_cuenta="CTA-002",
            balance=Decimal("500.00"),
        )

    def test_transferencia_exitosa(self):
        tx_retiro, tx_deposito = transferir_fondos(
            usuario_solicitante=self.usuario1,
            cuenta_origen_id=self.cuenta1.id,
            cuenta_destino_id=self.cuenta2.id,
            monto=Decimal("200.00"),
        )

        self.cuenta1.refresh_from_db()
        self.cuenta2.refresh_from_db()

        assert self.cuenta1.balance == Decimal("800.00")
        assert self.cuenta2.balance == Decimal("700.00")
        assert tx_retiro.monto == Decimal("200.00")
        assert tx_deposito.monto == Decimal("200.00")

    def test_error_por_saldo_insuficiente(self):
        with pytest.raises(SaldoInsuficienteError):
            transferir_fondos(
                usuario_solicitante=self.usuario1,
                cuenta_origen_id=self.cuenta1.id,
                cuenta_destino_id=self.cuenta2.id,
                monto=Decimal("1500.00"),
            )

    def test_error_intento_fraude_usuario_no_titular(self):
        with pytest.raises(OperacionNoPermitidaError):
            transferir_fondos(
                usuario_solicitante=self.usuario2,
                cuenta_origen_id=self.cuenta1.id,
                cuenta_destino_id=self.cuenta2.id,
                monto=Decimal("100.00"),
            )
