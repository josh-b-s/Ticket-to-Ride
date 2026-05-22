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


@dataclass(frozen=True)
class CardPlan:
    """
    How many of each card type to spend when claiming a route.

    Returned by ``Route.compute_card_slots``; consumed by both
    ``MoveValidator`` (pass/fail) and ``CardService`` (card selection)
    so the ferry arithmetic lives in exactly one place.
    """
    color_to_use: int
    locos_for_ferry: int
    locos_for_color: int

    @property
    def total_locos(self) -> int:
        return self.locos_for_ferry + self.locos_for_color


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

    #  Predicates 

    def is_claimed(self) -> bool:
        return self.owner_player is not None

    def is_ferry(self) -> bool:
        return self.ferry_locos > 0

    def is_gray(self) -> bool:
        return self.color is RouteColor.GRAY

    def connects(self, city1: str, city2: str) -> bool:
        return {self.city_a, self.city_b} == {city1, city2}

    #  Display helpers 

    @property
    def color_hex(self) -> str:
        return self.color.value

    @property
    def color_name(self) -> str | None:
        """None for gray routes; lowercase colour name otherwise."""
        return None if self.color is RouteColor.GRAY else self.color.name.lower()

    #  Card requirement 

    def compute_card_slots(
            self, color_count: int, loco_count: int
    ) -> CardPlan | None:
        """
        Return a ``CardPlan`` if the route can be claimed with the given
        card counts, or ``None`` if the hand is insufficient.

        Standard routes: prefer colour cards, fill remainder with locos.
        Ferry routes: ferry_locos slots each need 1 loco (or 3 colour cards
        as a substitute); remaining slots use colour cards with spare locos
        acting as wilds.
        """
        if not self.is_ferry():
            if color_count + loco_count < self.length:
                return None
            color_use = min(color_count, self.length)
            loco_use = self.length - color_use
            return CardPlan(color_to_use=color_use, locos_for_ferry=0, locos_for_color=loco_use)

        #  Ferry route 
        L = self.ferry_locos
        color_slots = self.length - L

        locos_for_ferry = min(loco_count, L)
        locos_remaining = loco_count - locos_for_ferry
        ferry_shortage = L - locos_for_ferry  # each missing loco costs 3 colour cards

        locos_for_color = min(locos_remaining, color_slots)
        color_uncovered = color_slots - locos_for_color
        color_needed = color_uncovered + ferry_shortage * 3

        if color_count < color_needed:
            return None

        return CardPlan(
            color_to_use=color_needed,
            locos_for_ferry=locos_for_ferry,
            locos_for_color=locos_for_color,
        )
