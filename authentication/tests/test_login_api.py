from django.test import TestCase, Client
from ..models import Usuario, Perfil


# Create your tests here.

class TestLoginAPI(TestCase):

    def setUp(self):
        self.client = Client()
        self.url_api_usuario = '/api/usuario/'
        self.url_api_login = '/api/login/'
        self.url_api_logout = '/api/logout/'
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
            data={'email': 'test@mail.com', 'password': 'test1234'})

    def test_api_login(self):
        response = self.client.post(
            path=self.url_api_login,
            data={'email': 'test@mail.com', 'password': 'test1234'}
        )
        self.assertEquals(response.status_code, 200)

    def test_create_and_login(self):
        # Crea el usuario
        response = self.client.post(
            path=self.url_api_usuario,
            data=self.valid_user,
        )
        self.assertEqual(response.status_code, 201)

        # Inicia sesión con el usuario recién creado
        response = self.client.post(
            path=self.url_api_login,
            data={'email': self.valid_user['email'], 'password': self.valid_user['password']}
        )
        self.assertEqual(response.status_code, 200)

        # Verifica que el usuario está autenticado
        self.assertTrue(self.client.login(username=self.valid_user['email'], password=self.valid_user['password']))

    def test_api_logout(self):
        data = dict(self.logged_user.json())['data']
        token = data['access_token']

        response = self.client.post(
            path=self.url_api_logout,
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEquals(response.status_code, 200)

        # caso de fallo, token invalido
        token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEzODQ5Njk1LCJpYXQiOjE3MTM3NjMyOTUsImp0aSI6ImI2NWRhNTc2NGYyMzQ1Mjk4MmEyMjczOGU3MjNjYzY3IiwidXNlcl9pZCI6MX0.NaUZPJK0ie5WryDX1mGOu7eUQPs-p2kh__JVYxPBla61d76Tv114GpmDmkjnMr1YSc5aK3x7yDIzGKeMuWAcoSA_wczE5dtZ0LFmX3JPVC0zr31qmnZ75qcLJT193ZU6z4Y_42MYqX8Nr0B_MV3fZ6OkqVS7O2cOBfMNouuT3USLo8sqJ5qx19sB0NJW_A77ZI9X17ssV5TXEZQ_vNELcisvbo7c-d3JpghwANEohdZNzS_y39J5lPcZhDJ4BSmqRkt7fBqvpQQvrG42JnpFYtAhbaTpi99sXeBA0dLQdsMYMmdoWD4OmAvSX4Y2e4DrAq5u2q8xeab7OTUfV9'
        response = self.client.post(
            path=self.url_api_logout,
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEquals(response.status_code, 401)

    def test_api_protected_view(self):
        data = dict(self.logged_user.json())['data']
        token = data['access_token']
        response = self.client.get(
            path=f'/vista/',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEquals(response.status_code, 200)
