import json
from game.classes.route import Route, RouteColor


class Board:
    def __init__(self, path: str = "board.json") -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.cities: dict[str, tuple[int, int]] = {
            name: tuple(coords) for name, coords in data["cities"].items()
        }
        self.routes: list[Route] = [self._parse_route(r) for r in data["routes"]]

    @staticmethod
    def _parse_route(r: dict) -> Route:
        color_name = r.get("color", "GRAY").upper()
        try:
            color = RouteColor[color_name]
        except KeyError:
            raise ValueError(f"Unknown route color {color_name!r} in board data.")
        return Route(
            r["a"], r["b"], r["length"], color,
            ferry_locos=r.get("ferry_locos", 0),
        )

    def get_routes(self, city_a: str, city_b: str) -> list[Route]:
        return [r for r in self.routes if r.connects(city_a, city_b)]

    def get_bounds(self) -> tuple[int, int, int, int]:
        xs = [x for x, _ in self.cities.values()]
        ys = [y for _, y in self.cities.values()]
        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
