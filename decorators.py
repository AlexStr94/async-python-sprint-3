from functools import wraps
from http import HTTPStatus

from aiohttp import web

from exceptions import NoUserTokenInRequest
from models import User


def check_user_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        token = request.headers.get('token')
        try:
            if not token:
                raise NoUserTokenInRequest

            User.get(
                token=token
            )
        except (User.DoesNotExist, NoUserTokenInRequest):
            return web.json_response(
                {'error': 'Invalid Token'},
                status=HTTPStatus.BAD_REQUEST
            )

        return func(*args, **kwargs)

    return wrapper
