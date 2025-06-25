from decimal import Decimal

from .currency_dto import CurrencyDTO


class ExchangeDTO:
    def __init__(
        self,
        base: CurrencyDTO = None,
        target: CurrencyDTO = None,
        rate: Decimal = 0,
        amount: Decimal = 0,
    ):
        self.__base_currency = base
        self.__target_currency = target
        self.__rate = Decimal(str(rate))
        self.__amount = Decimal(str(amount))

    def __str__(self):
        return f"Base_currency: {self.base_currency.code}, target currency: {self.target_currency.code}, rate: {self.rate}, amount: {self.amount}, converted amount: {self.converted_amount}"

    # --------- propetries ----------------------------------------------------

    @property
    def base_currency(self) -> CurrencyDTO:
        return self.__base_currency

    @property
    def target_currency(self) -> CurrencyDTO:
        return self.__target_currency

    @property
    def rate(self) -> Decimal:
        return self.__rate

    @property
    def amount(self) -> Decimal:
        return self.__amount

    @property
    def converted_amount(self) -> Decimal:
        return Decimal(self.rate * self.amount)

    # ---------- object methods -----------------------------------------------

    # возможны проблемы из-за использования Decimal
    def to_dict(self):
        return {
            "baseCurrency": self.base_currency.to_dict(),
            "targetCurrency": self.target_currency.to_dict(),
            "rate": float(self.rate),
            "amount": float(self.amount),
            "convertedAmount": round(float(self.converted_amount), 2),
        }


if __name__ == "__main__":
    import json

    exchange = ExchangeDTO(
        CurrencyDTO(10, "UAH", "Ukrainian hryvna", "U"),
        CurrencyDTO(12, "RUB", "Russian rubble", "R"),
        0.00316719,
        10,
    )
    print(exchange)
    print(exchange.to_dict())
    print(json.dumps(exchange.to_dict(), indent=4))
