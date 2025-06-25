import inspect
from random import randint
import sqlite3

import requests

# import math
# import json


sqlite3_exceptions = [
    name
    for name, value in vars(sqlite3).items()
    if inspect.isclass(value) and issubclass(value, Exception)
]


DB_FILE = "currency_exchange.sqlite3"

# print(*sqlite3_exceptions, sep='\n')


def create_currensies(con: sqlite3.Connection):
    cur = con.cursor()

    cur.execute(
        """
			CREATE TABLE IF NOT EXISTS currencies (
			ID    		INTEGER PRIMARY KEY AUTOINCREMENT,
			Code  		VARCHAR NOT NULL, 
			FullName   	VARCHAR NOT NULL, 
			Sign   		VARCHAR
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


def create_exchange_rates(con: sqlite3.Connection):
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


def add_currency(con: sqlite3.Connection, currency):
    if not (currency and currency[0]):
        print("Error, empty Code!")
        print(currency)
        return

    cur = con.cursor()

    try:
        cur.execute(
            """
				INSERT INTO currencies
				VALUES (NULL, ?, ?, ?);
			""",
            currency,
        )

        con.commit()
    except Exception as e:
        print(currency)
        print(type(e))
        print(e)
        # pass

    # cur.close()


def add_exchange(con: sqlite3.Connection, exchange):
    if not exchange:
        print("Error, empty exchange!")
        return

    cur = con.cursor()

    try:
        cur.execute(
            """
				INSERT INTO exchange_rates
				VALUES (NULL, ?, ?, ?);
			""",
            exchange,
        )

        con.commit()
    except Exception as e:
        print(exchange)
        print(type(e))
        print(e)
        # pass

    # cur.close()


def get_currencies():
    currencies = []

    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()

        try:
            cur.execute(
                """
					SELECT *
					FROM   currencies;
				"""
            )

            currencies = cur.fetchall()
        except:
            pass

    return currencies


def get_currency(code: str):
    currency = []

    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()

        try:
            cur.execute(
                """
					SELECT *
					FROM   currencies
					WHERE Code = ?;
				""",
                (code,),
            )

            currency = cur.fetchone()
        except:
            pass

    return currency


def download_currencies():
    url = "https://www.iban.com/currency-codes"
    headers = {
        "host": "iban.com",
        "user-agent": "my-app/0.0.1",
        "Content-Type": "text/html; charset=utf-8",
    }

    MAX_COLUMN_LEN = 33

    resp = requests.get(url, params=headers)
    currencies = []

    # print("Encoding:", resp.encoding)

    if not (200 <= resp.status_code < 300):
        return currencies

    # print(resp.text)
    start = resp.text.find("<table")
    end = resp.text.find("</table>") + len("</table>")

    if start > 0:
        table = resp.text[start:end]
        body = table[table.find("<tbody") : table.find("</tbody>")]
        rows = body.split("<tr>")

        for row in rows:
            row = row.replace("</tr>", "").strip()
            row = row.replace("&rsquo;", "'")
            cols = []
            for col in row.split("<td>"):
                col = col.replace("</td>", "").strip()
                cols.append(col)

            cols.pop(0)
            currencies.append(cols)

        currencies = list(filter(len, currencies))
        currencies.sort(key=lambda row: (row[2], row[0]))

        return currencies


def download_exchanges():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    resp = requests.get(url)
    exchanges = []

    if not (200 <= resp.status_code < 300):
        return exchanges

    exchanges = resp.json()

    return exchanges["Valute"].values()


currencies = download_currencies()
exchanges = download_exchanges()


with sqlite3.connect(DB_FILE) as con:
    create_currensies(con)
    create_exchange_rates(con)

    for currency in currencies:
        add_currency(con, (currency[2], currency[1], None))

    for exchange in exchanges:
        add_exchange(
            con, (exchange["CharCode"], "RUB", exchange["Value"] / exchange["Nominal"])
        )
