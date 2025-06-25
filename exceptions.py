# from functools import wraps
import sqlite3

from entities import Response
from view.view import response_to_error

# import sys
# import traceback

"""
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


ERRORS = {
    sqlite3.DataError: "DataError",
    sqlite3.DatabaseError: "DataBaseError",
    sqlite3.InternalError: "InternalError",
    sqlite3.IntegrityError: "IntegrityError",
    sqlite3.InterfaceError: "InterfaceError",
    sqlite3.OperationalError: "OperationalError",
    sqlite3.ProgrammingError: "ProgrammingError",
    sqlite3.NotSupportedError: "NotSupportedError",
}


def get_error_type(error_type: type) -> str:
    return ERRORS.get(error_type, "Undefinded Error!")


get_currencies_exceptions = {
    sqlite3.OperationalError: Response(500, "Database unavailable")
}


get_currency_exceptions = {
    NoCurrencyCodeError: Response(400, "Currency code is missing in the address"),
    CurrencyNotFoundError: Response(404, "Currency not found"),
    sqlite3.OperationalError: Response(500, "Database unavailable"),
}


post_currency_exceptions = {
    KeyError: Response(400, "Not all fields were transferred"),
    sqlite3.ProgrammingError: Response(400, "Not all fields were transferred"),
    sqlite3.IntegrityError: Response(409, "Currency with this code already exists."),
    sqlite3.OperationalError: Response(500, "Database unavailable"),
}


exception_response = {
    NoCurrencyCodeError: Response(400, "Currency code is missing in the address"),
    ProgrammingError: Response(400, "Not all fields were transferred"),
    CurrencyNotFoundError: Response(404, "Currency not found"),
    IntegrityError: Response(409, "Currency with this code already exists."),
    OperationalError: Response(500, "Database unavailable"),
}


def get_programming_error_response(err: sqlite3.Error):
    print(f"Programming Error: {err}")
    return response_to_error(400, "Not all fields were transferred")


def get_integrity_error_response(err: sqlite3.Error):
    print(f"Integrity Error: {err}")

    if "exchange_rates" in str(err):
        return response_to_error(409, "Exchange rate with this codes already exists.")

    if "currencies" in str(err):
        return response_to_error(409, "Currency with this code already exists.")
    # exc_type, exc_value, exc_tb = sys.exc_info()
    # print(f"type: {exc_type}\nvalue: {exc_value}\ntb: {exc_tb}\n")
    # print(traceback.format_exception(exc_type, exc_value, exc_tb))


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


"""
def handling_exceptions(func, *args, **kwargs):
	try:
		return func(*args, *kwargs)
	except Exception as e:
		if exception_response.get(type(e), False):
			return exception_response.get(type(e))
		else:
			return UNIDENTIFIED_ERROR_RESPONSE



def exception_handling(except_data):
	def func_decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except Exception as e:
				print(type(e), ":", e)
				if type(e) in except_data:
					return except_data[type(e)]
				else:
					return Response(111, "Unavailable exception")
		return wrapper
	return func_decorator
"""
