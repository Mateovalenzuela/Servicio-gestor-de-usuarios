from django.contrib.auth.models import User
from rest_framework import serializers


class ListarUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CrearUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    email = serializers.CharField(max_length=50, required=True)
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)

    def validate(self, data):
        # Validar si el nombre de usuario ya existe en la base de datos
        username = data.get('username')
        if len(username) > 30:
            raise serializers.ValidationError("Introduzca un nombre de usuario válido. El username debe contener menos de 30 caracteres.")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return data

    def create(self, validated_data):
        # Extraer la contraseña del diccionario de datos validados
        password = validated_data.pop('password', None)

        # Crear una nueva instancia del usuario con los datos validados
        user = User(**validated_data)
        # Establecer la contraseña utilizando el método set_password
        if password:
            user.set_password(password)
        # Guardar el usuario en la base de datos
        user.save()
        return user


class ActualizarUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        read_only_fields = ('id', 'username', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):

        password = validated_data.get('password')
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class LoginUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        write_only_fields = ('password',)

    username = serializers.CharField(max_length=30, required=True)
    password = serializers.CharField(required=True)
