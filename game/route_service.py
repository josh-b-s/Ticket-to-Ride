# route_service.py
from __future__ import annotations

from game_state import GameState
from move_validator import MoveValidator, ValidationResult
from player import Player
from route import Route

_ROUTE_POINTS: dict[int, int] = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}
_LAST_ROUND_THRESHOLD = 2


class RouteService:
    def __init__(self, state: GameState, card_service, turn_manager):
        self.state = state
        self.card_service = card_service
        self.turn_manager = turn_manager
        self.validator = MoveValidator()

    def claim_route(self, route: Route, chosen_color: str | None = None) -> ValidationResult:
        player = self.turn_manager.current_player()
        if player is None:
            return ValidationResult(ok=False, reason="No current player.")

        result = self.validator.validate_claim(
            player,
            route,
            chosen_color,
            self.state.board.routes,
            len(self.state.players),
        )
        if not result.ok:
            return result

        cards = self.card_service.select_cards_for_route(player, route, chosen_color)
        if cards is None:
            return ValidationResult(
                ok=False,
                reason="Card selection failed unexpectedly.",
                hint="Please report this bug.",
            )

        self.card_service.remove_cards_from_hand(player, cards)
        self.state.train_deck.discard(cards)

        route.owner_player = player
        player.trains -= route.length
        player.score += _ROUTE_POINTS.get(route.length, route.length)

        if player.trains <= _LAST_ROUND_THRESHOLD and not self.state.last_round_triggered:
            self.state.last_round_triggered = True
            self.state.last_player_index = self.state.current_player_index

        route_desc = f"{route.city_a} – {route.city_b}"
        if route.is_gray() and chosen_color:
            message = f"{player.name} claimed {route_desc} using {chosen_color.title()} cards."
        else:
            message = f"{player.name} claimed {route_desc}."

        if route.is_ferry():
            message += " (Ferry)"

        self.turn_manager.next_player()
        return ValidationResult(ok=True, reason=message)