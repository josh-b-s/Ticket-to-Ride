from dataclasses import dataclass
from typing import Optional


@dataclass
class Route:
    city_a: str
    city_b: str
    length: int
    color: Optional[str] = None
    claimed_by: Optional[str] = None
    claimed_color: Optional[str] = None

    def connects(self, city1: str, city2: str) -> bool:
        return {self.city_a, self.city_b} == {city1, city2}

    def is_claimed(self) -> bool:
        return self.claimed_by is not None