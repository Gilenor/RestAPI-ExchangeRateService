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

    exchange_rate = __get_exchange_rate_for_pair(CurrencyDTO(*base), CurrencyDTO(*target))

    return ExchangeDTO(
        base=exchange_rate.base_currency,
        target=exchange_rate.target_currency,
        rate=round(exchange_rate.rate, 6),
        amount=exchange.amount,
    )


def get_exchange_rate(exchange_rate: ExchangeRateDTO) -> ExchangeRateDTO:
    base = db.get_currency_by_code(exchange_rate.base_currency.code)
    target = db.get_currency_by_code(exchange_rate.target_currency.code)

    exchange_rate_record = db.get_exchange_rate(base, target)

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

    record = db.get_exchange_rate(base, target)
    patch = db.patch_exchange_rate(record[0], exchange_rate.rate)

    return ExchangeRateDTO(
        _id=patch[0],
        base=CurrencyDTO(*base),
        target=CurrencyDTO(*target),
        rate=patch[3],
    )


# ---------- private functions ------------------------------------------------


def __get_exchange_rate_for_pair(
    from_currency: CurrencyDTO, to_currency: CurrencyDTO
) -> ExchangeRateDTO:

    rate = Decimal(1)
    codes = __exchanges.get_path(from_currency.code, to_currency.code)
    currencies = [db.get_currency_by_code(code) for code in codes]

    if not codes:
        raise ExchangeRateError(404, f"Exchange rate not exist: {from_currency.code}, {to_currency.code}")

    for i in range(1, len(currencies)):
        base_currency = currencies[i - 1]
        target_currency = currencies[i]
        rate = rate * __get_rate_for_pair(base_currency, target_currency)

    return ExchangeRateDTO(
        base=from_currency,
        target=to_currency,
        rate=rate,
    )


def __get_rate_for_pair(from_currency: Tuple, to_currency: Tuple) -> Decimal:
    exchange_rates = [
        db.get_exchange_rate(from_currency, to_currency, quiet=True),  # прямой курс
        db.get_exchange_rate(to_currency, from_currency, quiet=True),  # обратный курс
    ]

    if not any(exchange_rates):
        raise ExchangeRateError(404, f"Exchange rate not exist: {from_currency[1]}, {to_currency[1]}")

    if exchange_rates[0]:
        return exchange_rates[0][3]
    
    return Decimal(1) / exchange_rates[1][3]


# заполняем граф данными из таблицы, нужно будет переделать чтобы структура сохранялась
# либо в файле, либо в базе данных, сейчас она каждый раз создается заново
def __fill_graph():
    for exchange_rate in db.get_exchange_rates():
        base_currency = exchange_rate[1:5]
        target_currency = exchange_rate[5:9]

        __exchanges.add_pair(base_currency[1], target_currency[1])


__fill_graph()
