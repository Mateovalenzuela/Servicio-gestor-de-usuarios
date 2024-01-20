from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import CustomTokenObtainPairSerializer
from .UsuarioController import UsuarioController
from .JWTController import JWTController


class AuthenticationController:
    def __init__(self):
        self._token_serializer_class = CustomTokenObtainPairSerializer

    def _get_serializer_class(self, data=None):
        return self._token_serializer_class(data=data)

    def _build_response(self, status, data):
        return status, data

    def login(self, password: str, email):
        try:
            user = authenticate(
                email=email,
                password=password,
            )  # devuelve un bool si existe o no un usuario para esas credenciales

            if user:
                controller = JWTController()
                status, data = controller.create_token_for_user(
                    email=email,
                    password=password
                )
                return self._build_response(status, data)

            return self._build_response(
                400, {'error': 'Contraseña o nombre de usuario incorrectos'}
            )
        except Exception as e:
            return self._build_response(
                500, {'error': f'Servicio no disponible: {e}'}
            )

    def logout(self, user_id: int):
        try:
            if not int == type(user_id):
                return self._build_response(
                    400, {'error': 'No existe este usuario'}
                )

            controller = UsuarioController()
            user = controller.get_object_user(user_id)

            if user:
                # actualiza el token de refresh y lo manda a la lista negra
                RefreshToken.for_user(user)
                return self._build_response(
                    200, {'message': 'Sesion cerrada correctamente'}
                )
            return self._build_response(
                400, {'error': 'No existe este usuario'}
            )
        except Exception as e:
            return self._build_response(
                500, {'error': f'Servicio no disponible: {e}'}
            )
