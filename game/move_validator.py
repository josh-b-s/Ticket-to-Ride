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
        player: "Player",
        route: "Route",
        chosen_color: Optional[str],
        all_routes: list["Route"],
        player_count: int,
    ) -> ValidationResult:
        """
        Check every precondition for claiming *route*.

        Returns ValidationResult with ok=True when the claim is legal.
        On failure, *reason* is a short UI message and *hint* gives the
        player specific details about what they are missing.
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

        # BUG FIX: for gray routes use chosen_color; for coloured routes use
        # route.color_name.  Previously route.color_name was always used, which
        # returns None for gray routes and caused every gray-route claim to fail
        # immediately with "No colour selected" regardless of the dialog choice.
        if route.is_gray():
            if not chosen_color:
                return ValidationResult(
                    ok=False,
                    reason="No colour selected for the gray route.",
                    hint="Pick a colour you have enough cards of.",
                )
            required_color = chosen_color.lower()
        else:
            required_color = route.color_name  # always a non-None string here

        if route.is_ferry():
            return self._validate_ferry(player, route, required_color)

        return self._validate_standard(player, route, required_color)

    # ---------------------------------------------------------------- helpers

    def _validate_standard(
        self,
        player: "Player",
        route: "Route",
        required_color: str,
    ) -> ValidationResult:
        """Validate a non-ferry route claim."""
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

    def _validate_ferry(
        self,
        player: "Player",
        route: "Route",
        required_color: str,
    ) -> ValidationResult:
        """
        Validate a ferry route claim.

        Ferry rules:
          - ferry_locos slots must each be covered by 1 locomotive card.
          - If the player is short on locomotives, any 3 color cards substitute
            for each missing locomotive (spending more cards in total).
          - Remaining (length - ferry_locos) color slots use color cards,
            with extra locomotives usable as wilds.
        """
        L = route.ferry_locos
        color_slots = route.length - L

        avail_locos = sum(1 for c in player.train_cards if c.is_locomotive())
        avail_color = sum(
            1 for c in player.train_cards if c.color == required_color
        )

        # Locos committed to ferry slots (1:1 — most efficient use).
        locos_for_ferry = min(avail_locos, L)
        locos_remaining = avail_locos - locos_for_ferry
        ferry_shortage = L - locos_for_ferry  # each missing loco costs 3 cards

        # Spare locos cover color slots as wilds.
        locos_for_color = min(locos_remaining, color_slots)
        color_slots_uncovered = color_slots - locos_for_color

        # Total color cards required.
        color_needed = color_slots_uncovered + ferry_shortage * 3

        if avail_color < color_needed:
            color_name = required_color.title()
            parts = [
                f"Ferry route — needs {L} locomotive(s) for the water crossing."
            ]
            if ferry_shortage > 0:
                parts.append(
                    f"You are short {ferry_shortage} locomotive(s); "
                    f"each can be replaced by 3 {color_name} cards "
                    f"({ferry_shortage * 3} extra card(s) total)."
                )
            parts.append(
                f"Total {color_name} cards required: {color_needed}. "
                f"You have {avail_color}. "
                f"Short by {color_needed - avail_color} card(s)."
            )
            return ValidationResult(
                ok=False,
                reason="Not enough cards for this ferry route.",
                hint=" ".join(parts),
            )

        return ValidationResult(ok=True)