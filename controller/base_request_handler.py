from http.server import BaseHTTPRequestHandler

from entities import Response
from exceptions import handling_exceptions
from view.view import response_to_error

ALLOWED_HOSTS = "*"
ALLOWED_METHODS = "POST, PATCH"
SERVICE_METHODS = "OPTIONS, GET, POST, PATCH"


class BaseRequestHandler(BaseHTTPRequestHandler):
    _handlers = {}

    # --------------- override methods ----------------------------------------

    def do_GET(self):
        handler = self.get_handler(self.default_handler)

        resp = handling_exceptions(handler, self)
        self.send_response(resp.code, resp.message)

        if not (resp.headers is None):
            print("GET response headers:", resp.headers)
            for name, value in resp.headers:
                self.send_header(name, value)

        self.send_header("Access-Control-Allow-Origin", ALLOWED_HOSTS)
        self.end_headers()

        if not (resp.body is None):
            self.wfile.write(resp.body)

    def do_POST(self):
        handler = self.get_handler(self.default_handler)

        resp = handling_exceptions(handler, self)
        self.send_response(resp.code, resp.message)

        if not (resp.headers is None):
            print("POST respornse headers:", resp.headers)
            for name, value in resp.headers:
                self.send_header(name, value)

            self.send_header("Access-Control-Allow-Origin", ALLOWED_HOSTS)
            self.end_headers()

        if not (resp.body is None):
            self.wfile.write(resp.body)

    def do_PATCH(self):
        handler = self.get_handler(self.default_handler)

        resp = handling_exceptions(handler, self)
        self.send_response(resp.code, resp.message)

        if not (resp.headers is None):
            print("PATCH response headers:", resp.headers)
            for name, value in resp.headers:
                self.send_header(name, value)

            self.send_header("Access-Control-Allow-Origin", ALLOWED_HOSTS)
            self.end_headers()

        if not (resp.body is None):
            self.wfile.write(resp.body)

    def do_OPTIONS(self):
        print("OPTIONS: start")

        self.send_response(204, "OK")

        headers = (
            ("Allow", SERVICE_METHODS),
            ("Access-Control-Allow-Origin", ALLOWED_HOSTS),
            ("Access-Control-Allow-Methods", ALLOWED_METHODS),
            ("Access-Control-Allow-Headers", "Content-type"),
        )

        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()

        print("OPTIONS: end")

    # --------------- static methods ------------------------------------------

    @staticmethod
    def default_handler(path: str):
        return response_to_error(400, "Undefined path")

    # --------------- class methods -------------------------------------------

    @classmethod
    def reg_handler(cls, method: str, path: str):
        def register(func):
            if method not in cls._handlers:
                cls._handlers[method] = {}
            cls._handlers[method][path] = func
            print(f"func: {func.__name__}, path: {path}")

            return func

        return register

    """
    _handlers = { 
        "GET": {
            "/currency": get_currency,
            "/currencies": get_currencies
        },

        "POST": {
            "/currencies": post_currencies
        } 
    }
    """

    # --------------- instance methods ----------------------------------------

    def get_handler(self, default_handler):
        request = self

        print("method:        ", request.command)
        print("path:          ", request.path)
        print("version:       ", request.request_version)
        print("headers:       ", request.headers)
        print("client address:", request.client_address)
        print("request string:", request.requestline)
        print()

        method = request.command.upper()
        path = request.path

        # наивное решение, но пока сойдет
        if path.count("/") > 1:
            path = path[: path.find("/", 1)]
        elif "?" in path:
            path = path[: path.find("?")]

        return request._handlers.get(method, {}).get(path, default_handler)
