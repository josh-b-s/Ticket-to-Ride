from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Route:
    city_a: str
    city_b: str
    length: int
    color: Optional[str] = None
    owner_player: Optional["Player"] = field(default=None, compare=False)
    # Number of locomotive symbols on the route (0 = not a ferry).
    ferry_locos: int = 0

    def is_claimed(self) -> bool:
        return self.owner_player is not None

    def is_ferry(self) -> bool:
        return self.ferry_locos > 0

    def connects(self, city1: str, city2: str) -> bool:
        return {self.city_a, self.city_b} == {city1, city2}