class CurrencyDTO:
    def __init__(
        self, _id: int = None, code: str = "", full_name: str = "", sign: str = ""
    ):
        self.__id = _id
        self.__code = code
        self.__full_name = full_name
        self.__sign = sign

    def __str__(self):
        return f"Id: {self.id}, code: '{self.code}', name: '{self.full_name}', sign: '{self.sign}'"

    # --------- propetries ----------------------------------------------------

    @property
    def id(self):
        return self.__id

    @property
    def code(self):
        return self.__code

    @property
    def sign(self):
        return self.__sign

    @property
    def full_name(self):
        return self.__full_name

    # ---------- object methods -----------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.full_name,
            "code": self.code,
            "sign": self.sign,
        }


if __name__ == "__main__":
    cur = CurrencyDTO(0, "RUB", "Russian rubble", "₽")
    print(cur)
