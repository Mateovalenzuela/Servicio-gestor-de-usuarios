import datetime
from django.test import TestCase
from ..services.PerfilService import PerfilService
from ..models import Usuario, Perfil


class TestPerfilService(TestCase):
    def setUp(self):
        self.valid_user_data = {
            'username': 'test10',
            'email': 'test@email.com',
            'password': 'test1234'
        }

        self.valid_user_data2 = {
            'username': 'test_user',
            'email': 'test_user@gmail.com',
            'password': 'test1234'
        }

        self.valid_perfil_data = {
            'nombre': 'Test',
            'apellido': 'Tester',
            'fecha_nacimiento': datetime.datetime.now().date() - datetime.timedelta(days=10000),
        }

        self.valid_perfil_data2 = {
            'nombre': 'Testsito',
            'apellido': 'Testersito',
            'fecha_nacimiento': datetime.datetime.now().date() - datetime.timedelta(days=10),
        }

        self.service = PerfilService()

    def crear_usuario(self):
        # crea un usuario
        user = Usuario.objects.create_user(
            username=self.valid_user_data['username'],
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        user.save()
        return user

    def add_perfil(self, id):
        user = self.get_user(id)
        perfil = Perfil.objects.create(
            usuario=user,
            nombre=self.valid_perfil_data['nombre'],
            apellido=self.valid_perfil_data['apellido'],
            fecha_nacimiento=self.valid_perfil_data['fecha_nacimiento']
        )
        perfil.save()
        return user


    def crear_usuario2(self):
        # crea un usuario
        user = Usuario.objects.create_user(
            username=self.valid_user_data2['username'],
            email=self.valid_user_data2['email'],
            password=self.valid_user_data2['password']
        )
        user.save()
        return user

    def get_user(self, id):
        user = Usuario.objects.get(id=id, is_active=True)
        return user

    def test_add_perfil_to_user(self):
        """
        Caso de fallo: Añadir un perfil válido a un usuario inexistente
        """
        id = 100
        response = self.service.add_perfil_to_user(
            id=id,
            nombre=self.valid_perfil_data['nombre'],
            apellido=self.valid_perfil_data['apellido'],
            fecha_nacimiento=self.valid_perfil_data['fecha_nacimiento'],
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de éxito: Añadir un perfil válido a un usuario existente
        """
        user = self.crear_usuario()
        id = user.id
        response = self.service.add_perfil_to_user(
            id=id,
            nombre=self.valid_perfil_data['nombre'],
            apellido=self.valid_perfil_data['apellido'],
            fecha_nacimiento=self.valid_perfil_data['fecha_nacimiento'],
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)
        self.assertIn('message', data)

        """
        Caso de fallo: Añadir un perfil a un usuario que ya tiene un perfil
        """
        id = id
        response = self.service.add_perfil_to_user(
            id=id,
            nombre=self.valid_perfil_data['nombre'],
            apellido=self.valid_perfil_data['apellido'],
            fecha_nacimiento=self.valid_perfil_data['fecha_nacimiento'],
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('message', data)

        """
        Caso de fallo: Añadir un perfil con datos inválidos
        """
        user2 = self.crear_usuario2()
        id = user2.id
        response = self.service.add_perfil_to_user(
            id=id,
            nombre='messi23342',
            apellido='messi%^&*',
            fecha_nacimiento='20-20-200000',
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('nombre', data)
        self.assertIn('apellido', data)
        self.assertIn('fecha_nacimiento', data)

        """
        Caso de fallo: Añadir un perfil con fecha inválida, superior a la actual
        """
        id = user2.id
        response = self.service.add_perfil_to_user(
            id=id,
            nombre='leo',
            apellido='messi',
            fecha_nacimiento=datetime.datetime.now().date() + datetime.timedelta(days=100),
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('fecha_nacimiento', data)

        """"
        Caso de fallo: id totalmente inválido
        """
        id = 'user2.id'
        response = self.service.add_perfil_to_user(
            id=id,
            nombre='leo',
            apellido='messi',
            fecha_nacimiento=datetime.datetime.now().date() - datetime.timedelta(days=100),
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)
        self.assertIn('error', data)
    def test_update_perfil_to_user(self):
        """
        Caso de fallo: actualizar un perfil de un usuario inexistente
        """
        response = self.service.update_perfil_to_user(
            user_id=100,
            nombre=self.valid_perfil_data['nombre'],
            apellido=self.valid_perfil_data['apellido'],
            fecha_nacimiento=self.valid_perfil_data['fecha_nacimiento']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de fallo: actualizar el perfil de un usuario que no tiene perfil
        """
        user = self.crear_usuario()
        id = user.id
        response = self.service.update_perfil_to_user(
            user_id=id,
            nombre=self.valid_perfil_data['nombre'],
            apellido=self.valid_perfil_data['apellido'],
            fecha_nacimiento=self.valid_perfil_data['fecha_nacimiento']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de exito: actualizar el perfil de un usuario con datos validos
        """
        id = id
        user = self.add_perfil(id)
        id = user.id
        response = self.service.update_perfil_to_user(
            user_id=id,
            nombre=self.valid_perfil_data2['nombre'],
            apellido=self.valid_perfil_data2['apellido'],
            fecha_nacimiento=self.valid_perfil_data2['fecha_nacimiento']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)
        self.assertIn('message', data)

        user = self.get_user(id)
        self.assertEqual(user.perfil.nombre, self.valid_perfil_data2['nombre'])
        self.assertEqual(user.perfil.apellido, self.valid_perfil_data2['apellido'])
        self.assertEqual(user.perfil.fecha_nacimiento, self.valid_perfil_data2['fecha_nacimiento'])

        """
        Caso de fallo: datos de perfil invalidos
        """
        user = self.crear_usuario2()
        user = self.add_perfil(user.id)
        id = user.id
        response = self.service.update_perfil_to_user(
            user_id=id,
            nombre='self.valid_perfil_data2[]',
            apellido='self.valid_perfil_data2['']',
            fecha_nacimiento='self.valid_perfil_data2[]'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('nombre', data)
        self.assertIn('apellido', data)
        self.assertIn('fecha_nacimiento', data)

        """
        Caso de fallo: id totalmente invalido
        """
        response = self.service.update_perfil_to_user(
            user_id='True',
            nombre=self.valid_perfil_data2['nombre'],
            apellido=self.valid_perfil_data2['apellido'],
            fecha_nacimiento=self.valid_perfil_data2['fecha_nacimiento']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)
        self.assertIn('error', data)
