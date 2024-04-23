from django.test import TestCase
from ..services.UsuarioService import UsuarioService
from ..models import Usuario


class TestUsuarioService(TestCase):

    def setUp(self):
        self.valid_user_data = {
            'username': 'test10',
            'email': 'test@email.com',
            'password': 'test1234'
        }

        self.service = UsuarioService()

    def crear_usuario(self):
        # crea un usuario
        user = Usuario.objects.create_user(
            username=self.valid_user_data['username'],
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        user.save()
        return user

    def get_user(self, id):
        user = Usuario.objects.get(id=id, is_active=True)
        return user

    def test_get_object_user(self):

        """
        Caso de fallo: obtener un usuario con base de datos vacia
        :return: none
        """
        response = self.service.get_object_user(1)
        self.assertEqual(response, None)


        """
        Caso de exito: obtener un usuario con id valido
        """
        user = self.crear_usuario()
        response = self.service.get_object_user(user.id)
        self.assertEqual(response.id, user.id)

        """
        Caso de fallo: id inexistente
        """
        response = self.service.get_object_user(100)
        self.assertEqual(response, None)

        """
        Caso de exito: id de tipo char
        """
        id = '1'
        with self.assertRaises(Exception):
            response = self.service.get_object_user(id)

        """
        Caso de Fallo: id totalmente extraño de tipo string, lanza una excepcion
        """
        id = 'id_invalido'
        with self.assertRaises(Exception):
            self.service.get_object_user(id)

    def test_list_all_users(self):
        """
        Caso de fallo: no hay usuarios en base de datos
        :return:
        """
        response = self.service.list_all_users()
        status = response.status_code
        data = response.data['data']

        self.assertEqual(status, 200)
        self.assertEqual(len(data), 0)
        self.assertEqual(data, [])  # Verificar que la lista esté vacía

        """
        Caso de éxito: obtener una lista de usuarios
        :return:
        """
        user = self.crear_usuario()
        response = self.service.list_all_users()
        status = response.status_code
        data = response.data['data']

        self.assertEqual(status, 200)
        self.assertEqual(len(data), 1)  # Verificar que la lista tenga un elemento
        self.assertEqual(data[0]['username'], 'test10')  # Verificar el contenido del usuario

    def test_list_one_user(self):
        """
        Caso de fallo: no hay usuarios en base de datos
        :return:
        """
        id = 1
        response = self.service.list_one_user(id)
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de éxito: obtener un usuario en formato dict
        """
        user = self.crear_usuario()
        id = user.id
        response = self.service.list_one_user(id)
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)

        """
        Caso de fallo: id en formato str
        """
        id = str(user.id)
        response = self.service.list_one_user(id)
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)

        """
        Caso de fallo: id valido pero inexistente
        """
        id = 100
        response = self.service.list_one_user(id)
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de fallo: id invalido, en formato str
        """
        id = 'id_invalido'
        response = self.service.list_one_user(id)
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)

    def test_create_user(self):
        """
        Caso de éxito: crear un usuario con datos válidos
        :return:
        """
        response = self.service.create_user(
            username=self.valid_user_data['username'],
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 201)

        """
        Caso de fallo: username invalido
        """
        response = self.service.create_user(
            username='I',
            email='email@valido.com',
            password='password123'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('username', data)

        """
        Caso de fallo: password invalido
        """
        response = self.service.create_user(
            username='username',
            email='email1@valido.com',
            password='pass'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('password', data)

        """
        Caso de fallo: email invalido
        """
        response = self.service.create_user(
            username='username2',
            email='emailInvalido.com.@.valido.com',
            password='password123'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('email', data)

        """
        Caso de fallo: datos incompletos
        """
        response = self.service.create_user(
            username=None,
            email=None,
            password=None
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('username', data)
        self.assertIn('password', data)
        self.assertIn('email', data)

        """
        Caso de fallo: datos incompletos, username
        """
        response = self.service.create_user(
            username=None,
            email='valid.email@gmail.com',
            password='password111'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('username', data)

        """
        Caso de fallo: datos incompletos, email
        """
        response = self.service.create_user(
            username='user1212',
            email=None,
            password='password111'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('email', data)

        """
        Caso de fallo: datos incompletos, password
        """
        response = self.service.create_user(
            username='user5050',
            email='email@email.com',
            password=None
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('password', data)

        """
        Caso de fallo: datos repetidos, username, ya existe un usuario con este username
        """
        response = self.service.create_user(
            username=self.valid_user_data['username'],
            email='email10@gmail.com',
            password='passs1234'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('username', data)

        """
        Caso de fallo: datos repetidos, email, ya existe un usuario con este email
        """
        response = self.service.create_user(
            username='user777',
            email=self.valid_user_data['email'],
            password='pass34555'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('email', data)

        """
        Caso de fallo: datos repetidos, username y email
        """
        response = self.service.create_user(
            username=self.valid_user_data['username'],
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('username', data)
        self.assertIn('email', data)

        """
            Caso de fallo: parametros invalidos
        """
        response = self.service.create_user(
            username=100,
            email=True,
            password=5.5
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('username', data)
        self.assertIn('email', data)
        self.assertIn('password', data)

    def test_set_password_user(self):
        """
        Caso de fallo: set password a un usuario que no existe en base de datos
        """
        response = self.service.set_password_user(
            id=100,
            password='password',
            password2='password'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de éxito: set password a un usuario válido
        """
        user = self.crear_usuario()
        id = user.id
        password = 'password'
        response = self.service.set_password_user(
            id=id,
            password=password,
            password2=password
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)
        self.assertIn('message', data)
        user = self.get_user(id)
        self.assertTrue(user.check_password(password))

        """
        Caso de fallo: set password con id válido pero passwords distintos
        """
        id = user.id
        password = 'password'
        response = self.service.set_password_user(
            id=id,
            password=password,
            password2='password distinto'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('password', data)

        """
        Caso de fallo: set password con id válido pero passwords inválidos
        """
        id = user.id
        password = 'pass'
        response = self.service.set_password_user(
            id=id,
            password=password,
            password2=password
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('password', data)

        """
        Caso de fallo: set password con id inválido en string
        """
        id = 'user.id'
        password = 'password'
        response = self.service.set_password_user(
            id=id,
            password=password,
            password2=password
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)
        self.assertIn('error', data)

        """
        Caso de fallo: set password con datos totalmente inválidos
        """
        id = '1'
        password = 'password'
        response = self.service.set_password_user(
            id=id,
            password=10,
            password2=True
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)

    def test_update_email_user(self):
        """
        Caso de fallo: update un email de un usuario inexistente en base de datos
        :return:
        """

        response = self.service.update_email_user(
            id=1,
            email='email@test.com',
            password=self.valid_user_data['password']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de éxito: update un email de un usuario válido
        """
        user = self.crear_usuario()
        id = user.id
        email = 'nuevo_email@test.com'
        response = self.service.update_email_user(
            id=id,
            email=email,
            password=self.valid_user_data['password']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)
        self.assertIn('message', data)
        user = self.get_user(id)
        self.assertEqual(email, user.email)

        """
        Caso de fallo: update un email con contraseña incorrecta
        """
        response = self.service.update_email_user(
            id=id,
            email=self.valid_user_data['email'],
            password='password_incorrecta_1'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 401)

        """
        Caso de fallo, no se envía una contraseña del usuario
        """
        response = self.service.update_email_user(
            id=id,
            email=self.valid_user_data['email'],
            password=None
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('password', data)

        """
        Caso de fallo, email nuevo inválido
        """
        email_nuevo = 'invalid_email@,com'
        response = self.service.update_email_user(
            id=id,
            email=email_nuevo,
            password=self.valid_user_data['password']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('email', data)

        """
        Caso de fallo, se actualiza el email de un usuario no existente
        """

        response = self.service.update_email_user(
            id=100,
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de fallo, datos totalmente invlaidos
        """
        response = self.service.update_email_user(
            id='invalid_id',
            email=33,
            password=False
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)

    def test_update_username_user(self):
        """
        Caso de fallo, se intenta actualizar un username de un usuario con base de datos vacía
        """
        nuevo_username_valido = 'messi_10'
        response = self.service.update_username_user(
            id=1,
            username=nuevo_username_valido
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de éxito, se actualiza un usuario existente con datos válidos
        """
        usuario_nuevo = self.crear_usuario()
        id = usuario_nuevo.id
        response = self.service.update_username_user(
            id=id,
            username=nuevo_username_valido,
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)
        self.assertIn('message', data)
        self.assertEqual(nuevo_username_valido, self.get_user(id).username)

        """
        Caso de fallo, se actualiza un usuario existente con datos inválidos
        """
        username_invalido = 'messi@10'
        id = usuario_nuevo.id
        response = self.service.update_username_user(
            id=id,
            username=username_invalido,
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('username', data)

        """
        Caso de fallo, id inválido
        """
        nuevo_username_valido += '10'
        id = usuario_nuevo.id
        response = self.service.update_username_user(
            id=100,
            username=nuevo_username_valido,
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de fallo, datos totalmente inválidos
        """
        username_invalido = 'usuario_nuevo_id'
        id = 'usuario_nuevo.id'
        response = self.service.update_username_user(
            id=id,
            username=username_invalido,
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)
        self.assertIn('error', data)

    def test_delete_user(self):
        """
        Caso de fallo, se elimina un usuario inexistente
        """
        id = 100
        response = self.service.delete_user(
            id=id,
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de fallo, se elimina un usuario existente
        """
        usuario_nuevo = self.crear_usuario()
        self.assertTrue(usuario_nuevo.is_active)
        id = usuario_nuevo.id
        response = self.service.delete_user(
            id=id,
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)
        self.assertIn('message', data)
        with self.assertRaises(Exception):
            self.get_user(id)

        user = Usuario.objects.get(id=id)
        self.assertFalse(user.is_active)

        """
        Caso de fallo, se elimina un usuario ya eliminado
        """
        id = usuario_nuevo.id
        response = self.service.delete_user(
            id=id,
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        with self.assertRaises(Exception):
            self.get_user(id)
        user = Usuario.objects.get(id=id)
        self.assertFalse(user.is_active)

        """
        Caso de fallo, id totalmente inválido
        """
        id = 'usuario_nuevo.id'
        response = self.service.delete_user(
            id=id,
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)
        self.assertIn('error', data)













    