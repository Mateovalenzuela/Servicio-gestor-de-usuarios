import jwt
from django.conf import settings
from ..serializers import CustomTokenObtainPairSerializer
from ..responses import ErrorResponse, SuccessResponse


class JWTService:

    def __init__(self):
        self._serializer_class = CustomTokenObtainPairSerializer

    def validate_token(self, token):
        try:
            # Verificar el token JWT con la clave pública RSA
            decoded_payload = jwt.decode(token, settings.SIMPLE_JWT['VERIFYING_KEY'], settings.SIMPLE_JWT['ALGORITHM'])
            usuario_id = decoded_payload.get('user_id')
            message = f'Token valido, user_id: {usuario_id}'
            return SuccessResponse.ok(message)

        except jwt.ExpiredSignatureError:
            return ErrorResponse.bad_request('Token expirado')

        except jwt.InvalidTokenError:
            return ErrorResponse.bad_request('Token no válido')

        except Exception as e:
            return ErrorResponse.server_error()

    def create_token_for_user(self, password: str, email: str):
        try:

            # Datos de usuario validados que existen en la base de datos
            user_data = {
                'email': email,
                'password': password
            }

            # Crear instancia de CustomTokenObtainPairSerializer
            serializer = self._serializer_class(data=user_data)
            if serializer.is_valid():
                # Obtener el token de acceso y de actualización
                access_token = serializer.validated_data.get('access')
                refresh_token = serializer.validated_data.get('refresh')
                return SuccessResponse.ok(
                    data={'access_token': access_token, 'refresh_token': refresh_token}, message='Token creado'
                )
            else:
                return ErrorResponse.bad_request(message='Token error', errors=serializer.errors)

        except Exception as e:
            return ErrorResponse.server_error()
