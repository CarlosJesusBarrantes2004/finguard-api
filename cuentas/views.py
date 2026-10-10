from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import EsTitularDeCuenta

from .selectors import obtener_cuentas_usuario
from .serializers import (
    CrearCuentaSerializer,
    CuentaBancariaSerializer,
    TransferenciaEntradaSerializer,
)
from .services import (
    CuentaNoEncontradaError,
    OperacionNoPermitidaError,
    SaldoInsuficienteError,
    transferir_fondos,
)
from .throttles import TransferenciaRateThrottle

# Create your views here.


class ListarCrearCuentasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuentas_qs = obtener_cuentas_usuario(usuario=request.user)
        serializer = CuentaBancariaSerializer(cuentas_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CrearCuentaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cuenta = serializer.save(usuario=request.user)
        return Response(
            CuentaBancariaSerializer(cuenta).data,
            status=status.HTTP_201_CREATED,
        )


class DetalleCuentaView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, EsTitularDeCuenta]
    serializer_class = CuentaBancariaSerializer

    def get_queryset(self):
        return obtener_cuentas_usuario(usuario=self.request.user)


class TransferenciaView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [TransferenciaRateThrottle]

    def post(self, request):
        serializer = TransferenciaEntradaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            tx_retiro, tx_deposito = transferir_fondos(
                usuario_solicitante=request.user,
                cuenta_origen_id=data["cuenta_origen_id"],
                cuenta_destino_id=data["cuenta_destino_id"],
                monto=data["monto"],
            )

            return Response(
                {
                    "mensaje": "Transferencia ejecutada con éxito.",
                    "retiro": {
                        "id": tx_retiro.id,
                        "monto": str(tx_retiro.monto),
                    },
                    "deposito": {
                        "id": tx_deposito.id,
                        "monto": str(tx_deposito.monto),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except CuentaNoEncontradaError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except OperacionNoPermitidaError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except (SaldoInsuficienteError, ValueError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {
                    "error": "Error interno del servidor al procesar la transferencia bancaria."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
