from aiohttp import web

from db_manager import initialize_db
from logger import server_logger
from settings import HOST, PORT
from views import routes


class Server:
    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        self.host = host
        self.port = port
        self.server = web.Application()
        initialize_db()

    def listen(self) -> None:
        self.server.add_routes(routes)
        web.run_app(self.server, port=self.port)


if __name__ == '__main__':
    server_logger.info('Server`s started')
    Server().listen()
