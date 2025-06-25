import sqlite3
import requests

from decimal import Decimal
from exceptions import get_error_type
from model import data_base as base


def download_currencies():
    url = "https://www.iban.com/currency-codes"
    headers = {
        "host": "iban.com",
        "user-agent": "my-app/0.0.1",
        "Content-Type": "text/html; charset=utf-8",
    }

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


base.create_currensies()
base.create_exchange_rates()


# заполняем таблицу <currencies>
for currency in filter(lambda c: c[2] != "", currencies):
    try:
        c = base.add_currency(currency[2], currency[1], None)
        print(c)
    except sqlite3.Error as e:
        #pass
        print(get_error_type(type(e)))


# заполняем таблицу <exchange_rates>
for exchange in exchanges:
    try:
        base_currency = base.get_currency_by_code(exchange["CharCode"])
        target_currency = base.get_currency_by_code("RUB")
        rate = Decimal(str(exchange["Value"])) / Decimal(str(exchange["Nominal"]))
        e = base.add_exchange_rate(base_currency[0], target_currency[0], rate)
        print(e)
    except sqlite3.Error as e:
        #pass
        print(get_error_type(type(e)))

try:
    base.add_currency(())  # ("LOL", "Valute of cringeville"))
except sqlite3.Error as e:
    print(get_error_type(type(e)), ":", e)
except Exception as e:
    print(f"{type(e)}: {e}")
