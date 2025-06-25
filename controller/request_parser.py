from typing import Dict, Tuple
from urllib.parse import unquote

from exceptions import NoCurrencyCodeError, NoExchangeRateCodeError, QueryParamsError


# ToDo: добавить валидацию и проверку формата кода
def parse_currency_code(path: str) -> str:
    code = path[path.rfind("/") + 1 :]

    if (len(code) < 3) or (code == "currency"):
        raise NoCurrencyCodeError()

    return code


# ToDo: добавить валидацию и проверку формата кода
def parse_exchange_rate(path: str) -> Tuple[str]:
    code = path[path.rfind("/") + 1 :]

    if (len(code) < 6) or (code == "exchangeRate"):
        raise NoExchangeRateCodeError()

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

        params = {
            k: __spaces(v)
            for k, v in [pair.split("=") for pair in request_body.split("&")]
        }

    return params


# ToDo: добавить обработку ошибок
def parse_query_params(path: str) -> Dict:
    params = {}

    if "?" not in path:
        raise QueryParamsError()

    query = path[path.find("?") + 1 :]

    print("Data:", query)

    params = {k: __spaces(v) for k, v in [pair.split("=") for pair in query.split("&")]}

    return params


# проверка того, что все значения keys содержатся в params
def validate_params(params: Dict, keys: Tuple) -> bool:
    return set(keys) <= set(params.keys())


def __spaces(s: str) -> str:
    return s.replace("+", " ", s.count("+"))
