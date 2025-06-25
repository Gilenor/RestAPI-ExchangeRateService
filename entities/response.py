class Response:
    def __init__(self, code, message="", headers=None, body=None):
        self.code = code
        self.message = message
        self.headers = headers or [("Content-length", 0)]
        self.body = body
