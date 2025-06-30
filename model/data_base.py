import sqlite3

from typing import Tuple
from decimal import Decimal
from exceptions import CurrencyError, ExchangeRateError


DB_FILE = "data/currency_exchange.sqlite3"

CURRENCY_QUERY = "SELECT * FROM currencies WHERE {} = ?;"
EXCHANGE_QUERY = "SELECT * FROM exchange_rates WHERE {} = ?;"

CURRENCY_ROWID_QUERY = CURRENCY_QUERY.format("rowid")
CURRENCY_BY_ID_QUERY = CURRENCY_QUERY.format("ID")
CURRENCY_BY_CODE_QUERY = CURRENCY_QUERY.format("Code")

EXCHANGE_ROWID_QUERY = EXCHANGE_QUERY.format("rowid")


#get_currency_by_id = lambda c_id: get_currency(CURRENCY_BY_ID_QUERY, c_id)
#get_currency_by_code = lambda c_code: get_currency(CURRENCY_BY_CODE_QUERY, c_code)


def adapt_decimal(d):
    # print("set decimal")
    return str(d)


def convert_decimal(s):
    # print("get decimal")
    return Decimal(s.decode("utf-8"))


# Register the adapter
sqlite3.register_adapter(Decimal, adapt_decimal)

# Register the converter
sqlite3.register_converter("decimal", convert_decimal)



# ---------- create tables ----------------------------------------------------


def create_currensies():
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()

        cur.execute(
            """
    			CREATE TABLE IF NOT EXISTS currencies (
    			ID    		INTEGER PRIMARY KEY AUTOINCREMENT,
    			Code  		VARCHAR NOT NULL, 
    			FullName   	VARCHAR NOT NULL ON CONFLICT REPLACE DEFAULT "", 
    			Sign   		VARCHAR NOT NULL ON CONFLICT REPLACE DEFAULT ""
    		)
    		"""
        )

        cur.execute(
            """
    			CREATE UNIQUE INDEX IF NOT EXISTS code_index
    			ON currencies (Code);
    		"""
        )

        con.commit()
        cur.close()


def create_exchange_rates():
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()

        cur.execute(
            """
    			CREATE TABLE IF NOT EXISTS exchange_rates (
    				ID 					INTEGER PRIMARY KEY AUTOINCREMENT,
    				BaseCurrencyId 		INTEGER NOT NULL,
    				TargetCurrencyId 	INTEGER NOT NULL,
    				Rate 				DECIMAL(6) NOT NULL,
    				FOREIGN KEY			(BaseCurrencyId) REFERENCES currencies(ID),
    				FOREIGN KEY			(TargetCurrencyId) REFERENCES currencies(ID)
    			)
    		"""
        )

        cur.execute(
            """
    			CREATE UNIQUE INDEX IF NOT EXISTS currency_pair
    			ON exchange_rates (BaseCurrencyId, TargetCurrencyId);
    		"""
        )

        con.commit()
        cur.close()


def get_record_by_rowid(sql_query: str, rowid: int):
    record = None

    with sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES) as con:
        cur = con.cursor()
        cur.execute(sql_query, (rowid,))

        record = cur.fetchone()
        cur.close()

    return record


# ---------- currencies -------------------------------------------------------


def get_currencies():
    currencies = []

    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()

        cur.execute(
            """
				SELECT *
				FROM   currencies;
			"""
        )

        currencies = cur.fetchall()
        cur.close()

    return currencies


def get_currency(sql_query: str, *args):
    currency = None

    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()

        cur.execute(sql_query, args)

        currency = cur.fetchone()
        cur.close()

    return currency


def get_currency_by_id(currency_id: int, quiet: bool=False): 
    currency = get_currency(CURRENCY_BY_ID_QUERY, currency_id)

    if currency is None and not quiet:
        raise CurrencyError(404, f"Currency not found: id={currency_id}")
    return currency


def get_currency_by_code(currency_code: str, quiet: bool=False): 
    currency = get_currency(CURRENCY_BY_CODE_QUERY, currency_code)

    if currency is None and not quiet:
        raise CurrencyError(404, f"Currency not found: code={currency_code}")
    return currency


def add_currency(code: str, full_name: str, sign: str):
    lastrowid = -1

    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()

        cur.execute(
            """
				INSERT INTO currencies
				VALUES (NULL, ?, ?, ?);
			""",
            (code, full_name, sign),
        )
        lastrowid = cur.lastrowid
        con.commit()
        cur.close()

    return get_record_by_rowid(CURRENCY_ROWID_QUERY, lastrowid)


# ---------- exchange rates ---------------------------------------------------


def get_exchange_rate(base_currency: Tuple, target_currency: Tuple, quiet: bool=False):
    exchange_rate = None

    with sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        cur.execute(
            """
				SELECT	*
				FROM	exchange_rates
				WHERE	BaseCurrencyId=? AND TargetCurrencyId=?;
			""",
            (base_currency[0], target_currency[0]),
        )

        exchange_rate = cur.fetchone()
        cur.close()

    if exchange_rate is None and not quiet:
        raise ExchangeRateError(404, f"Exchange rate not exist: {base_currency[1]}, {target_currency[1]}")

    return exchange_rate


def get_exchange_rates():
    exchange_rates = []

    with sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        cur.execute(
            """
			SELECT
				e.ID,
				base.ID,
				base.Code,
				base.FullName,
				base.Sign,
				target.ID,
				target.Code,
				target.FullName,
				target.Sign,
				e.Rate
			FROM
				exchange_rates as e
			JOIN
				currencies as base
			ON
				e.BaseCurrencyId = base.ID
			JOIN
				currencies as target
			ON
				e.TargetCurrencyId = target.ID;
			"""
        )

        exchange_rates = cur.fetchall()
        cur.close()

    return exchange_rates


def add_exchange_rate(base_id: int, target_id: int, rate: Decimal):
    lastrowid = -1

    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()

        cur.execute("PRAGMA foreign_keys = ON;")

        cur.execute(
            """
				INSERT INTO exchange_rates
				VALUES (NULL, ?, ?, ?);
			""",
            (base_id, target_id, rate),
        )

        lastrowid = cur.lastrowid
        con.commit()
        cur.close()

    return get_record_by_rowid(EXCHANGE_ROWID_QUERY, lastrowid)


def patch_exchange_rate(exchange_rate_id: int, rate: Decimal):
    lastrowid = -1

    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()

        cur.execute(
            """
                UPDATE exchange_rates
                SET    Rate = ?
                WHERE  Id = ?;
            """,
            (rate, exchange_rate_id),
        )

        lastrowid = cur.lastrowid
        con.commit()
        cur.close()

    return get_record_by_rowid(EXCHANGE_ROWID_QUERY, exchange_rate_id)
