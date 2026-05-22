from __future__ import annotations

from game.classes.player import Player
from game.classes.route import Route
from game.services.game_state import GameState


class CardService:
    def __init__(self, state: GameState) -> None:
        self.state = state

    #  Draw actions 

    def draw_from_deck(self, player: Player):
        card = self.state.train_deck.draw()
        if card:
            player.train_cards.append(card)
        return card

    def draw_from_face_up(self, player: Player, index: int):
        card = self.state.train_deck.draw_face_up(index)
        if card:
            player.train_cards.append(card)
        return card

    #  Route card helpers 

    def available_colors_for_gray_route(
            self, player: Player, route_length: int
    ) -> list[str]:
        """Return colour names the player can legally spend on a gray route."""
        locos = sum(1 for c in player.train_cards if c.is_locomotive())
        return [
            color
            for color in player.card_color_summary()
            if sum(1 for c in player.train_cards if c.color == color) + locos >= route_length
        ]

    def select_cards_for_route(
            self,
            player: Player,
            route: Route,
            chosen_color: str | None = None,
    ) -> list | None:
        """
        Return the exact card objects to spend, or None if insufficient.

        All slot arithmetic is delegated to ``route.compute_card_slots``
        via the ``CardPlan`` it returns, so the ferry math is not duplicated.
        """
        required_color = chosen_color.lower() if route.is_gray() else route.color_name
        if required_color is None:
            return None

        color_cards = [c for c in player.train_cards if c.color == required_color]
        loco_cards = [c for c in player.train_cards if c.is_locomotive()]

        plan = route.compute_card_slots(len(color_cards), len(loco_cards))
        if plan is None:
            return None

        return color_cards[: plan.color_to_use] + loco_cards[: plan.total_locos]

    @staticmethod
    def remove_cards_from_hand(player: Player, cards: list) -> None:
        for card in cards:
            player.train_cards.remove(card)
