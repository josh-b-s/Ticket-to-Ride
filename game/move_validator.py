"""Validation logic for route-claim moves."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from player import Player
    from route import Route


@dataclass
class ValidationResult:
    """Structured result returned by MoveValidator and Game.claim_route."""

    ok: bool
    reason: str = ""
    hint: str = ""


class MoveValidator:
    """
    Validates whether a player may claim a route.

    Separating validation from Game keeps claim_route focused on
    state mutation and makes each rule independently testable.
    """

    def validate_claim(
        self,
        player: Player,
        route: Route,
        chosen_color: Optional[str],
        all_routes: list[Route],
        player_count: int,
    ) -> ValidationResult:
        """
        Check every precondition for claiming *route*.

        Returns a ValidationResult with ok=True when the claim is legal.
        On failure, *reason* is a short UI-ready message and *hint*
        explains specifically what the player is missing or must do.
        """
        if route.is_claimed():
            return ValidationResult(
                ok=False,
                reason="That route is already claimed.",
                hint="Choose a different route between these cities.",
            )

        same_routes = [
            r for r in all_routes
            if {r.city_a, r.city_b} == {route.city_a, route.city_b}
        ]

        if player_count <= 3 and any(r.is_claimed() for r in same_routes):
            return ValidationResult(
                ok=False,
                reason="Route blocked in a 2–3 player game.",
                hint=(
                    "With 3 or fewer players only one route between "
                    "two cities may be claimed."
                ),
            )

        if any(
            r is not route and r.is_claimed() and r.owner_player is player
            for r in same_routes
        ):
            return ValidationResult(
                ok=False,
                reason="You already own a route between these two cities.",
                hint="Each player may claim at most one of the parallel routes.",
            )

        if player.trains < route.length:
            return ValidationResult(
                ok=False,
                reason=(
                    f"Not enough trains — need {route.length}, "
                    f"have {player.trains}."
                ),
                hint="Claim shorter routes to spend your remaining trains.",
            )

        required_color = route.color if route.color is not None else chosen_color
        if required_color is None:
            return ValidationResult(
                ok=False,
                reason="No colour selected for the gray route.",
                hint="",
            )

        matching = sum(
            1 for c in player.train_cards if c.color == required_color
        )
        locos = sum(1 for c in player.train_cards if c.is_locomotive())
        available = matching + locos

        if available < route.length:
            short = route.length - available
            color_name = required_color.title()
            return ValidationResult(
                ok=False,
                reason="Not enough cards to claim this route.",
                hint=(
                    f"Need {route.length} {color_name} card(s). "
                    f"You have {matching} {color_name} "
                    f"+ {locos} locomotive(s) = {available} total. "
                    f"Short by {short} card(s)."
                ),
            )

        return ValidationResult(ok=True)