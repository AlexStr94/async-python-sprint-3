import unittest
from datetime import datetime
from uuid import uuid4

from aiohttp.test_utils import AioHTTPTestCase

from db_manager import initialize_db
from models import Chat, User, UserChat
from server import Server
from views import routes


class TestServer(AioHTTPTestCase):
    USER_DATA = {
        'username': 'nobodytakesuchusername',
        'password': 'nobodytakesuchusername'
    }
    USER_DATA2 = {
        'username': 'nobodytakesuchusername2',
        'password': 'nobodytakesuchusername2'
    }

    @classmethod
    def setUpClass(cls):
        initialize_db()
        user = User.create(
            username=cls.USER_DATA2['username'],
            password=cls.USER_DATA2['password'],
            token=str(uuid4())
        )
        print(user)
        chat, _ = Chat.get_or_create(name='Common')
        UserChat.get_or_create(
            user=user,
            chat=chat,
            last_check=datetime.now()
        )

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        server = Server('127.0.0.1', 8000)
        app = server.server
        app.add_routes(routes)

        return app

    async def test_reg_endpoint(self):
        async with self.client.request("POST", "/reg/", json=self.USER_DATA) as response:
            data = await response.json()
            self.assertEqual(response.status, 201)
            self.assertTrue(
                data['token'], 'Нет токена в ответе при регистрации')
            self.assertTrue(
                data['chats'], 'Нет списка чатов в ответе при регистрации')

    async def test_login_endpoint(self):
        async with self.client.request("POST", "/login/", json=self.USER_DATA2) as response:
            data = await response.json()
            self.assertEqual(response.status, 200)
            self.assertTrue(data['token'], 'Нет токена в ответе при входе')
            self.assertTrue(
                data['chats'], 'Нет списка чатов в ответе при входе')

    @classmethod
    def tearDownClass(cls):
        User.get(username='nobodytakesuchusername').delete_instance()
        User.get(username='nobodytakesuchusername2').delete_instance()


if __name__ == '__main__':
    unittest.main()
