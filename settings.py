import os


MESSAGE_LIMIT = 20
HOST = os.getenv('SERVER_HOST', default='127.0.0.1')
PORT = os.getenv('SERVER_PORT', default=8000)
