from datetime import datetime
from http import HTTPStatus
from uuid import uuid4

import peewee as pw
from aiohttp import web

from decorators import check_user_token
from logger import server_logger
from models import Chat, ChatMessage, Dialog, DialogMessage, User, UserChat
from settings import MESSAGE_LIMIT

routes = web.RouteTableDef()


@routes.post('/login/')
async def login(request: web.BaseRequest) -> web.json_response:
    data = await request.json()
    username = data['username']
    password = data['password']
    server_logger.info(
        f'Try to login. Username: {username}'
    )
    try:
        user = User.get(username=username, password=password)
        if not user.token:
            token = str(uuid4())
            user.token = token
            user.save()
        responce = {
            'token': user.token,
            'chats': [
                chat.chat.id for chat in list(user.chats)
            ]
        }
        server_logger.info(
            f'{username} logged succesfully'
        )

        return web.json_response(
            responce,
            status=HTTPStatus.OK
        )
    except User.DoesNotExist as e:
        server_logger.info(e)
        return web.json_response(
            {'error': 'Пользователь не найден. Попробуйте еще раз.\n'},
            status=HTTPStatus.BAD_REQUEST
        )


@routes.post('/reg/')
async def reg(request: web.BaseRequest) -> web.json_response:
    data = await request.json()
    username = data['username']
    password = data['password']
    server_logger.info(
        f'Try to login. Username: {username}'
    )
    try:
        user = User.create(
            username=username,
            password=password,
            token=str(uuid4())
        )
        chat = Chat.get(name='Common')
        UserChat.create(
            chat=chat,
            user=user,
            last_check=datetime.now()
        )
        responce = {
            'token': user.token,
            'chats': [chat.id]
        }

        return web.json_response(
            responce,
            status=HTTPStatus.CREATED
        )

    except pw.IntegrityError as e:
        server_logger.info(e)
        return web.json_response(
            {'error': 'Пользователь с таким логином уже зарегистрирован.\n'},
            status=HTTPStatus.BAD_REQUEST
        )


@check_user_token
@routes.get('/chat/{name}/get_id/')
async def get_chat_id(request: web.BaseRequest) -> web.json_response:
    name = request.match_info['name']
    server_logger.info(
        f'Try to connect chat "{name}"'
    )
    try:
        chat = Chat.get(name=name)

        responce = {
            'id': chat.id,
            'name': chat.name
        }

        return web.json_response(
            responce,
            status=HTTPStatus.OK
        )
    except Chat.DoesNotExist as e:
        server_logger.info(e)
        return web.json_response(
            {'error': 'Чата с таким названием не существует\n'},
            status=HTTPStatus.BAD_REQUEST
        )


@check_user_token
@routes.post('/chat/{id}/send/')
async def send_message_to_chat(request: web.BaseRequest) -> web.json_response:
    data = await request.json()
    text = data['text']

    token = request.headers.get('token')
    user = User.get(
        token=token
    )
    
    chat_id = request.match_info['id']
    chat = Chat.get(id=chat_id)

    server_logger.info(
        f'{user} try to send message {text}'
    )

    ChatMessage.create(
        chat=chat,
        user=user,
        text=text,
        date=datetime.now()
    )

    server_logger.info(
        f'{user} send message succesfully'
    )

    return web.json_response(
        status=HTTPStatus.OK
    )


@check_user_token
@routes.get('/chat/{id}/users/')
async def get_chat_users(request: web.BaseRequest) -> web.json_response:
    chat_id = request.match_info['id']
    chat = Chat.get(id=chat_id)
    user_chats = UserChat.filter(
        chat=chat,
    )
    users = 'Участники чата: '
    for user_chat in user_chats:
        users += f'{user_chat.user}, '

    return web.json_response(
        {'users': users},
        status=HTTPStatus.OK
    )


