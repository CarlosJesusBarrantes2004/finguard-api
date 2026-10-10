from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginSeguroView, PerfilUsuarioView, RegistroUsuarioView

app_name = "usuarios"

urlpatterns = [
    path("registro/", RegistroUsuarioView.as_view(), name="registro"),
    path("login/", LoginSeguroView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("perfil/", PerfilUsuarioView.as_view(), name="perfil"),
]
