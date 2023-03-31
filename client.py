import asyncio
from http import HTTPStatus
import aioconsole
import aiohttp

from messages import WELCOM_MESSAGE


class Client:
    def __init__(self, server_host="127.0.0.1", server_port=8000):
        self.server_host = server_host
        self.server_port = server_port
        self.token: str = ''
        self.chats: list = []
        self.current_chat_id: int = 1
        self.current_dialog_id: int = 0
        self.login_endpoint = (
            f'http://{server_host}:{str(server_port)}/login/'
        )
        self.reg_endpoint = (
            f'http://{server_host}:{str(server_port)}/reg/'
        )
        self.chat_endpoint = (
            f'http://{server_host}:{str(server_port)}/chat/'
        )
        self.dialog_endpoint = (
            f'http://{server_host}:{str(server_port)}/dialog/'
        )
        self.received_messages: list = []
        self.sending_messages: list = []


    async def run(self):
        async with aiohttp.ClientSession() as session:
            await self.authentication(session)
            task1 = asyncio.create_task(self.check_chat(session))
            task2 = asyncio.create_task(self.process_input(session))
            task3 = asyncio.create_task(self.check_dialog(session))

            # операции отправки и получения данных выполняем конкурентно
            await asyncio.gather(task1, task2, task3)

    async def authentication(self, session: aiohttp.ClientSession):
        message = WELCOM_MESSAGE
        while not self.token:
            inpt = await aioconsole.ainput(message)
            inpt = inpt.split()
                
            if inpt[0] == '$$login' or inpt[0] == '$$reg':
                data = {
                    'username': inpt[1],
                    'password': inpt[2]
                }
                if inpt[0] == '$$login':
                    url = self.login_endpoint 
                else:
                    url = self.reg_endpoint
                async with session.post(url, json=data) as response:
                    data = await response.json()
                    if response.status == HTTPStatus.OK or response.status == HTTPStatus.CREATED:
                        self.token = data['token']
                        self.chats = data['chats']
                        print('Вы вошли в общий чат.')
                    else:
                        print(data['error'])
            
            message = 'Введите корректную команду.\n'
                        
    async def check_chat(self, session: aiohttp.ClientSession):
        first = 1
        while True:
            chat_id = self.current_chat_id
            if chat_id == 0:
                await asyncio.sleep(0.1)
                continue
            await asyncio.sleep(0.1)
            url = f'{self.chat_endpoint}{chat_id}/?first={first}'
            headers = {
                'token': self.token
            }
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                if self.current_chat_id == chat_id:
                    first = 0
                    messages = data['messages']
                    for message in messages:
                        print(message)

    async def process_input(self, session: aiohttp.ClientSession):
        while True:
            await asyncio.sleep(0.1)
            inpt = await aioconsole.ainput()
            command = inpt.split()[0]
            if command == '$$users':
                await self.get_chat_users(session)
                continue

            if command == '$$dialog':
                user = inpt.split()[1]
                # если none
                id = await self.get_dialog(session, user)
                self.current_dialog_id = int(id)
                self.current_chat_id = 0
                print(f'Диалог с пользователем {user}')
                continue

            if command == '$$chat':
                chat_name = inpt.split()[1]
                id, name = await self.get_chat(session, chat_name)
                self.current_chat_id = int(id)
                self.current_dialog_id = 0
                print(f'Вы перешли в чат {name}')
                continue
            
            await self.send(session, inpt)        

    async def send(self, session: aiohttp.ClientSession, message: str):
        chat_id = self.current_chat_id
        if chat_id != 0:
            url = f'{self.chat_endpoint}{chat_id}/send/'
            data = {'text': message}
            headers = {
                'token': self.token
            }
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == HTTPStatus.BAD_REQUEST:
                    print(data['error'])
            return
        dialog_id = self.current_dialog_id
        if dialog_id != 0:
            url = f'{self.dialog_endpoint}{dialog_id}/send/'
            data = {'text': message}
            headers = {
                'token': self.token
            }
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == HTTPStatus.BAD_REQUEST:
                    print(data['error'])
            return

    async def get_chat_users(self, session: aiohttp.ClientSession):
        chat_id = self.current_chat_id
        url = f'{self.chat_endpoint}{chat_id}/users/'
        headers = {
            'token': self.token
        }
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            users = data['users']
            print(users)

    async def get_dialog(self, session: aiohttp.ClientSession, user: str):
        url = f'{self.dialog_endpoint}{user}/get_id/'
        headers = {
            'token': self.token
        }
        async with session.get(url, headers=headers) as response:
            # если error
            data = await response.json()
            id = data['id']
            return id
        
    async def get_chat(self, session: aiohttp.ClientSession, name: str):
        url = f'{self.chat_endpoint}{name}/get_id/'
        headers = {
            'token': self.token
        }
        async with session.get(url, headers=headers) as response:
            # если error
            data = await response.json()
            id = data['id']
            name = data['name']
            return id, name

    async def check_dialog(self, session: aiohttp.ClientSession):
        while True:
            dialog_id = self.current_dialog_id
            if dialog_id == 0:
                await asyncio.sleep(0.1)
                continue
            url = f'{self.dialog_endpoint}{dialog_id}/'
            headers = {
                'token': self.token
            }
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                if self.current_dialog_id == dialog_id:
                    messages = data['messages']
                    for message in messages:
                        print(message)

if __name__ == '__main__':
    asyncio.run(Client().run())