@check_user_token
@routes.get('/chat/{id}/')
async def get_chat(request: web.BaseRequest) -> web.json_response:
    token = request.headers.get('token')

    user = User.get(
        token=token
    )

    chat_id = request.match_info['id']
    chat = Chat.get(id=chat_id)
    user_chat = UserChat.get(
        chat=chat,
        user=user
    )
    first = int(request.query['first'])
    client_last_check = request.query.get('last_check')
    if not client_last_check:
        last_check = user_chat.last_check
    else:
        last_check = datetime.strptime(client_last_check, '%m/%d/%Y,%H:%M:%S.%f')
    user_chat.last_check = datetime.now()
    # last_check = user_chat.last_check
    # if first:
    #     last_messages = ChatMessage.select() \
    #         .where(ChatMessage.chat == chat) \
    #         .order_by(ChatMessage.date.desc()) \
    #         .limit(MESSAGE_LIMIT)[::-1]
    # else:
    last_messages = ChatMessage.select() \
        .where(ChatMessage.chat == chat) \
        .where(ChatMessage.date > last_check) \
        .order_by(ChatMessage.date.desc())
    if first and last_messages.count() < 20:
        last_messages = ChatMessage.select() \
            .where(ChatMessage.chat == chat) \
            .order_by(ChatMessage.date.desc()) \
            .limit(MESSAGE_LIMIT)[::-1]

    last_messages_formatted = []

    for message in last_messages:
        date = message.date.strftime('%d/%m, %H:%M:%S')
        text = message.text
        message_user = message.user
        if message_user == user:
            text = f'[{date}] Вы: {text}'
        else:
            text = f'[{date}] {message_user.username}: {text}'

        last_messages_formatted.append(text)

    # print(last_check)
    # print(last_messages.count())

    user_chat.save()

    responce = {
        'messages': last_messages_formatted,
        'last_check': user_chat.last_check.strftime('%m/%d/%Y,%H:%M:%S.%f')
    }

    return web.json_response(
        responce,
        status=HTTPStatus.OK
    )


@check_user_token
@routes.get('/dialog/{username}/get_id/')
async def get_dialog(request: web.BaseRequest) -> web.json_response:
    token = request.headers.get('token')
    user = User.get(
        token=token
    )
    second_user_username = request.match_info['username']
    server_logger.info(
        f'Try to start dialog with {second_user_username}'
    )
    try:
        second_user = User.get(
            username=second_user_username
        )
    except User.DoesNotExist as e:
        server_logger.info(e)
        return web.json_response(
            {'error': 'Пользователя с таким ником не существует.\n'},
            status=HTTPStatus.BAD_REQUEST
        )
    dialog = Dialog.get_dialog(
        user, second_user
    )

    responce = {
        'id': dialog.id,
    }

    return web.json_response(
        responce,
        status=HTTPStatus.OK
    )


@check_user_token
@routes.post('/dialog/{id}/send/')
async def send_message_to_dialog(
    request: web.BaseRequest
) -> web.json_response:
    data = await request.json()
    text = data['text']

    token = request.headers.get('token')
    user = User.get(
        token=token
    )

    dialog_id = request.match_info['id']
    dialog = Dialog.get(id=dialog_id)

    DialogMessage.create(
        dialog=dialog,
        user=user,
        text=text,
        date=datetime.now()
    )

    return web.json_response(
        status=HTTPStatus.OK
    )


@check_user_token
@routes.get('/dialog/{id}/')
async def get_dialog(request: web.BaseRequest) -> web.json_response:
    token = request.headers.get('token')
    user = User.get(
        token=token
    )
    dialog_id = request.match_info['id']
    dialog = Dialog.get(
        id=dialog_id
    )
    if dialog.recipient == user:
        last_check = dialog.recipient_last_check
    else:
        last_check = dialog.initiator_last_check

    last_messages = DialogMessage.select() \
        .where(DialogMessage.dialog == dialog) \
        .where(DialogMessage.date > last_check) \
        .order_by(DialogMessage.date.desc())

    last_messages_formatted = []

    for message in last_messages:
        date = message.date.strftime('%d/%m, %H:%M:%S')
        text = message.text
        message_user = message.user
        if message_user == user:
            text = f'[{date}] Вы: {text}'
        else:
            text = f'[{date}] {message_user.username}: {text}'

        last_messages_formatted.append(text)

    now = datetime.now()
    if dialog.recipient == user:
        dialog.recipient_last_check = now
    else:
        dialog.initiator_last_check = now

    dialog.save()

    responce = {
        'messages': last_messages_formatted,
    }

    return web.json_response(
        responce,
        status=HTTPStatus.OK
    )
