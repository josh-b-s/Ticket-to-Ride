from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.classes.game import Game

from game.classes.route import Route
from game.services.move_validator import MoveValidator, ValidationResult

_ROUTE_POINTS: dict[int, int] = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}
_LAST_ROUND_THRESHOLD = 2


class RouteService:
    def __init__(self, game: Game, card_service, turn_manager) -> None:
        self.game = game
        self.card_service = card_service
        self.turn_manager = turn_manager
        self.validator = MoveValidator()

    def claim_route(
        self, route: Route, chosen_color: str | None = None
    ) -> ValidationResult:
        """
        Validate and apply a route claim for the current player.

        Turn advancement is NOT done here — Game.claim_route owns that so
        last-round detection always fires in the correct order.
        """
        player = self.turn_manager.current_player()
        if player is None:
            return ValidationResult(ok=False, reason="No current player.")

        result = self.validator.validate_claim(
            player,
            route,
            chosen_color,
            self.game.board.routes,
            len(self.game.players),
        )
        if not result.ok:
            return result

        cards = self.card_service.select_cards_for_route(
            player, route, chosen_color
        )
        if cards is None:
            return ValidationResult(
                ok=False,
                reason="Card selection failed unexpectedly.",
                hint="Please report this bug.",
            )

        self.card_service.remove_cards_from_hand(player, cards)
        self.game.train_deck.discard(cards)

        route.owner_player = player
        player.trains -= route.length
        player.score += _ROUTE_POINTS.get(route.length, route.length)

        if (
            player.trains <= _LAST_ROUND_THRESHOLD
            and not self.game.last_round_triggered
        ):
            self.game.last_round_triggered = True
            self.game.last_player_index = self.game.current_player_index

        return ValidationResult(
            ok=True, reason=self._claim_message(route, player, chosen_color)
        )

    @staticmethod
    def _claim_message(
        route: Route, player, chosen_color: str | None
    ) -> str:
        desc = f"{route.city_a} \u2014 {route.city_b}"
        msg = (
            f"{player.name} claimed {desc} using {chosen_color.title()} cards."
            if route.is_gray() and chosen_color
            else f"{player.name} claimed {desc}."
        )
        return msg + " (Ferry)" if route.is_ferry() else msg