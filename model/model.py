import sqlite3

from decimal import Decimal
from typing import List, Tuple

from entities import CurrencyDTO, ExchangeDTO, ExchangeRateDTO
from exceptions import (
    CurrencyNotFoundError,
    CurrencyInvalidDataError,
    ExchangeRateNotFoundError,
)

from . import data_base as base
from .graph import Graph



__exchanges = Graph()


# ---------- currencies -------------------------------------------------------


def get_currency(currency: CurrencyDTO) -> CurrencyDTO:
    currency_record = base.get_currency_by_code(currency.code)

    if currency_record is None:
        raise CurrencyNotFoundError()

    return CurrencyDTO(*currency_record)


def get_currencies() -> List[CurrencyDTO]:
    currencies = [CurrencyDTO(*currency) for currency in base.get_currencies()]

    return currencies


def add_currency(currency: CurrencyDTO) -> CurrencyDTO:
    if len(currency.code) != 3:
        raise CurrencyInvalidDataError()

    new_currency = base.add_currency(currency.code, currency.full_name, currency.sign)

    return CurrencyDTO(*new_currency)


# ---------- exchange rates ---------------------------------------------------


def get_exchange(exchange: ExchangeDTO) -> ExchangeDTO:
    base_currency = base.get_currency_by_code(exchange.base_currency.code)
    target_currency = base.get_currency_by_code(exchange.target_currency.code)

    if (base_currency is None) or (target_currency is None):
        raise CurrencyNotFoundError()

    print(
        __exchanges.get_path(exchange.base_currency.code, exchange.target_currency.code)
    )
    # __exchanges.print_graph()
    # print(__exchanges)

    exchange_rate = __get_exchange_rate_for_pair(
        CurrencyDTO(*base_currency), CurrencyDTO(*target_currency)
    )

    if exchange_rate is None:
        raise ExchangeRateNotFoundError()

    return ExchangeDTO(
        base=exchange_rate.base_currency,
        target=exchange_rate.target_currency,
        rate=round(exchange_rate.rate, 6),
        amount=exchange.amount,
    )


def get_exchange_rate(exchange_rate: ExchangeRateDTO) -> ExchangeRateDTO:
    base_currency = base.get_currency_by_code(exchange_rate.base_currency.code)
    target_currency = base.get_currency_by_code(exchange_rate.target_currency.code)

    if (base_currency is None) or (target_currency is None):
        raise CurrencyNotFoundError()

    exchange_rate = base.get_exchange_rate(base_currency[0], target_currency[0])

    if exchange_rate is None:
        raise ExchangeRateNotFoundError()

    return ExchangeRateDTO(
        _id=exchange_rate[0],
        base=CurrencyDTO(*base_currency),
        target=CurrencyDTO(*target_currency),
        rate=exchange_rate[3],
    )


def get_exchange_rates() -> List[ExchangeRateDTO]:
    exchange_rates = []

    for e in base.get_exchange_rates():
        # возможно распаковка кортежа не лучший способ инициализации
        # потому-что может измениться порядок и форма данных в базе
        base_currency = CurrencyDTO(*e[1:5])
        target_currency = CurrencyDTO(*e[5:9])
        exchange = ExchangeRateDTO(e[0], base_currency, target_currency, e[9])
        exchange_rates.append(exchange)

    return exchange_rates


def add_exchange_rate(exchange_rate: ExchangeRateDTO) -> ExchangeRateDTO:
    base_currency = base.get_currency_by_code(exchange_rate.base_currency.code)
    target_currency = base.get_currency_by_code(exchange_rate.target_currency.code)

    if (base_currency is None) or (target_currency is None):
        raise CurrencyNotFoundError()

    new_exchange_rate = base.add_exchange_rate(
        base_currency[0], target_currency[0], exchange_rate.rate
    )

    # добавляем новую связь для валютной пары в граф
    __exchanges.add_pair(base_currency[1], target_currency[1])

    return ExchangeRateDTO(
        _id=new_exchange_rate[0],
        base=CurrencyDTO(*base_currency),
        target=CurrencyDTO(*target_currency),
        rate=new_exchange_rate[3],
    )


def patch_exchange_rate(exchange_rate: ExchangeRateDTO) -> ExchangeRateDTO:
    base_currency = base.get_currency_by_code(exchange_rate.base_currency.code)
    target_currency = base.get_currency_by_code(exchange_rate.target_currency.code)

    if (base_currency is None) or (target_currency is None):
        raise CurrencyNotFoundError()

    exchange_rate_record = base.get_exchange_rate(base_currency[0], target_currency[0])

    if exchange_rate_record is None:
        raise ExchangeRateNotFoundError()

    exchange_rate_patch = base.patch_exchange_rate(
        exchange_rate_record[0], exchange_rate.rate
    )

    return ExchangeRateDTO(
        _id=exchange_rate_patch[0],
        base=CurrencyDTO(*base_currency),
        target=CurrencyDTO(*target_currency),
        rate=exchange_rate_patch[3],
    )


# ---------- private functions ------------------------------------------------


def __get_exchange_rate_for_pair(
    from_currency: CurrencyDTO, to_currency: CurrencyDTO
) -> ExchangeRateDTO:

    rate = Decimal(1)
    codes = __exchanges.get_path(from_currency.code, to_currency.code)
    currencies = [base.get_currency_by_code(code) for code in codes]

    if not all(currencies):
        return None

    for i in range(1, len(currencies)):
        base_currency = currencies[i - 1]
        target_currency = currencies[i]
        pair_rate = __get_rate_for_pair(base_currency[0], target_currency[0])

        if pair_rate is None:
            return None

        rate = rate * pair_rate
        print(type(rate), rate)

    return ExchangeRateDTO(
        # _id=exchange_rate[0],
        base=from_currency,
        target=to_currency,
        rate=rate,
    )


def __get_rate_for_pair(from_currency_id: int, to_currency_id: int) -> Decimal:
    # ToDo: возможно лучше сразу возвращать из базы, вместо двух запросов
    exchange_rates = [
        base.get_exchange_rate(from_currency_id, to_currency_id),  # прямой курс
        base.get_exchange_rate(to_currency_id, from_currency_id),  # обратный курс
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

    # print(type(exchange_rate[3]), rate)

    return rate


# заполняем граф данными из таблицы, нужно будет переделать чтобы структура сохранялась
# либо в файле, либо в базе данных, сейчас она каждый раз создается заново
def __fill_graph():
    for exchange_rate in base.get_exchange_rates():
        base_currency = exchange_rate[1:5]
        target_currency = exchange_rate[5:9]

        __exchanges.add_pair(base_currency[1], target_currency[1])
    print(__exchanges)


__fill_graph()
