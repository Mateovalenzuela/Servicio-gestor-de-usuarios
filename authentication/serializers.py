from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        min_length=4,
        max_length=50,
        required=True,
        validators=User._meta.get_field('username').validators
    )
    password = serializers.CharField(
        min_length=8,
        max_length=50,
        required=True,
        validators=User._meta.get_field('password').validators
    )
    email = serializers.EmailField(max_length=50, required=True)
    first_name = serializers.CharField(min_length=2, max_length=50, required=True)
    last_name = serializers.CharField(min_length=2, max_length=50, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {'read_only': True},
            'email': {'read_only': True},
            'password': {'write_only': True}
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)

        # Solo establecer la contraseña si se proporciona
        password = validated_data.get('password')
        if password:
            instance.set_password(password)

        instance.save()
        return instance

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass

