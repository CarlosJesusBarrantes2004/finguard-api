from decimal import Decimal
from rest_framework import serializers
from .models import CuentaBancaria, Transaccion


class TransaccionDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = ["id", "monto", "tipo", "creado_en"]


class CuentaBancariaSerializer(serializers.ModelSerializer):
    transacciones = TransaccionDetalleSerializer(many=True, read_only=True)

    class Meta:
        model = CuentaBancaria
        fields = [
            "id",
            "numero_cuenta",
            "tipo_cuenta",
            "balance",
            "creado_en",
            "transacciones",
        ]


class CrearCuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaBancaria
        fields = ["id", "numero_cuenta", "tipo_cuenta", "balance"]
        read_only_fields = ["id"]


class TransferenciaEntradaSerializer(serializers.Serializer):
    cuenta_origen_id = serializers.IntegerField(min_value=1)
    cuenta_destino_id = serializers.IntegerField(min_value=1)
    monto = serializers.DecimalField(max_digits=14, decimal_places=2)

    def validate_monto(self, value: Decimal) -> Decimal:
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("El monto debe ser mayor a 0.00.")
        return value

    def validate(self, data: dict) -> dict:
        if data["cuenta_origen_id"] == data["cuenta_destino_id"]:
            raise serializers.ValidationError(
                "La cuenta de destino no puede ser la misma que la de origen."
            )
        return data
