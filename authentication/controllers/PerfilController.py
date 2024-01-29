from ..serializers import PerfilSerializer
from .UsuarioController import UsuarioController


class PerfilController:
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

    def _get_serializer_class(self, data=None):
        return self._serializer_class(data=data)

    def _build_response(self, status, data):
        return status, data

    def add_perfil_to_user(self, id: int, nombre, apellido, fecha_nacimiento):
        try:
            data_perfil = {
                'nombre': nombre,
                'apellido': apellido,
                'fecha_nacimiento': fecha_nacimiento
            }

            # serializa los datos del perfil
            serializer = self._get_serializer_class(data=data_perfil)

            if serializer.is_valid():

                usuario = UsuarioController().get_object_user(id)
                if usuario is None:
                    return self._build_response(404, {'error': 'Usuario no encontrado'})

                # Verificar si ya existe un perfil para el usuario
                if hasattr(usuario, 'perfil'):
                    return self._build_response(400, {'message': 'Ya existe un perfil para este usuario.'})

                serializer.save(usuario=usuario)
                return self._build_response(200, {'message': 'Perfil Agregado a usuario'})
            return self._build_response(400, serializer.errors)

        except Exception as e:
            return self._build_response(500, {'error': f'Error de sistema: {e}'})

    def update_perfil_to_user(self, user_id: id, nombre: str, apellido: str, fecha_nacimiento):
        try:
            data_perfil = {
                'nombre': nombre,
                'apellido': apellido,
                'fecha_nacimiento': fecha_nacimiento
            }

            # serializa los datos del perfil
            serializer_data = self._serializer_class(data=data_perfil)

            if serializer_data.is_valid():

                usuario_controller = UsuarioController()
                usuario = usuario_controller.get_object_user(user_id)
                if usuario is None:
                    return self._build_response(404, {'error': 'Usuario no encontrado'})

                # Verificar si el usuario no tiene datos de perfil
                if not hasattr(usuario, 'perfil'):
                    return self._build_response(
                        404, {'error': 'El usuario que desea actualizar no tiene datos de perfil'}
                    )

                usuario.perfil.nombre = serializer_data.validated_data['nombre']
                usuario.perfil.apellido = serializer_data.validated_data['apellido']
                usuario.perfil.fecha_nacimiento = serializer_data.validated_data['fecha_nacimiento']
                usuario.perfil.save()

                return self._build_response(200, {'message': 'Perfil actualizado'})

            return self._build_response(400, serializer_data.errors)

        except Exception as e:
            return self._build_response(500, {'error': f'Error de sistema: {e}'})
