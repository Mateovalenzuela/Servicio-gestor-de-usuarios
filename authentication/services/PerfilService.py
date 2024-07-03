from ..serializers import PerfilSerializer
from ..responses import ErrorResponse, SuccessResponse
from .UsuarioService import UsuarioService


class PerfilService:
    def __init__(self):
        self._model = PerfilSerializer.Meta.model
        self._serializer_class = PerfilSerializer
        self._queryset = None

    def _get_object(self, pk):
        try:

            usuario = self._model.objects.get(pk=pk, is_active=True)
            return usuario

        except self._model.DoesNotExist:
            return None
        except Exception as e:
            raise Exception(f"Error al recuperar el usuario: {e}")

    def _get_queryset(self):
        if self._queryset is None:
            return self._model.objects.filter(is_active=True, is_superuser=False)
        return self._queryset

    def add_perfil_to_user(self, id: int, nombre, apellido, fecha_nacimiento):
        try:
            # convertir id a int
            id = int(id)

            data_perfil = {
                'nombre': nombre,
                'apellido': apellido,
                'fecha_nacimiento': fecha_nacimiento
            }

            # serializa los datos del perfil
            serializer = self._serializer_class(data=data_perfil)

            if serializer.is_valid():

                usuario = UsuarioService().get_object_user(id)
                if usuario is None:
                    return ErrorResponse.user_not_found()

                # Verificar si ya existe un perfil para el usuario
                if hasattr(usuario, 'perfil'):
                    message = 'Ya existe un perfil para este usuario.'
                    return ErrorResponse.bad_request(message=message)

                serializer.save(usuario=usuario)
                message = 'Perfil Agregado a usuario'
                return SuccessResponse.ok(message=message, data=serializer.validated_data)
            return ErrorResponse.bad_request(message='Datos inválidos', errors=serializer.errors)

        except Exception as e:
            return ErrorResponse.server_error()

    def update_perfil_to_user(self, user_id: id, nombre: str, apellido: str, fecha_nacimiento):
        try:
            # convertir id a int
            user_id = int(user_id)

            data_perfil = {
                'nombre': nombre,
                'apellido': apellido,
                'fecha_nacimiento': fecha_nacimiento
            }

            # serializa los datos del perfil
            serializer = self._serializer_class(data=data_perfil)

            if serializer.is_valid():

                usuario_controller = UsuarioService()
                usuario = usuario_controller.get_object_user(user_id)
                if usuario is None:
                    return ErrorResponse.user_not_found()

                # Verificar si el usuario no tiene datos de perfil
                if not hasattr(usuario, 'perfil'):
                    return ErrorResponse.perfil_not_found()

                usuario.perfil.nombre = serializer.validated_data['nombre']
                usuario.perfil.apellido = serializer.validated_data['apellido']
                usuario.perfil.fecha_nacimiento = serializer.validated_data['fecha_nacimiento']
                usuario.perfil.save()

                message = 'Perfil actualizado'
                return SuccessResponse.ok(message=message, data=serializer.validated_data)

            return ErrorResponse.bad_request(message='Datos inválidos', errors=serializer.errors)

        except Exception as e:
            return ErrorResponse.server_error()
