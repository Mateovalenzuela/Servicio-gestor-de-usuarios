import json

from django.test import TestCase, Client
from django.contrib.auth.models import User
from .serializers import UsuarioSerializer


# Create your tests here.

class UsuarioTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='test',
            password='test1234',
            first_name='Leo',
            last_name='Messi'
        )

        self.valid_user = {
            'username': 'messi',
            'password': 'messi123',
            'email': 'messi@gmail.com',
            'first_name': 'Leo',
            'last_name': 'Messi'
        }

        self.logged_user = self.client.post(
            '/api/usuario/login/',
            data={'username': 'test', 'password': 'test1234'})

    def test_api_create_user(self):
        response = self.client.post(
            '/api/usuario/usuarios/',
            self.valid_user,
        )

    def test_api_login(self):
        response = self.client.post(
            '/api/usuario/login/',
            data={'username': 'test', 'password': 'test1234'}
        )
        self.assertEquals(response.status_code, 201)

    def test_create_and_login(self):
        # crea el usuario
        response = self.client.post(
            '/api/usuario/usuarios/',
            data=self.valid_user,
        )
        self.assertEquals(response.status_code, 201)

        # inicia sesion con el usuario
        response = self.client.post(
            '/api/usuario/login/',
            data=self.valid_user
        )
        self.assertEquals(response.status_code, 201)

    def test_api_protected_view(self):
        data = dict(self.logged_user.json())
        token = data['token']
        response = self.client.get(
            '/api/usuario/vista/',
            headers={'Authorization': f'Token {token}'}
        )
        self.assertEquals(response.status_code, 200)

    def test_api_get_all_users(self):
        response = self.client.get(
            '/api/usuario/usuarios/'
        )
        self.assertEquals(response.status_code, 200)

    def test_api_get_one_user(self):
        id = self.user.id
        response = self.client.get(
            f'/api/usuario/usuarios/{id}/'
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            dict(response.json()),
            UsuarioSerializer(self.user).data
            )  # compara usuario recibido con usuario creado, ambos en formato dict

    def test_api_update_user(self):
        id = self.user.id
        data = {'first_name': 'UsuarioDeTest', 'last_name': 'UsuarioDeTest'}
        response = self.client.put(
            f'/api/usuario/usuarios/{id}/',
            data=json.dumps(data),  # Convertir datos a JSON
            content_type='application/json',  # Establecer tipo de contenido
        )
        self.assertEquals(response.status_code, 200)

        # obtener usuario actualizado
        usuario_actualizado = self.client.get(
            f'/api/usuario/usuarios/{id}/'
        )
        self.assertEquals(usuario_actualizado.status_code, 200)

        # comparar data para actualizar con el usuario ya actualizado en bd
        usuario_actualizado = dict(usuario_actualizado.json())
        self.assertEquals(
            usuario_actualizado['first_name'],
            data['first_name']
        )
        self.assertEquals(
            usuario_actualizado['last_name'],
            data['last_name']
        )
