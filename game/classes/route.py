from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RouteColor(Enum):
    BLUE = "#1E82C8"
    GREEN = "#32A532"
    BLACK = "#323232"
    YELLOW = "#FAEA00"
    ORANGE = "#F08C00"
    PINK = "#E35C98"
    GRAY = "#B0B0B3"


@dataclass
class Route:
    city_a: str
    city_b: str
    length: int
    color: RouteColor = RouteColor.GRAY
    owner_player: Optional["Player"] = field(default=None, compare=False)
    ferry_locos: int = 0

    def __post_init__(self) -> None:
        if self.length < 1:
            raise ValueError(f"Route length must be at least 1, got {self.length}.")
        if self.ferry_locos < 0:
            raise ValueError(f"ferry_locos cannot be negative, got {self.ferry_locos}.")
        if self.ferry_locos > self.length:
            raise ValueError(
                f"ferry_locos ({self.ferry_locos}) cannot exceed route length ({self.length})."
            )

    def is_claimed(self) -> bool:
        return self.owner_player is not None

    def is_ferry(self) -> bool:
        return self.ferry_locos > 0

    def is_gray(self) -> bool:
        return self.color is RouteColor.GRAY

    def connects(self, city1: str, city2: str) -> bool:
        return {self.city_a, self.city_b} == {city1, city2}

    @property
    def color_hex(self) -> str:
        return self.color.value

    @property
    def color_name(self) -> str | None:
        return None if self.color is RouteColor.GRAY else self.color.name.lower()