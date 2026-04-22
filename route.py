from dataclasses import dataclass
from typing import Optional


@dataclass
class Route:
    city_a: str
    city_b: str
    length: int
    color: Optional[str] = None
    owner_player: Optional["Player"] = None

    def is_claimed(self):
        return self.owner_player is not None

    def connects(self, city1: str, city2: str) -> bool:
        return {self.city_a, self.city_b} == {city1, city2}