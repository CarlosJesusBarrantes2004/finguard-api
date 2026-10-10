from rest_framework import serializers
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ["id", "email", "nombre", "password"]

    def create(self, validated_data: dict) -> Usuario:
        return Usuario.objects.create_user(**validated_data)


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "email", "nombre", "creado_en"]
