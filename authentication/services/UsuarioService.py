from ..serializers import UsuarioSerializer, PasswordSerializer


class UsuarioService:

    def __init__(self):
        self._model = UsuarioSerializer.Meta.model
        self._serializer_class = UsuarioSerializer
        self._queryset = None

    def _get_object(self, id: int):
        try:

            if int != type(id):
                raise ValueError(f"Id de tipo invalido")

            usuario = self._model.objects.get(pk=id, is_active=True)
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

    def get_object_user(self, id: int):
        return self._get_object(id)

    def get_object_user_by_email(self, email: int):
        return self._model.objects.get(email=email, is_active=True)

    def list_all_users(self):
        try:
            usuarios = self._get_queryset()
            usuarios_serializer = self._serializer_class
            data_ususarios = usuarios_serializer(usuarios, many=True)
            return self._build_response(200, data_ususarios.data)
        except Exception as e:
            return self._build_response(500, {'error': f'Error de sistema: {e}'})

    def list_one_user(self, id: int):
        try:
            # convertir id a int
            id = int(id)

            usuario = self._get_object(id)
            if usuario:
                usuario_serializer = self._serializer_class(usuario)
                data_usuario = usuario_serializer.data
                return self._build_response(200, data_usuario)
            else:
                return self._build_response(404, {'error': "Usuario no encontrado"})
        except Exception as e:
            return self._build_response(500, {'error': f'Error de sistema: {e}'})

    def create_user(self, username: str, password: str, email: str):
        try:
            usuario_data = {
                "username": username,
                "password": password,
                "email": email
            }

            usuario_serializer = self._get_serializer_class(usuario_data)
            if usuario_serializer.is_valid():
                usuario_serializer.save()
                return self._build_response(200, {'message': 'Usuario creado'})
            else:
                return self._build_response(400, usuario_serializer.errors)

        except Exception as e:
            return self._build_response(500, {'error': f'Error de sistema: {e}'})

    def set_password_user(self, id: int, password: str, password2: str):
        try:
            # convertir id a int
            id = int(id)

            password_data = {
                "password": password,
                "password2": password2
            }
            password_serializer = PasswordSerializer(data=password_data)
            if password_serializer.is_valid():

                user = self._get_object(id)
                if user is None:
                    return self._build_response(404, {'error': "Usuario no encontrado"})

                user.set_password(password_serializer.validated_data['password'])
                user.save()
                return self._build_response(200, {'message': 'Contraseña Actualizada'})
            else:
                return self._build_response(400, password_serializer.errors)

        except Exception as e:
            return self._build_response(500, {'error': f'Error de sistema: {e}'})

    def update_email_user(self, id: int, email: str, password: str):
        try:
            # convertir id a int
            id = int(id)


            data = {"email": email, "password": password}

            usuario_serializer = self._serializer_class
            serializer = usuario_serializer(data=data, partial=True)

            if serializer.is_valid():

                user = self._get_object(id)
                if user is None:
                    return self._build_response(404, {'error': "Usuario no encontrado"})

                # valída que la contraseña ingresada sea la del usuario a actualizar
                valid_password = user.check_password(serializer.validated_data['password'])

                if not valid_password:
                    # La contraseña no ingresada no coincide con la del usuario
                    return self._build_response(401, {'error': 'La contraseña es invalida'})

                # la contraseña es correcta
                user.email = serializer.validated_data['email']
                user.save()
                return self._build_response(200, {'message': 'Email Actualizado'})
            else:
                # datos invalidos
                return self._build_response(400, serializer.errors)

        except Exception as e:
            return self._build_response(500, {'error': f'Error de sistema: {e}'})

    def update_username_user(self, id: int, username: str):
        try:
            # convertir id a int
            id = int(id)

            data = {"username": username}

            # valida los datos
            serializer_data = self._serializer_class(data=data, partial=True)
            if not serializer_data.is_valid():
                return self._build_response(400, serializer_data.errors)

            user = self._get_object(id)
            if user is None:
                return self._build_response(404, {'error': "Usuario no encontrado"})

            user.username = serializer_data.validated_data['username']
            user.save()
            return self._build_response(200, {'message': 'Username Actualizado'})

        except Exception as e:
            return self._build_response(500, {'error': f'Error de sistema: {e}'})

    def delete_user(self, id: int):
        try:
            # convertir id a int
            id = int(id)

            updated_rows = self._model.objects.filter(id=id, is_active=True, is_superuser=False).update(is_active=False)
            if updated_rows == 1:
                return self._build_response(200, {'message': 'Usuario eliminado'})
            return self._build_response(404, {'error': 'Usuario no encontrado'})
        except Exception as e:
            return self._build_response(500, {'error': f'Error de sistema: {e}'})
