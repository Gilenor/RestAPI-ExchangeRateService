import json
from typing import List

from entities import CurrencyDTO, ExchangeDTO, ExchangeRateDTO, Response

# ---------- currencies -------------------------------------------------------


def response_get_currency(currency: CurrencyDTO) -> Response:
    resp_body = bytes(json.dumps(currency.to_dict()), "utf-8")

    resp_headers = [
        ("Content-type", "application/json"),
        ("Content-length", str(len(resp_body))),
    ]

    return Response(200, "OK", resp_headers, resp_body)


def response_get_currencies(currencies: List[CurrencyDTO]) -> Response:
    body = [currency.to_dict() for currency in currencies]
    resp_body = bytes(json.dumps(body), "utf-8")

    resp_headers = [
        ("Content-type", "application/json"),
        ("Content-length", str(len(resp_body))),
    ]

    return Response(200, "OK", resp_headers, resp_body)


def response_post_currencies(currency: CurrencyDTO) -> Response:
    resp_body = bytes(json.dumps(currency.to_dict()), "utf-8")

    resp_headers = [
        ("Content-type", "application/json"),
        ("Content-length", len(resp_body)),
    ]

    return Response(201, "Currency was created", resp_headers, resp_body)


# ---------- exchange rates ---------------------------------------------------


def response_get_exchange(exchange: ExchangeDTO) -> Response:
    resp_body = bytes(json.dumps(exchange.to_dict()), "utf-8")

    resp_headers = [
        ("Content-type", "application/json"),
        ("Content-length", str(len(resp_body))),
    ]

    return Response(200, "OK", resp_headers, resp_body)


def response_get_exchange_rate(exchange_rate: ExchangeRateDTO) -> Response:
    resp_body = bytes(json.dumps(exchange_rate.to_dict()), "utf-8")

    resp_headers = [
        ("Content-type", "application/json"),
        ("Content-length", str(len(resp_body))),
    ]

    return Response(200, "OK", resp_headers, resp_body)


def response_get_exchange_rates(exchange_rates: List[ExchangeRateDTO]) -> Response:
    body = [exchange_rate.to_dict() for exchange_rate in exchange_rates]
    resp_body = bytes(json.dumps(body), "utf-8")

    resp_headers = [
        ("Content-type", "application/json"),
        ("Content-length", str(len(resp_body))),
    ]

    return Response(200, "OK", resp_headers, resp_body)


def response_post_exchange_rate(exchange_rate: ExchangeRateDTO) -> Response:
    resp_body = bytes(json.dumps(exchange_rate.to_dict()), "utf-8")

    resp_headers = [
        ("Content-type", "application/json"),
        ("Content-length", str(len(resp_body))),
    ]

    return Response(201, "Exchange rate was created", resp_headers, resp_body)


def response_patch_exchange_rate(exchange_rate: ExchangeRateDTO) -> Response:
    resp_body = bytes(json.dumps(exchange_rate.to_dict()), "utf-8")

    resp_headers = [
        ("Content-type", "application/json"),
        ("Content-length", str(len(resp_body))),
    ]

    return Response(200, "Exchange rate was patched", resp_headers, resp_body)


# ---------- errors -----------------------------------------------------------


def response_to_error(error_code: int, error_message: str) -> Response:
    body = {"message": error_message}
    resp_body = bytes(json.dumps(body), "utf-8")

    resp_headers = [
        ("Content-type", "application/json"),
        ("Content-length", str(len(resp_body))),
    ]

    return Response(error_code, error_message, resp_headers, resp_body)
