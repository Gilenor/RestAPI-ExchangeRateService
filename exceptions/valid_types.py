from types import SimpleNamespace

__CODE = "[A-Z]{3}"
__CHAR = "."
__STRING = ".*"
__POSITIVE_FLOAT = "[0][.][0-9]*|[1-9][0-9]*[.]?[0-9]*"

__SIGN = ".?"


match_types = SimpleNamespace(
    CODE=__CODE,
    RATE=__POSITIVE_FLOAT,
    AMOUNT=__POSITIVE_FLOAT,
    Currency=SimpleNamespace(),
    Exchange=SimpleNamespace(),
    ExchangeRate=SimpleNamespace(),
)

match_types.Currency.Get = SimpleNamespace(names=("code",), types=(__CODE,))

match_types.Currency.Post = SimpleNamespace(
    names=("code", "name", "sign"), types=(__CODE, __STRING, __SIGN)
)

match_types.Exchange.Get = SimpleNamespace(
    names=("from", "to", "amount"), types=(__CODE, __CODE, __POSITIVE_FLOAT)
)

match_types.ExchangeRate.Get = SimpleNamespace(
    names=("fromCurrency", "toCurrency"), types=(__CODE, __CODE)
)

match_types.ExchangeRate.Post = SimpleNamespace(
    names=("baseCurrencyCode", "targetCurrencyCode", "rate"),
    types=(__CODE, __CODE, __POSITIVE_FLOAT),
)

match_types.ExchangeRate.Patch = SimpleNamespace(
    names=("fromCurrency", "toCurrency", "rate"), types=(__CODE, __CODE, __POSITIVE_FLOAT)
)
