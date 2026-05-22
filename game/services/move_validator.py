"""Validation logic for route-claim moves."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from game.classes.player import Player
    from game.classes.route import Route


@dataclass
class ValidationResult:
    """Structured result returned by MoveValidator and Game.claim_route."""
    ok: bool
    reason: str = ""
    hint: str = ""


class MoveValidator:
    """
    Validates whether a player may claim a route.

    Card-sufficiency checks delegate entirely to ``route.compute_card_slots``
    (which returns a ``CardPlan``).  Neither the ferry math nor the standard
    math is re-implemented here; this class is responsible only for rule
    checks (ownership, train count, colour selection) and failure messages.
    """

    def validate_claim(
        self,
        player: "Player",
        route: "Route",
        chosen_color: Optional[str],
        all_routes: list["Route"],
        player_count: int,
    ) -> ValidationResult:
        """Check every precondition for claiming *route*."""

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
                reason=f"Not enough trains — need {route.length}, have {player.trains}.",
                hint="Claim shorter routes to spend your remaining trains.",
            )

        if route.is_gray():
            if not chosen_color:
                return ValidationResult(
                    ok=False,
                    reason="No colour selected for the gray route.",
                    hint="Pick a colour you have enough cards of.",
                )
            required_color = chosen_color.lower()
        else:
            required_color = route.color_name

        return self._validate_cards(player, route, required_color)

    # ── Card sufficiency ──────────────────────────────────────────────────────

    def _validate_cards(
        self,
        player: "Player",
        route: "Route",
        required_color: str,
    ) -> ValidationResult:
        color_count = sum(1 for c in player.train_cards if c.color == required_color)
        loco_count  = sum(1 for c in player.train_cards if c.is_locomotive())

        if route.compute_card_slots(color_count, loco_count) is not None:
            return ValidationResult(ok=True)

        # Build a detailed failure message
        color_name = required_color.title()
        if route.is_ferry():
            return self._ferry_failure(route, color_name, color_count, loco_count)

        available = color_count + loco_count
        return ValidationResult(
            ok=False,
            reason="Not enough cards to claim this route.",
            hint=(
                f"Need {route.length} {color_name} card(s). "
                f"You have {color_count} {color_name} "
                f"+ {loco_count} locomotive(s) = {available} total. "
                f"Short by {route.length - available} card(s)."
            ),
        )

    @staticmethod
    def _ferry_failure(
        route: "Route",
        color_name: str,
        color_count: int,
        loco_count: int,
    ) -> ValidationResult:
        """Build a descriptive failure result for an unaffordable ferry route."""
        L               = route.ferry_locos
        locos_for_ferry = min(loco_count, L)
        ferry_shortage  = L - locos_for_ferry
        locos_remaining = loco_count - locos_for_ferry
        color_slots     = route.length - L
        locos_for_color = min(locos_remaining, color_slots)
        color_needed    = (color_slots - locos_for_color) + ferry_shortage * 3

        parts = [f"Ferry route — needs {L} locomotive(s) for the water crossing."]
        if ferry_shortage > 0:
            parts.append(
                f"You are short {ferry_shortage} locomotive(s); "
                f"each can be replaced by 3 {color_name} cards "
                f"({ferry_shortage * 3} extra card(s) total)."
            )
        parts.append(
            f"Total {color_name} cards required: {color_needed}. "
            f"You have {color_count}. "
            f"Short by {color_needed - color_count} card(s)."
        )
        return ValidationResult(
            ok=False,
            reason="Not enough cards for this ferry route.",
            hint=" ".join(parts),
        )
