import os

from controller import Controller

HOST_NAME = os.environ.get("HOST_NAME", "localhost")
SERVER_PORT = os.environ.get("SERVER_PORT", "8080")


if __name__ == "__main__":
    exchange_service = Controller(HOST_NAME, int(SERVER_PORT))

    try:
        print(f"Server started http://{str(exchange_service)}")
        exchange_service.run()
    except KeyboardInterrupt:
        print("Server stopped by keyboard interruption")
        exchange_service.stop()
