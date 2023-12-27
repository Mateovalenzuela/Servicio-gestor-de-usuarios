from django.test import TestCase, Client
from ..serializers import UsuarioSerializer


class TestUsuarioViewSet(TestCase):
    def setUp(self):
        self.client = Client()
        self.url_api_usuario = '/api/usuario/'
        self.url_api_login = '/api/login/'
        self.model_usuario = UsuarioSerializer.Meta.model

        self.user = self.model_usuario.objects.create_user(
            username='test',
            password='test1234',
            email='test@mail.com',
            nombre='Leo',
            apellido='Messi'
        )

        self.valid_user = {
            'username': 'messi',
            'password': 'messi123',
            'email': 'messi@gmail.com',
            'nombre': 'Leo',
            'apellido': 'Messi',
            'fecha_nacimiento': '12-03-03'
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

    def test_api_get_all_users(self):
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

    def test_api_update_user(self):
        id = self.user.id
        data = {'nombre': 'UsuarioDeTest', 'apellido': 'UsuarioDeTest'}

        cliente = self.client
        response = cliente.put(
            path=f'{self.url_api_usuario}{id}/',
            data=data,
            content_type='application/json',  # Establecer tipo de contenido
        )
        self.assertEquals(response.status_code, 200)

        # obtener usuario actualizado
        usuario_actualizado = cliente.get(
            path=f'{self.url_api_usuario}{id}/'
        )
        self.assertEquals(usuario_actualizado.status_code, 200)

        # comparar data para actualizar con el usuario ya actualizado en bd
        usuario_actualizado = dict(usuario_actualizado.json())
        self.assertEquals(
            usuario_actualizado['nombre'],
            data['nombre']
        )
        self.assertEquals(
            usuario_actualizado['apellido'],
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
