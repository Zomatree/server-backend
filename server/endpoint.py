class Endpoint:
    def __init__(self, callback, url):
        self._callback = callback
        self.url = url
   
    async def _middleware(self, request):
        return request

    @property
    def callback(self):
        return self._callback
    
    def middleware(self, func):
        self._middleware = func
        return func

    async def invoke(self, request):
        request = await self._middleware(request)
        return await self.callback(request)
