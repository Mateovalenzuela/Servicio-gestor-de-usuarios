from django.contrib.auth.models import User
from rest_framework import serializers


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        read_only_fields = ('id', 'username')

    # Añadir atributos 'required' para campos específicos
    username = serializers.CharField(required=True)
    # Puedes manejar la contraseña de una manera segura utilizando un campo de contraseña
    password = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
