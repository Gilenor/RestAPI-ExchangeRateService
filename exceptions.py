import sqlite3

from entities import Response
from view.view import response_to_error


"""
sqlite errors

Error
Warning
InterfaceError
DatabaseError
InternalError
OperationalError
ProgrammingError
IntegrityError
DataError
NotSupportedError
"""


class QueryParamsError(Exception):
    pass


class CurrencyFieldError(KeyError):
    pass


class NoCurrencyCodeError(Exception):
    pass


class CurrencyNotFoundError(Exception):
    pass


class CurrencyInvalidDataError(Exception):
    pass


class ExchangeFieldError(KeyError):
    pass


class ExchangeRateFieldError(KeyError):
    pass


class NoExchangeRateCodeError(Exception):
    pass


class ExchangeRateNotFoundError(Exception):
    pass


class IntegrityError(sqlite3.IntegrityError):
    pass


class OperationalError(sqlite3.OperationalError):
    pass


class ProgrammingError(sqlite3.ProgrammingError):
    pass




def get_programming_error_response(err: sqlite3.Error):
    print(f"Programming Error: {err}")
    return response_to_error(400, "Not all fields were transferred")


def get_integrity_error_response(err: sqlite3.Error):
    print(f"Integrity Error: {err}")

    if "exchange_rates" in str(err):
        return response_to_error(409, "Exchange rate with this codes already exists.")

    if "currencies" in str(err):
        return response_to_error(409, "Currency with this code already exists.")


def get_operational_error_response(err: sqlite3.Error):
    print(f"Operational Error: {err}")
    return response_to_error(500, "Database unavailable")


def handling_exceptions(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except QueryParamsError:
        return response_to_error(400, "Query parameters missing, or bad format")

    except CurrencyFieldError:
        return response_to_error(400, "Not all fields were transferred for currency")
    except ExchangeFieldError:
        return response_to_error(
            400, "Not all query-fields were transferred for exchange"
        )
    except ExchangeRateFieldError:
        return response_to_error(
            400, "Not all fields were transferred for exchange_rate"
        )

    except NoCurrencyCodeError:
        return response_to_error(400, "Currency code is missing in the address")
    except NoExchangeRateCodeError:
        return response_to_error(
            400, "Current currencies of pairs are absent in the address"
        )

    except CurrencyNotFoundError:
        return response_to_error(404, "Currency not found")
    except ExchangeRateNotFoundError:
        return response_to_error(404, "The exchange rate for the couple was not found")

    except CurrencyInvalidDataError:
        return response_to_error(400, "Currency ivalid data")

    except sqlite3.IntegrityError as err:
        return get_integrity_error_response(err)
    except sqlite3.OperationalError as err:
        return get_operational_error_response(err)
    except sqlite3.ProgrammingError as err:
        return get_programming_error_response(err)
