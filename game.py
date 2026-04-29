from __future__ import annotations

import random
from typing import Callable

from board import Board
from destination_ticket import DestinationTicket
from player import Player
from route import Route
from train_deck import TrainDeck

_ROUTE_POINTS: dict[int, int] = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}
_LAST_ROUND_THRESHOLD = 2


class Game:
    def __init__(self):
        self.players: list[Player] = []
        self.current_player_index: int = 0
        self.board = Board()
        self.train_deck = TrainDeck()
        self.destination_deck: list[DestinationTicket] = []
        self.last_round_triggered: bool = False
        self.last_player_index: int | None = None
        # Game-over state — checked by the UI after each action
        self.game_over: bool = False
        self.on_game_end: Callable | None = None  # optional UI callback

    # ---------------------------------------------------------------- proxies

    @property
    def cities(self):
        return self.board.cities

    @property
    def routes(self):
        return self.board.routes

    def get_routes(self, city_a: str, city_b: str):
        return self.board.get_routes(city_a, city_b)

    def get_bounds(self):
        return self.board.get_bounds()

    # -------------------------------------------------------------- setup / start

    def add_player(self, name: str) -> Player | None:
        name = name.strip()
        if not name or any(p.name.lower() == name.lower() for p in self.players):
            return None
        player = Player(name)
        self.players.append(player)
        return player

    def get_players(self) -> list[Player]:
        return self.players

    def start(self) -> None:
        if len(self.players) < 2:
            raise ValueError("At least 2 players are required.")

        self.board = Board()
        self.train_deck = TrainDeck()
        self.current_player_index = 0
        self.last_round_triggered = False
        self.last_player_index = None
        self.game_over = False

        for p in self.players:
            p.score = 0
            p.trains = 45
            p.train_cards.clear()
            p.destination_tickets.clear()

        self._build_destination_deck()
        self._deal_initial_train_cards()

    def _deal_initial_train_cards(self) -> None:
        for p in self.players:
            for _ in range(4):
                card = self.train_deck.draw()
                if card:
                    p.train_cards.append(card)

    # ------------------------------------------------------------ turn helpers

    def current_player(self) -> Player | None:
        return self.players[self.current_player_index] if self.players else None

    def next_player(self) -> None:
        if not self.players:
            return
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.last_round_triggered and self.current_player_index == self.last_player_index:
            self._end_game()

    # ---------------------------------------------------------- train cards

    def draw_train_card_from_deck(self, player: Player) -> object | None:
        card = self.train_deck.draw()
        if card:
            player.train_cards.append(card)
        return card

    def draw_train_card_from_face_up(self, player: Player, index: int) -> object | None:
        card = self.train_deck.draw_face_up(index)
        if card:
            player.train_cards.append(card)
        return card

    def select_cards_for_route(
            self, player: Player, route: Route, chosen_color: str | None = None
    ) -> list | None:
        required_color = route.color if route.color is not None else chosen_color
        if required_color is None:
            return None

        matching = [c for c in player.train_cards if c.color == required_color]
        if len(matching) >= route.length:
            return matching[: route.length]

        locos = [c for c in player.train_cards if c.is_locomotive()]
        combined = matching + locos
        return combined[: route.length] if len(combined) >= route.length else None

    def remove_cards_from_hand(self, player: Player, cards: list) -> None:
        for card in cards:
            player.train_cards.remove(card)

    def claim_route(self, route: Route, chosen_color: str | None = None) -> tuple[bool, str]:
        player = self.current_player()
        if player is None:
            return False, "No current player."
        if route.is_claimed():
            return False, "That route is already claimed."

        same_routes = [r for r in self.routes if {r.city_a, r.city_b} == {route.city_a, route.city_b}]
        if len(self.players) <= 3 and any(r.is_claimed() for r in same_routes):
            return False, "Route blocked in 2–3 player game."

        if player.trains < route.length:
            return False, "Not enough trains."

        cards = self.select_cards_for_route(player, route, chosen_color)
        if not cards:
            return False, "You do not have the required cards."

        self.remove_cards_from_hand(player, cards)
        self.train_deck.discard(cards)

        route.owner_player = player
        player.trains -= route.length
        player.score += _ROUTE_POINTS.get(route.length, route.length)

        if player.trains <= _LAST_ROUND_THRESHOLD and not self.last_round_triggered:
            self.last_round_triggered = True
            self.last_player_index = self.current_player_index

        self.next_player()
        return True, "Route claimed."

    # -------------------------------------------------------- destination tickets

    def _build_destination_deck(self) -> None:
        self.destination_deck = [
            DestinationTicket("King's Cross", "Waterloo", 5),
            DestinationTicket("Baker Street", "Big Ben", 5),
            DestinationTicket("Regent's Park", "Tower of London", 8),
            DestinationTicket("Hyde Park", "Brick Lane", 7),
            DestinationTicket("Buckingham Palace", "Elephant & Castle", 6),
            DestinationTicket("Covent Garden", "St Paul's", 4),
        ]
        random.shuffle(self.destination_deck)

    def draw_destination_tickets(self, count: int = 3) -> list[DestinationTicket]:
        drawn = []
        for _ in range(count):
            if self.destination_deck:
                drawn.append(self.destination_deck.pop())
        return drawn

    def keep_destination_tickets(
            self,
            player: Player,
            chosen: list[DestinationTicket],
            drawn: list[DestinationTicket],
            advance_turn: bool = True,
    ) -> tuple[bool, str]:
        """Assign chosen tickets to player; return unchosen to bottom of deck."""
        if not chosen:
            return False, "You must keep at least 1 ticket."

        for ticket in chosen:
            player.destination_tickets.append(ticket)

        returned = [t for t in drawn if t not in chosen]
        self.destination_deck = returned + self.destination_deck

        if advance_turn:
            self.next_player()
        return True, "Tickets chosen."

    # ------------------------------------------------------------- end-game

    def _calculate_destination_scores(self) -> None:
        for player in self.players:
            player.completed_tickets = 0
            for ticket in player.destination_tickets:
                if self._is_connected(player, ticket.city_a, ticket.city_b):
                    player.score += ticket.points
                    player.completed_tickets += 1
                else:
                    player.score -= ticket.points

    def _is_connected(self, player: Player, start: str, end: str) -> bool:
        return self._dfs(player, start, end, set())

    def _dfs(self, player: Player, current: str, target: str, visited: set) -> bool:
        if current == target:
            return True
        visited.add(current)
        for route in self.routes:
            if route.owner_player != player:
                continue
            if route.city_a == current:
                nxt = route.city_b
            elif route.city_b == current:
                nxt = route.city_a
            else:
                continue
            if nxt not in visited and self._dfs(player, nxt, target, visited):
                return True
        return False

    def _longest_route_length(self, player: Player) -> int:
        graph: dict[str, list[tuple[str, int]]] = {}
        for route in self.routes:
            if route.owner_player != player:
                continue
            a, b = route.city_a, route.city_b
            graph.setdefault(a, []).append((b, route.length))
            graph.setdefault(b, []).append((a, route.length))

        best = 0
        visited_edges: set = set()

        def dfs(city: str, length: int) -> None:
            nonlocal best
            best = max(best, length)
            for nxt, weight in graph.get(city, []):
                edge = tuple(sorted((city, nxt)))
                if edge in visited_edges:
                    continue
                visited_edges.add(edge)
                dfs(nxt, length + weight)
                visited_edges.remove(edge)

        for start in graph:
            dfs(start, 0)

        return best

    def _end_game(self) -> None:
        self.game_over = True
        self._calculate_destination_scores()

        route_lengths = {p: self._longest_route_length(p) for p in self.players}
        max_len = max(route_lengths.values(), default=0)
        for p, length in route_lengths.items():
            if length == max_len:
                p.score += 10

        if self.on_game_end:
            self.on_game_end(route_lengths)
