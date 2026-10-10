from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import PerfilUsuarioSerializer, RegistroUsuarioSerializer
from .throttles import LoginRateThrottle

# Create your views here.


class RegistroUsuarioView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistroUsuarioSerializer


class LoginSeguroView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]


class PerfilUsuarioView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PerfilUsuarioSerializer

    def get_object(self):
        return self.request.user
