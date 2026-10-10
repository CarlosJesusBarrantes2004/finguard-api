from django.urls import path
from .views import ListarCrearCuentasView, DetalleCuentaView, TransferenciaView

app_name = "cuentas"

urlpatterns = [
    path("", ListarCrearCuentasView.as_view(), name="cuentas-list-create"),
    path("<int:pk>/", DetalleCuentaView.as_view(), name="detalle-cuenta"),
    path("transferir/", TransferenciaView.as_view(), name="transferir-fondos"),
]
