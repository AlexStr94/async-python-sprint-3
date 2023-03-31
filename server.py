from aiohttp import web

from db_manager import initialize_db
from views import routes


class Server:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.server = web.Application()
        initialize_db()

    def listen(self):
        self.server.add_routes(routes)
        web.run_app(self.server, port=self.port)

# async def hello(request):
#     return web.Response(text="Hello, world")

# app = web.Application()
# app.add_routes(routes)
# web.run_app(app, port=8000)

if __name__ == '__main__':
    Server('127.0.0.1', 8000).listen()

