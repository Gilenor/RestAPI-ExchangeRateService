import re

from functools import wraps
from typing import Dict, Tuple

from exceptions import (
    CurrencyError,
    ExchangeError,
    ExchangeRateError,
    FieldError,
    FormatError,
)
from exceptions.valid_types import match_types as mt


# проверка того, что все значения keys содержатся в params
# и что они соответствуют определенным типам в строковой записи
def validate_params(params: Dict, keys: Tuple, types: Tuple):
    # возможны ошибки, если агрументы будут типа None
    missing_params = [key for key in keys if key not in params]

    if len(missing_params) > 0:
        raise FieldError(message=f"missing fields - {missing_params}")

    # выборка невалидных параметров
    invalid_params = [k for k, t in zip(keys, types) if not re.fullmatch(t, params[k])]

    if len(invalid_params) > 0:
        raise FormatError(message=f"incorrect format for params - {invalid_params}")


def validate_decorator(error_type: Exception, code: int, message: str):
    def func_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except (FieldError, FormatError) as e:
                raise error_type(code=code, message=f"{message}{e.message}")

        return wrapper

    return func_decorator


# ---------- currency ---------------------------------------------------------


@validate_decorator(CurrencyError, 400, "Error currency: ")
def validate_get_currency(code: str):
    validate_params({"code": code}, mt.Currency.Get.names, mt.Currency.Get.types)


@validate_decorator(CurrencyError, 400, "Error currency: ")
def validate_post_currencies(params: Dict):
    validate_params(params, mt.Currency.Post.names, mt.Currency.Post.types)


# ---------- exchange ---------------------------------------------------------


@validate_decorator(ExchangeError, 400, "Error exchange: ")
def validate_get_exchange(query_params: Dict):
    validate_params(query_params, mt.Exchange.Get.names, mt.Exchange.Get.types)


# ---------- exchange rate ----------------------------------------------------


@validate_decorator(ExchangeRateError, 400, "Error exchange rate: ")
def validate_get_exchange_rate(codes: Tuple[str]):
    params = dict(zip(("fromCurrency", "toCurrency"), codes))
    validate_params(params, mt.ExchangeRate.Get.names, mt.ExchangeRate.Get.types)


@validate_decorator(ExchangeRateError, 400, "Error exchange rate: ")
def validate_post_exchange_rate(params: Dict):
    validate_params(params, mt.ExchangeRate.Post.names, mt.ExchangeRate.Post.types)


@validate_decorator(ExchangeRateError, 400, "Error exchange rate: ")
def validate_patch_exchange_rate(params: Dict, codes: Tuple[str]):
    params = {"fromCurrency": codes[0], "toCurrency": codes[1], **params}
    validate_params(params, mt.ExchangeRate.Patch.names, mt.ExchangeRate.Patch.types)
