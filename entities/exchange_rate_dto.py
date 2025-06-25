from decimal import Decimal

from .currency_dto import CurrencyDTO


class ExchangeRateDTO:
    def __init__(
        self,
        _id: int = None,
        base: CurrencyDTO = None,
        target: CurrencyDTO = None,
        rate: Decimal = 0,
    ):
        self.__id = _id
        self.__base_currency = base
        self.__target_currency = target
        self.__rate = Decimal(str(rate))

    def __str__(self):
        return f"Id: {self.id}, base_currency: {self.base_currency.code}, target currency: {self.target_currency.code}, rate: {self.rate}"

    # --------- propetries ----------------------------------------------------

    @property
    def id(self):
        return self.__id

    @property
    def rate(self):
        return self.__rate

    @property
    def base_currency(self):
        return self.__base_currency

    @property
    def target_currency(self):
        return self.__target_currency

    # ---------- object methods -----------------------------------------------

    # возможны проблемы из-за использования Decimal
    def to_dict(self):
        return {
            "id": self.id,
            "baseCurrency": self.base_currency.to_dict(),
            "targetCurrency": self.target_currency.to_dict(),
            "rate": float(self.rate),
        }


if __name__ == "__main__":
    exchange = ExchangeRateDTO(
        0,
        CurrencyDTO(10, "UAH", "Ukrainian hryvna", "U"),
        CurrencyDTO(12, "RUB", "Russian rubble", "R"),
        0.33443,
    )

    print(exchange)
    print(exchange.to_dict())
