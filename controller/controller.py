from http.server import HTTPServer

from .exchange_service_request_handler import ExchangeServiceRequestHandler


class Controller:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = HTTPServer((host, port), ExchangeServiceRequestHandler)

    def __str__(self):
        return "{}:{}".format(self.host, self.port)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.server_close()
