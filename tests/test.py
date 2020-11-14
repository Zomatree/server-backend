import server as http
import asyncio


class Request(http.Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aa = None
        self.db = None


class Server(http.Server):
    async def init(self):
        self.db = None

    def get_request(self, *args):
        request = Request(*args)
        request.db = self.db


server = Server()


@server.get(r"/a/(.+)")
async def a(request):
    request.set_body({"b": 1})
    request.status = 200

@a.middleware
async def a_middleware(request):
    raise http.HttpException("aaaaaaaaaa", code=402)

@server.post(r"/b")
async def b(request):
    request.set_body({"/b": request.body})
    request.status = 200

@b.middleware
async def b_middleware(request):
    request.aa = 1
    return request

print(server.endpoints)
server.run()