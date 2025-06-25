import json

from entities import CurrencyDTO, ExchangeDTO, ExchangeRateDTO, Response
from exceptions import CurrencyFieldError, ExchangeFieldError, ExchangeRateFieldError
from model import model
from view import view

from . import request_parser as parser
from . import request_validator as validator
from .base_request_handler import BaseRequestHandler


class ExchangeServiceRequestHandler(BaseRequestHandler):
    pass


# ------------- currencies handlers --------------------------------------------


@ExchangeServiceRequestHandler.reg_handler("GET", "/currencies")
def get_currencies(request):
    currencies = model.get_currencies()

    return view.response_get_currencies(currencies)


@ExchangeServiceRequestHandler.reg_handler("GET", "/currency")
def get_currency(request):
    code = parser.parse_currency_code(request.path)
    currency = model.get_currency(CurrencyDTO(code=code))

    return view.response_get_currency(currency)


@ExchangeServiceRequestHandler.reg_handler("POST", "/currencies")
def post_currencies(request):
    params = parser.parse_request_params(request)

    if not parser.validate_params(params, ("code", "name", "sign")):
        raise CurrencyFieldError()

    currency = model.add_currency(
        CurrencyDTO(code=params["code"], full_name=params["name"], sign=params["sign"])
    )

    return view.response_post_currencies(currency)


# ------------- exchange rates handlers ----------------------------------------


@ExchangeServiceRequestHandler.reg_handler("GET", "/exchange")
def get_exchange(request):
    query_params = parser.parse_query_params(request.path)

    if not parser.validate_params(query_params, ("from", "to", "amount")):
        raise ExchangeFieldError()

    exchange = model.get_exchange(
        ExchangeDTO(
            base=CurrencyDTO(code=query_params["from"]),
            target=CurrencyDTO(code=query_params["to"]),
            amount=query_params["amount"],
        )
    )

    return view.response_get_exchange(exchange)


@ExchangeServiceRequestHandler.reg_handler("GET", "/exchangeRate")
def get_exchange_rate(request):
    currency_codes = parser.parse_exchange_rate(request.path)
    exchange_rate = model.get_exchange_rate(
        ExchangeRateDTO(
            base=CurrencyDTO(code=currency_codes[0]),
            target=CurrencyDTO(code=currency_codes[1]),
        )
    )

    return view.response_get_exchange_rate(exchange_rate)


@ExchangeServiceRequestHandler.reg_handler("GET", "/exchangeRates")
def get_exchange_rates(request):
    exchange_rates = model.get_exchange_rates()

    return view.response_get_exchange_rates(exchange_rates)


@ExchangeServiceRequestHandler.reg_handler("POST", "/exchangeRates")
def post_exchange_rates(request):
    params = parser.parse_request_params(request)

    if not parser.validate_params(
        params, ("baseCurrencyCode", "targetCurrencyCode", "rate")
    ):
        raise ExchangeRateFieldError()

    exchange_rate = model.add_exchange_rate(
        ExchangeRateDTO(
            base=CurrencyDTO(code=params["baseCurrencyCode"]),
            target=CurrencyDTO(code=params["targetCurrencyCode"]),
            rate=params["rate"],
        )
    )

    return view.response_post_exchange_rate(exchange_rate)


@ExchangeServiceRequestHandler.reg_handler("PATCH", "/exchangeRate")
def patch_exchange_rate(request):
    currency_codes = parser.parse_exchange_rate(request.path)
    params = parser.parse_request_params(request)

    if not parser.validate_params(params, ("rate",)):
        raise ExchangeRateFieldError()

    exchange_rate = model.patch_exchange_rate(
        ExchangeRateDTO(
            base=CurrencyDTO(code=currency_codes[0]),
            target=CurrencyDTO(code=currency_codes[1]),
            rate=params["rate"],
        )
    )

    return view.response_patch_exchange_rate(exchange_rate)
