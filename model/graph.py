import json
from typing import List


class Graph:

    def __init__(self):
        self.__graph = dict()

    def add_pair(self, a, b):
        self.__graph.setdefault(a, set()).add(b)
        self.__graph.setdefault(b, set()).add(a)

    def get_intersections(self, a, b):
        set_a = self.__graph.get(a, set())
        set_b = self.__graph.get(b, set())

        return list(set_a.intersection(set_b))

    def get_path(self, a, b) -> List:

        # поиск в ширину
        start = a
        current = None

        deque = [start]
        visited = {start: None}

        while len(deque):
            current = deque.pop()

            if current == b:
                break

            bucket = self.__graph.get(current, set())

            for v in bucket:
                if v in visited:
                    continue

                deque.insert(0, v)
                visited[v] = current

                if v == b:
                    break
        else:
            return []

        path = []
        target = current

        # восстанавливаем путь до цели
        while target != start:
            path.insert(0, target)
            target = visited[target]

        return path if not path else [a] + path

    def __str__(self):
        return json.dumps(self.__graph, indent=4, cls=GraphEncoder)

    def print_graph(self):
        for key, value in self.__graph.items():
            print(f"{key}: {value}")


class GraphEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return str(list(obj))
        return super().default(obj)


if __name__ == "__main__":
    exchanges = Graph()

    exchanges.add_pair("UAH", "RUB")
    exchanges.add_pair("USD", "RUB")
    exchanges.add_pair("EUR", "USD")
    exchanges.add_pair("JPY", "UAH")
    exchanges.add_pair("NZD", "MVR")
    # exchanges.add_pair("UAH", "USD")

    print("UAH >> USD =", exchanges.get_path("UAH", "USD"))
    print("UAH >> EUR =", exchanges.get_path("UAH", "EUR"))
    print("EUR >> UAH =", exchanges.get_path("EUR", "UAH"))
    print("RUB >> JPY =", exchanges.get_path("RUB", "JPY"))
    print("RUB >> UAH =", exchanges.get_path("RUB", "UAH"))
    print("UAH >> MZD =", exchanges.get_path("UAH", "MZD"))
    print()
    exchanges.print_graph()
    # print(exchanges)

    print(exchanges.get_intersections("UAH", "USD"))
    print(exchanges.get_intersections("UAH", "EUR"))
    print(exchanges.get_intersections("UAH", "USD"))
    print(exchanges.get_intersections("RUB", "JPY"))
    # print(exchanges)
