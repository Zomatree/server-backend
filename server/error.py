class HttpException(Exception):
    def __init__(self, message, *, code=400):
        super().__init__(message)
        self.code = code
    
    def __repr__(self):
        return f"{self.code}: {str(self)}"