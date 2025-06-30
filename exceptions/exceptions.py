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


class BaseResponseError(Exception):
    def __init__(self, code: int = 400, message: str = ""):
        super().__init__(message)

        self.code = code
        self.message = message


class FieldError(BaseResponseError):
    pass


class FormatError(BaseResponseError):
    pass


class QueryParamsError(BaseResponseError):
    pass


class CurrencyError(BaseResponseError):
    pass


class ExchangeError(BaseResponseError):
    pass


class ExchangeRateError(BaseResponseError):
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
    except BaseResponseError as e:
        return response_to_error(e.code, e.message)

    except sqlite3.IntegrityError as err:
        return get_integrity_error_response(err)
    except sqlite3.OperationalError as err:
        return get_operational_error_response(err)
    except sqlite3.ProgrammingError as err:
        return get_programming_error_response(err)
