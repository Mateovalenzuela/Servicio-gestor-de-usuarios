from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import CustomTokenObtainPairSerializer
from .UsuarioService import UsuarioService
from .JWTService import JWTService
from ..responses import SuccessResponse, ErrorResponse


class AuthenticationService:
    def __init__(self):
        self._token_serializer_class = CustomTokenObtainPairSerializer

    def _get_serializer_class(self, data=None):
        return self._token_serializer_class(data=data)

    def login(self, password: str, email):
        try:
            user = authenticate(
                email=email,
                password=password,
            )  # devuelve un bool si existe o no un usuario para esas credenciales

            if user:
                service = JWTService()
                response = service.create_token_for_user(
                    email=email,
                    password=password
                )
                return response

            return ErrorResponse.credentials_not_found()

        except Exception as e:
            return ErrorResponse.server_error()

    def logout(self, user_id: int):
        try:
            if not int == type(user_id):
                return ErrorResponse.not_found()

            service = UsuarioService()
            user = service.get_object_user(user_id)

            if user:
                # actualiza el token de refresh y lo manda a la lista negra
                RefreshToken.for_user(user)
                return SuccessResponse.ok(message='Sesion cerrada correctamente')

            return ErrorResponse.user_not_found()

        except Exception as e:
            return ErrorResponse.server_error()
