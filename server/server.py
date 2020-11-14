from .request import Request
from .endpoint import Endpoint
from .error import HttpException

import re
import time
import asyncio
import inspect


class Server:
    def __init__(self, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.endpoints = {}
        self._not_found = Endpoint(self._not_found)
        self._invalid_method = Endpoint(self._invalid_method)

    def add_endpoint(self, method, url, func):
        endpoint = Endpoint(func)
        method = method.upper()
        url = url.strip("/")
        if url not in self.endpoints:
            self.endpoints[url] = {}
        self.endpoints[url][method] = endpoint

        return endpoint

    async def handle(self, reader, writer):
        request = await reader.readline()
        method, path, protocol = request.decode().split()
        path = path.split("?", 1)
        params = ""

        if len(path) == 2:
            params = path[1]

        params_dict = {}
        for param in params.split("&"):
            if not param:
                continue

            key, value = params.split("=")
            params_dict[key] = value

        path = path[0]
        path = path.strip("/")
        endpoint = self._not_found
        match_groups = ()

        for _endpoint, handles in self.endpoints.items():
            match = re.match(_endpoint, path, re.IGNORECASE)
            if match:
                endpoint = handles.get(method, self._invalid_method)
                match_groups = match.groups()

        headers = {}
        while True:
            header = await reader.readline()
            if header == b'\r\n':
                break
            name, value = header.decode().strip().split(": ", 1)
            headers[name] = value

        body = b""
        if "Content-Length" in headers:
            body = await reader.readexactly(int(headers["Content-Length"]))

        body = body.decode()

        request = self.get_request(body, params_dict, match_groups, headers, reader, writer)

        try:
            await endpoint.invoke(request)
        except HttpException as e:
            request.set_body(repr(e))
            request.status = e.code

        await request.finish()

    def not_found(self, func):
        self._not_found = Endpoint(func)
        return self._not_found

    async def _not_found(self, request):
        request.set_body("404: Not Found")

    def invalid_method(self, func):
        self._invalid_method = Endpoint(func)
        return self._invalid_method

    async def _invalid_method(self, request):
        request.set_body("405: Method Not Allowed")

    async def start(self, host, port):
        await self.init()
        await asyncio.start_server(self.handle, host, port, loop=self.loop)

    def run(self, host="127.0.0.1", port=8080):
        print(f"Running on http://{host}:{port}/")
        try:
            self.loop.create_task(self.start(host, port))
            self.loop.run_forever()
        except Exception as e:
            self.loop.run_until_complete(self.close())
            raise e

    def get(self, url):
        def inner(func):
            return self.add_endpoint("get", url, func)
        return inner

    def post(self, url):
        def inner(func):
            return self.add_endpoint("post", url, func)
        return inner

    async def close(self):
        await self.loop.close()
        
    async def init(self):
        pass

    async def get_request(self, body, params_dict, match_groups, headers, reader, writer):
        return Request(body, params_dict, match_groups, headers, reader, writer)
    