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

        self.valid_perfil_user = {
            "nombre": 'Leo',
            "apellido": 'Messi',
        }

        self.valid_user = {
            'username': 'messi',
            'password': 'messi123',
            'email': 'messi@gmail.com'
        }

        self.logged_user = self.client.post(
            path=self.url_api_login,
            data={'username': 'test', 'password': 'test1234'})

    def test_api_create_user(self):
        response = self.client.post(
            path=self.url_api_usuario,
            data=self.valid_user,
        )
        self.assertEquals(response.status_code, 201)

    def test_api_add_perfil(self):
        # agrega un usuario sin perfil
        usuario = Usuario.objects.create_user(
            username='temp',
            password='temp',
            email='temp@email.com'
        )
        usuario.save()

        path = f'{self.url_api_usuario}{usuario.id}/add_perfil/'
        response = self.client.post(
            path=path,
            data=self.valid_perfil_user
        )
        self.assertEquals(response.status_code, 201)

    def test_api_get_all_users(self):
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
        id = self.user.id
        response = self.client.get(
            path=f'{self.url_api_usuario}{id}/'
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            dict(response.json()),
            UsuarioSerializer(self.user).data
        )  # compara usuario recibido con usuario creado, ambos en formato dict


    def test_api_update_username(self):
        id = self.user.id
        data = {'username': 'nombre_de_usuario'}
        response = self.client.patch(
            path=f'{self.url_api_usuario}{id}/update_username/',
            data=data,
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 200)

        # valida que haya actualizado correctamente el username
        usuario_actualizado = Usuario.objects.get(id=id)
        self.assertEquals(data['username'], usuario_actualizado.username)

        # Caso de error con username invalido
        id = self.user.id
        data = {'username': 'nombre-de-usuario-invalido#$@'}
        response = self.client.patch(
            path=f'{self.url_api_usuario}{id}/update_username/',
            data=data,
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_api_update_perfil(self):
        id = self.user.id
        data = {'nombre': 'UsuarioDeTest', 'apellido': 'UsuarioDeTest'}

        cliente = self.client
        response = cliente.put(
            path=f'{self.url_api_usuario}{id}/update_perfil/',
            data=data,
            content_type='application/json',  # Establecer tipo de contenido
        )
        self.assertEquals(response.status_code, 200)

        # obtener usuario actualizado
        usuario_actualizado = Usuario.objects.get(id=id)

        # comparar data para actualizar con el usuario ya actualizado en bd
        self.assertEquals(
            usuario_actualizado.perfil.nombre,
            data['nombre']
        )
        self.assertEquals(
            usuario_actualizado.perfil.apellido,
            data['apellido']
        )

    def test_api_delete_usuario(self):

        user_id = self.user.id

        response = self.client.delete(
            path=f'{self.url_api_usuario}{user_id}/',
        )
        self.assertEquals(response.status_code, 204)

        # Caso de fallo
        user_id = 34
        response = self.client.delete(
            path=f'{self.url_api_usuario}{user_id}/',
        )
        self.assertEquals(response.status_code, 404)

    def test_api_change_password(self):
        user_id = self.user.id

        response = self.client.post(
            path=f'{self.url_api_usuario}{user_id}/set_password/',
            data={
                'password': 'leomessi10',
                'password2': 'leomessi10',
            }
        )
        self.assertEquals(response.status_code, 200)

        # caso de fallo 1
        response = self.client.post(
            path=f'{self.url_api_usuario}{user_id}/set_password/',
            data={
                'password': 'leo',
                'password2': 'leomessi10',
            }
        )
        self.assertEquals(response.status_code, 400)

        # caso de fallo 2
        response = self.client.post(
            path=f'{self.url_api_usuario}{user_id}/set_password/',
            data={
                'password': 'leo',
                'password2': 'leo',
            }
        )
        self.assertEquals(response.status_code, 400)
