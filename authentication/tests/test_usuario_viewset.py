from django.test import TestCase, Client
from ..models import Usuario, Perfil
from ..serializers import UsuarioSerializer


class TestUsuarioViewSet(TestCase):
    def setUp(self):
        self.client = Client()
        self.url_api_usuario = '/api/usuario/'
        self.url_api_login = '/api/login/'
        self.model_usuario = Usuario

        self.user = self.model_usuario.objects.create_user(
            username='test',
            password='test1234',
            email='test@mail.com'
        )

        self.perfil_user = Perfil.objects.create(
            nombre='Tester',
            apellido='Super tester',
            usuario=self.user
        )

        self.data_perfil_user_1 = {
            "nombre": 'Leo',
            "apellido": 'Messi',
        }

        self.data_user_1 = {
            'username': 'messi10',
            'password': 'messi123',
            'email': 'messi@gmail.com'
        }

        self.data_perfil_user_2 = {
            "nombre": 'Luis',
            "apellido": 'Suarez',
        }

        self.data_user_1 = {
            'username': 'suarez9',
            'password': 'suarez123',
            'email': 'suarez@gmail.com'
        }

        self.logged_user = self.client.post(
            path=self.url_api_login,
            data={'email': 'test@mail.com', 'password': 'test1234'})

    def _autenticar_usuario(self, data: dict):
        response = self.client.post(
            path=self.url_api_login,
            data=data
        )
        data = dict(response.json())
        token = data['access_token']
        return token

    def _get_usuario_by_username(self, username):
        usuario = self.model_usuario.objects.filter(is_active=True, username=username)
        if not usuario:
            return None
        return usuario.first()

    def test_api_create_user(self):
        """
        Caso de exito: Se realiza la peticion con datos validos.
        """

        response = self.client.post(
            path=self.url_api_usuario,
            data=self.data_user_1,
        )
        print(response.json())
        self.assertEquals(response.status_code, 201)

        """
            Caso de Fallo: Se realiza la peticion con datos invalidos.
        """
        invalid_data = {
            'username': 'Messi@@@',
            'password': 'inv',
            'email': 'mailinvalido.com'
        }
        response = self.client.post(
            path=self.url_api_usuario,
            data=invalid_data,
        )
        print(response.json())
        self.assertEquals(response.status_code, 400)

        """
            Caso de Fallo: Se realiza la peticion con datos incompletos.
        """
        invalid_data = {
            'email': 'mailinvalido.com'
        }
        response = self.client.post(
            path=self.url_api_usuario,
            data=invalid_data,
        )
        print(response.json())
        self.assertEquals(response.status_code, 400)

    def test_api_add_perfil(self):
        """
        Caso de exito: Se crea un usuario en bd, inicia sesion, se hace la peticion pasando el perfil del setUp, para agregarle el perfil al usuario creado.
        """

        data = self.data_user_1
        response = self.client.post(
            path=self.url_api_usuario,
            data=data
        )
        if response.status_code != 201:
            raise Exception("Error al crear un usuario")

        # obtiene el token de sesion de un usuario para poder realizar la peticion
        token = self._autenticar_usuario(data)
        headers = {'Authorization': f'Bearer {token}'}
        id = self._get_usuario_by_username(data['username']).id

        path = f'{self.url_api_usuario}{id}/add_perfil/'
        response = self.client.post(
            path=path,
            headers=headers,
            data=self.data_perfil_user_1
        )
        self.assertEquals(response.status_code, 201)

        """
        Caso de Fallo: Se le asigna un perfil a un usuario que ya tiene perfil.
        """
        path = f'{self.url_api_usuario}{id}/add_perfil/'
        response = self.client.post(
            path=path,
            headers=headers,
            data=self.data_perfil_user_2
        )
        self.assertEquals(response.status_code, 400)

        """
        Caso de Fallo: se intenta realizar la peticion sin toen de autorizacion.
        """

        path = f'{self.url_api_usuario}{id}/add_perfil/'
        response = self.client.post(
            path=path,
            data=self.data_perfil_user_1
        )
        self.assertEquals(response.status_code, 401)

    def test_api_get_all_users(self):
        """
        Caso de exito: Se agrega un usuario a bd y se realiza la peticion de obtener todos
        """

        # agrega un usuario sin perfil
        usuario = Usuario.objects.create_user(
            username='temp',
            password='temp',
            email='temp@email.com'
        )
        usuario.save()

        response = self.client.get(
            path=self.url_api_usuario
        )
        self.assertEquals(response.status_code, 200)

    def test_api_get_one_user(self):
        """
        Caso de exito: Se crea un usuario, inicia sesion, y se realiza la peticion para listar el usuario
        """
        # obtiene el token de sesion de un usuario para poder realizar la peticion
        # agrega un usuario sin perfil
        data = self.data_user_1
        response = self.client.post(
            path=self.url_api_usuario,
            data=data
        )
        if response.status_code != 201:
            raise Exception("Error al crear un usuario")

        # obtiene el token de sesion de un usuario para poder realizar la peticion
        token = self._autenticar_usuario(data)
        headers = {'Authorization': f'Bearer {token}'}
        usuario = self._get_usuario_by_username(data['username'])
        id = usuario.id

        response = self.client.get(
            path=f'{self.url_api_usuario}{id}/',
            headers=headers
        )
        print(response.json())
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            dict(response.json()),
            UsuarioSerializer(usuario).data
        )  # compara usuario recibido con usuario creado, ambos en formato dict

        """
        Caso de fallo: Sin token de autorizacion
        """
        response = self.client.get(
            path=f'{self.url_api_usuario}{id}/',
        )
        self.assertEquals(response.status_code, 401)

    def test_api_update_username(self):
        """
        Caso de exito: Se crea un usuario en bd, se inicia sesion, se realiza la peticion modificando el username por uno valido
        """
        data = self.data_user_1
        response = self.client.post(
            path=self.url_api_usuario,
            data=data
        )
        if response.status_code != 201:
            raise Exception("Error al crear un usuario")

        # obtiene el token de sesion de un usuario para poder realizar la peticion
        token = self._autenticar_usuario(data)
        headers = {'Authorization': f'Bearer {token}'}
        usuario = self._get_usuario_by_username(data['username'])
        id = usuario.id

        data = {'username': 'nombre_de_usuario'}
        response = self.client.patch(
            path=f'{self.url_api_usuario}{id}/update_username/',
            headers=headers,
            data=data,
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 200)

        # valida que haya actualizado correctamente el username
        usuario_actualizado = Usuario.objects.get(id=id)
        self.assertEquals(data['username'], usuario_actualizado.username)

        """
        Caso de Fallo: Se initenta actualizar el username de un usuario autenticado, con un username invalido
        """

        data = {'username': 'nombre-de-usuario-invalido#$@'}
        response = self.client.patch(
            path=f'{self.url_api_usuario}{id}/update_username/',
            headers=headers,
            data=data,
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

        """
        Caso de Fallo: se intenta modificar el username de un usuario sin enviar el token.
        """
        data = {'username': 'nombre188'}
        response = self.client.patch(
            path=f'{self.url_api_usuario}{id}/update_username/',
            data=data,
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 401)

    def test_api_update_perfil(self):

        """
        Caso de Fallo: el usuario a actualizar, no tiene datos de perfil cargados
        """

        data = self.data_user_1
        response = self.client.post(
            path=self.url_api_usuario,
            data=data
        )
        if response.status_code != 201:
            raise Exception("Error al crear un usuario")

        # obtiene el token de sesion de un usuario para poder realizar la peticion
        token = self._autenticar_usuario(data)
        headers = {'Authorization': f'Bearer {token}'}
        usuario = self._get_usuario_by_username(data['username'])
        id = usuario.id
        data_perfil = {'nombre': 'UsuarioDeTest', 'apellido': 'UsuarioDeTest'}

        cliente = self.client
        response = cliente.put(
            path=f'{self.url_api_usuario}{id}/update_perfil/',
            headers=headers,
            data=data_perfil,
            content_type='application/json',  # Establecer tipo de contenido
        )
        self.assertEquals(response.status_code, 400)



        """
        Caso de exito: se agrega un perfil a un usuario y se actualiza el perfil agregado.
        """
        # se agrega un perfil al usuario creado anteriormente
        data_perfil = {'nombre': 'UsuarioDeTest', 'apellido': 'UsuarioDeTest'}
        path = f'{self.url_api_usuario}{id}/add_perfil/'
        response = self.client.post(
            path=path,
            headers=headers,
            data=data_perfil
        )
        self.assertEquals(response.status_code, 201)

        # se actualizan los datos de perfil
        data_perfil = self.data_perfil_user_2
        response = cliente.put(
            path=f'{self.url_api_usuario}{id}/update_perfil/',
            headers=headers,
            data=data_perfil,
            content_type='application/json',  # Establecer tipo de contenido
        )
        self.assertEquals(response.status_code, 200)

        # obtener usuario actualizado
        usuario_actualizado = self._get_usuario_by_username(data['username'])

        # comparar data para actualizar con el usuario ya actualizado en bd
        self.assertEquals(
            usuario_actualizado.perfil.nombre,
            data_perfil['nombre']
        )
        self.assertEquals(
            usuario_actualizado.perfil.apellido,
            data_perfil['apellido']
        )

        """
        Caso de Fallo: se intenta actualizar sin enviar el token de sesion.
        """

        data_perfil = self.data_perfil_user_2
        response = cliente.put(
            path=f'{self.url_api_usuario}{id}/update_perfil/',
            data=data_perfil,
            content_type='application/json',  # Establecer tipo de contenido
        )
        self.assertEquals(response.status_code, 401)

    def test_api_delete_usuario(self):

        """
        Caso de Exito: se crea un usuario, se autentica y realiza la peticion para eliminar al usuario
        """

        data = self.data_user_1
        response = self.client.post(
            path=self.url_api_usuario,
            data=data
        )
        if response.status_code != 201:
            raise Exception("Error al crear un usuario")

        # obtiene el token de sesion de un usuario para poder realizar la peticion
        token = self._autenticar_usuario(data)
        headers = {'Authorization': f'Bearer {token}'}
        usuario = self._get_usuario_by_username(data['username'])
        id = usuario.id

        response = self.client.delete(
            path=f'{self.url_api_usuario}{id}/',
            headers=headers
        )
        self.assertEquals(response.status_code, 204)

        # verifica que el usuario se elimino
        response = self.client.get(
            path=f'{self.url_api_usuario}{id}/',
            headers=headers
        )
        self.assertEquals(response.status_code, 401)

        """
        Caso de Fallo: se realiza la peticion sin enviar el token de sesion
        """""
        response = self.client.delete(
            path=f'{self.url_api_usuario}{id}/',
        )
        print(response.json())
        self.assertEquals(response.status_code, 401)

    def test_api_change_password(self):

        """
        Caso de exito: se crea un usuario, se autentica y se cambia la contraseña
        :return:
        """

        data = self.data_user_1
        response = self.client.post(
            path=self.url_api_usuario,
            data=data
        )
        if response.status_code != 201:
            raise Exception("Error al crear un usuario")

        # obtiene el token de sesion de un usuario para poder realizar la peticion
        token = self._autenticar_usuario(data)
        headers = {'Authorization': f'Bearer {token}'}
        usuario = self._get_usuario_by_username(data['username'])
        id = usuario.id

        response = self.client.post(
            path=f'{self.url_api_usuario}{id}/set_password/',
            headers=headers,
            data={
                'password': 'leomessi10',
                'password2': 'leomessi10',
            }
        )
        self.assertEquals(response.status_code, 200)

        """
        Caso de Fallo: se envian contraseñas distintas
        """
        response = self.client.post(
            path=f'{self.url_api_usuario}{id}/set_password/',
            headers=headers,
            data={
                'password': 'leo',
                'password2': 'leomessi10',
            }
        )
        self.assertEquals(response.status_code, 400)

        """
        Caso de Fallo: se envian contraseñas invalidas
        """""
        response = self.client.post(
            path=f'{self.url_api_usuario}{id}/set_password/',
            headers=headers,
            data={
                'password': 'leo',
                'password2': 'leo',
            }
        )
        self.assertEquals(response.status_code, 400)
