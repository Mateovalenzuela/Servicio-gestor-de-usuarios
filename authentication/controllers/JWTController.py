import jwt
from django.conf import settings
from ..serializers import CustomTokenObtainPairSerializer


class JWTController:

    def __init__(self):
        self._serializer_class = CustomTokenObtainPairSerializer

    def _build_response(self, status, data):
        return status, data

    def validate_token(self, token):
        try:
            # Verificar el token JWT con la clave pública RSA
            decoded_payload = jwt.decode(token, settings.SIMPLE_JWT['VERIFYING_KEY'], settings.SIMPLE_JWT['ALGORITHM'])
            usuario_id = decoded_payload.get('user_id')
            return self._build_response(200, {'message': f'Token valido, user_id: {usuario_id}'})
        except jwt.ExpiredSignatureError:
            return self._build_response(400, {'error': f'Token expirado'})
        except jwt.InvalidTokenError:
            return self._build_response(400, {'error': f'Token no válido'})
        except Exception as e:
            return self._build_response(500, {'error': f'Servicio no disponible: {e}'})

    def create_token_for_user(self, password: str, email):
        try:

            # Datos de usuario validados que existen en la base de datos
            user_data = {
                'email': email,
                'password': password
            }

            # Crear instancia de CustomTokenObtainPairSerializer
            serializer = self._serializer_class(data=user_data)
            if serializer.is_valid(raise_exception=True):
                # Obtener el token de acceso y de actualización
                access_token = serializer.validated_data.get('access')
                refresh_token = serializer.validated_data.get('refresh')
                return self._build_response(
                    200, {'access_token': access_token, 'refresh_token': refresh_token}
                )
            else:
                return self._build_response(400, serializer.errors)
        except Exception as e:
            return self._build_response(500, {'error': f'Servicio no disponible: {e}'})
