import asyncio
import json
from .utils import status_codes


class Request:
    def __init__(self, body, params, groups, headers, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.body = body
        self.url_params = params
        self.groups = groups
        self.headers = headers
        self._reader = reader
        self._writer = writer
        self.return_body = ""
        self.return_headers = {}
        self.status = 200
        self.finished = False
        
    async def finish(self):
        if self.finished:
            return

        self.finished = True
        
        self._writer.write(f"HTTP/1.1 {self.status} {status_codes[self.status]}\r\n".encode())
        for key, value in self.return_headers.items():
            self._writer.write(f"{key}: {value}\r\n".encode())

        self._writer.write(b"\r\n")
        self._writer.write(self.return_body.encode())

        self._writer.close()

    def set_header(self, key, value):
        self.return_headers[key] = value
        return self

    def set_content_type(self, type):
        self.return_body["Content-Type"] = type

    def set_body(self, body):
        if isinstance(body, dict):
            body = json.dumps(body)
            if "Content-Type" not in self.return_body:
                self.return_headers["Content-Type"] = "application/json"
        self.return_body = body
