# card_service.py
from __future__ import annotations

from game_state import GameState
from player import Player
from route import Route


class CardService:
    def __init__(self, state: GameState):
        self.state = state

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

    def available_colors_for_gray_route(self, player: Player, route_length: int) -> list[str]:
        locos = sum(1 for c in player.train_cards if c.is_locomotive())
        playable: list[str] = []

        for color in player.card_color_summary():
            normal_count = sum(1 for c in player.train_cards if c.color == color)
            if normal_count + locos >= route_length:
                playable.append(color)

        return playable

    def select_cards_for_route(self, player: Player, route: Route, chosen_color: str | None = None) -> list | None:
        if route.is_gray():
            if not chosen_color:
                return None
            required_color = chosen_color.lower()
        else:
            required_color = route.color_name

        loco_cards = [c for c in player.train_cards if c.is_locomotive()]
        color_cards = [c for c in player.train_cards if c.color == required_color]

        if not route.is_ferry():
            if len(color_cards) >= route.length:
                return color_cards[:route.length]

            combined = color_cards + loco_cards
            return combined[:route.length] if len(combined) >= route.length else None

        L = route.ferry_locos
        color_slots = route.length - L

        locos_for_ferry = min(len(loco_cards), L)
        selected = loco_cards[:locos_for_ferry]
        remaining_locos = loco_cards[locos_for_ferry:]
        ferry_shortage = L - locos_for_ferry

        color_cards_needed_for_shortage = ferry_shortage * 3
        if len(color_cards) < color_cards_needed_for_shortage:
            return None

        selected += color_cards[:color_cards_needed_for_shortage]
        leftover_color = color_cards[color_cards_needed_for_shortage:]

        locos_for_color = min(len(remaining_locos), color_slots)
        selected += remaining_locos[:locos_for_color]

        color_slots_still_uncovered = color_slots - locos_for_color
        if len(leftover_color) < color_slots_still_uncovered:
            return None

        selected += leftover_color[:color_slots_still_uncovered]
        return selected

    @staticmethod
    def remove_cards_from_hand(player: Player, cards: list) -> None:
        for card in cards:
            player.train_cards.remove(card)