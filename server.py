from aiohttp import web

from db_manager import initialize_db
from logger import server_logger
from views import routes


class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.host = host
        self.port = port
        self.server = web.Application()
        initialize_db()

    def listen(self) -> None:
        self.server.add_routes(routes)
        web.run_app(self.server, port=self.port)


if __name__ == '__main__':
    server_logger.info('Server`s started')
    Server('127.0.0.1', 8000).listen()
