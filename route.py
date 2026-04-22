from dataclasses import dataclass


@dataclass
class Route:
    def __init__(self, city_a, city_b, length, color=None):
        self.city_a = city_a
        self.city_b = city_b
        self.length = length
        self.color = color

        self.owner_player = None  # single source of truth

    def is_claimed(self):
        return self.owner_player is not None

    def connects(self, city1: str, city2: str) -> bool:
        return {self.city_a, self.city_b} == {city1, city2}