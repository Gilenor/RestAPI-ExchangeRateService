from typing import Dict, Tuple
from urllib.parse import unquote

from exceptions import CurrencyError, ExchangeRateError, QueryParamsError


def parse_currency_code(path: str) -> str:
    code = path[path.rfind("/") + 1 :]

    if (code == "currency") or (len(code) == 0):
        raise CurrencyError(400, "Currency code is missing in the address")

    return code


def parse_exchange_rate(path: str) -> Tuple[str]:
    code = path[path.rfind("/") + 1 :]

    if (code == "exchangeRate") or (len(code) == 0):
        raise ExchangeRateError(400, "Currencies of pairs are absent in the address")

    return code[:3], code[3:]


# ToDo: в будущем добавить обработку разных форматов и проверку ошибок
#       сейчас функция парсит только валидный формат x-www-form-urlencoded
def parse_request_params(request) -> Dict:
    params = {}
    request_body_len = int(request.headers.get("Content-length", 0))

    if request.rfile.readable and request_body_len > 0:
        request_body = request.rfile.read(request_body_len).decode(encoding="ascii")
        request_body = unquote(request_body, encoding="ascii")
        print("Data:", request_body)

        # возможна ошибка
        params = {
            k: __to_spaces(v, "+")
            for k, v in [pair.split("=") for pair in request_body.split("&")]
        }
    print("params:", params)

    return params


# ToDo: добавить обработку ошибок
def parse_query_params(path: str) -> Dict:
    params = {}

    if "?" not in path:
        raise QueryParamsError(400, "Query parameters missing")

    query = path[path.find("?") + 1 :]

    print("Data:", query)

    # тут возможна ошибка
    params = {k: __to_spaces(v, "%20") for k, v in [pair.split("=") for pair in query.split("&")]}
    print("params:", params)

    return params


def __to_spaces(s: str, old: str) -> str:
    return s.replace(old, " ")
