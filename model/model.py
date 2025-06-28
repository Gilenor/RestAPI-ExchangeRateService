import sqlite3

from decimal import Decimal
from typing import List, Tuple

from entities import CurrencyDTO, ExchangeDTO, ExchangeRateDTO
from exceptions import CurrencyError, ExchangeRateError

from . import data_base as db
from .graph import Graph

__exchanges = Graph()


# ---------- currencies -------------------------------------------------------


def get_currency(currency: CurrencyDTO) -> CurrencyDTO:
    record = db.get_currency_by_code(currency.code)
    __check_currencies_exist((record, currency))

    return CurrencyDTO(*record)


def get_currencies() -> List[CurrencyDTO]:
    currencies = [CurrencyDTO(*currency) for currency in db.get_currencies()]

    return currencies


def add_currency(currency: CurrencyDTO) -> CurrencyDTO:
    new_currency = db.add_currency(currency.code, currency.full_name, currency.sign)

    return CurrencyDTO(*new_currency)


# ---------- exchange rates ---------------------------------------------------


def get_exchange(exchange: ExchangeDTO) -> ExchangeDTO:
    base = db.get_currency_by_code(exchange.base_currency.code)
    target = db.get_currency_by_code(exchange.target_currency.code)
    __check_currencies_exist(
        (base, exchange.base_currency), (target, exchange.target_currency)
    )

    exchange_rate = __get_exchange_rate_for_pair(
        CurrencyDTO(*base), CurrencyDTO(*target)
    )
    __check_exchange_rate_exist((exchange_rate, exchange))

    return ExchangeDTO(
        base=exchange_rate.base_currency,
        target=exchange_rate.target_currency,
        rate=round(exchange_rate.rate, 6),
        amount=exchange.amount,
    )


def get_exchange_rate(exchange_rate: ExchangeRateDTO) -> ExchangeRateDTO:
    base = db.get_currency_by_code(exchange_rate.base_currency.code)
    target = db.get_currency_by_code(exchange_rate.target_currency.code)
    __check_currencies_exist(
        (base, exchange_rate.base_currency), (target, exchange_rate.target_currency)
    )

    exchange_rate_record = db.get_exchange_rate(base[0], target[0])
    __check_exchange_rate_exist((exchange_rate_record, exchange_rate))

    return ExchangeRateDTO(
        _id=exchange_rate_record[0],
        base=CurrencyDTO(*base),
        target=CurrencyDTO(*target),
        rate=exchange_rate_record[3],
    )


def get_exchange_rates() -> List[ExchangeRateDTO]:
    exchange_rates = []

    for e in db.get_exchange_rates():
        # возможно распаковка кортежа не лучший способ инициализации
        # потому-что может измениться порядок и форма данных в базе
        base_currency = CurrencyDTO(*e[1:5])
        target_currency = CurrencyDTO(*e[5:9])
        exchange = ExchangeRateDTO(e[0], base_currency, target_currency, e[9])
        exchange_rates.append(exchange)

    return exchange_rates


def add_exchange_rate(exchange_rate: ExchangeRateDTO) -> ExchangeRateDTO:
    base = db.get_currency_by_code(exchange_rate.base_currency.code)
    target = db.get_currency_by_code(exchange_rate.target_currency.code)
    __check_currencies_exist(
        (base, exchange_rate.base_currency), (target, exchange_rate.target_currency)
    )

    new_exchange_rate = db.add_exchange_rate(base[0], target[0], exchange_rate.rate)

    # добавляем новую связь для валютной пары в граф
    __exchanges.add_pair(base[1], target[1])

    return ExchangeRateDTO(
        _id=new_exchange_rate[0],
        base=CurrencyDTO(*base),
        target=CurrencyDTO(*target),
        rate=new_exchange_rate[3],
    )


def patch_exchange_rate(exchange_rate: ExchangeRateDTO) -> ExchangeRateDTO:
    base = db.get_currency_by_code(exchange_rate.base_currency.code)
    target = db.get_currency_by_code(exchange_rate.target_currency.code)
    __check_currencies_exist(
        (base, exchange_rate.base_currency), (target, exchange_rate.target_currency)
    )

    exchange_rate_record = db.get_exchange_rate(base[0], target[0])
    __check_exchange_rate_exist((exchange_rate_record, exchange_rate))

    exchange_rate_patch = db.patch_exchange_rate(
        exchange_rate_record[0], exchange_rate.rate
    )

    return ExchangeRateDTO(
        _id=exchange_rate_patch[0],
        base=CurrencyDTO(*base),
        target=CurrencyDTO(*target),
        rate=exchange_rate_patch[3],
    )


# ---------- private functions ------------------------------------------------


def __get_exchange_rate_for_pair(
    from_currency: CurrencyDTO, to_currency: CurrencyDTO
) -> ExchangeRateDTO:

    rate = Decimal(1)
    codes = __exchanges.get_path(from_currency.code, to_currency.code)
    currencies = [db.get_currency_by_code(code) for code in codes]

    if not codes or not all(currencies):
        return None

    for i in range(1, len(currencies)):
        base_currency = currencies[i - 1]
        target_currency = currencies[i]
        pair_rate = __get_rate_for_pair(base_currency[0], target_currency[0])

        if pair_rate is None:
            return None

        rate = rate * pair_rate

    return ExchangeRateDTO(
        # _id=exchange_rate[0],
        base=from_currency,
        target=to_currency,
        rate=rate,
    )


def __get_rate_for_pair(from_currency_id: int, to_currency_id: int) -> Decimal:
    # ToDo: возможно лучше сразу возвращать из базы, вместо двух запросов
    exchange_rates = [
        db.get_exchange_rate(from_currency_id, to_currency_id),  # прямой курс
        db.get_exchange_rate(to_currency_id, from_currency_id),  # обратный курс
    ]

    if not any(exchange_rates):
        return None

    # хочется сделать это как-то красиво, но не знаю как(((
    if exchange_rates[0]:
        exchange_rate = exchange_rates[0]
        rate = exchange_rate[3]
    else:
        exchange_rate = exchange_rates[1]
        rate = Decimal(1) / exchange_rate[3]

    return rate


def __check_currencies_exist(*currencies):
    """в случае если какая-то из валют является None бросается исключение CurrencyError с кодом этой валюты"""
    not_existing = [currency.code for record, currency in currencies if not record]

    if len(not_existing) > 0:
        raise CurrencyError(404, f"Error currency not found: {not_existing}")


def __check_exchange_rate_exist(*exchange_rates):
    """в случае если какой-то из курсов является None бросается исключение ExchangeRateError с кодом этого курса"""
    not_existing = [
        (exch.base_currency.code, exch.target_currency.code)
        for record, exch in exchange_rates
        if not record
    ]

    if len(not_existing) > 0:
        raise ExchangeRateError(404, f"Error exchange rate not exist: {not_existing}")


# заполняем граф данными из таблицы, нужно будет переделать чтобы структура сохранялась
# либо в файле, либо в базе данных, сейчас она каждый раз создается заново
def __fill_graph():
    for exchange_rate in db.get_exchange_rates():
        base_currency = exchange_rate[1:5]
        target_currency = exchange_rate[5:9]

        __exchanges.add_pair(base_currency[1], target_currency[1])


__fill_graph()
