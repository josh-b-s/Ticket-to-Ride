from __future__ import annotations

import random
from typing import Callable

from board import Board
from destination_ticket import DestinationTicket
from move_validator import MoveValidator, ValidationResult
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
        self.game_over: bool = False
        self.on_game_end: Callable | None = None
        self.final_standings: list[Player] = []
        self._validator = MoveValidator()

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

    # -------------------------------------------------------------- setup

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
        self.final_standings = []

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
        self.current_player_index = (
            (self.current_player_index + 1) % len(self.players)
        )
        if (
            self.last_round_triggered
            and self.current_player_index == self.last_player_index
        ):
            self._end_game()

    # ---------------------------------------------------------- train cards

    def draw_train_card_from_deck(self, player: Player) -> object | None:
        card = self.train_deck.draw()
        if card:
            player.train_cards.append(card)
        return card

    def draw_train_card_from_face_up(
        self, player: Player, index: int
    ) -> object | None:
        card = self.train_deck.draw_face_up(index)
        if card:
            player.train_cards.append(card)
        return card

    def available_colors_for_gray_route(
        self, player: Player, route_length: int
    ) -> list[str]:
        """Return colors the player can spend on a gray route."""
        locos = sum(1 for c in player.train_cards if c.is_locomotive())
        playable: list[str] = []
        for color in player.card_color_summary():
            normal_count = sum(
                1 for c in player.train_cards if c.color == color
            )
            if normal_count + locos >= route_length:
                playable.append(color)
        return playable

    def select_cards_for_route(
        self,
        player: Player,
        route: Route,
        chosen_color: str | None = None,
    ) -> list | None:
        """Select the cards to spend, preferring color cards over locomotives."""
        required_color = (
            route.color if route.color is not None else chosen_color
        )
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

    def claim_route(
        self, route: Route, chosen_color: str | None = None
    ) -> ValidationResult:
        """
        Attempt to claim *route* for the current player.

        Validation is delegated entirely to MoveValidator so this method
        only handles state mutation on a valid claim.
        """
        player = self.current_player()
        if player is None:
            return ValidationResult(ok=False, reason="No current player.")

        result = self._validator.validate_claim(
            player,
            route,
            chosen_color,
            self.routes,
            len(self.players),
        )
        if not result.ok:
            return result

        cards = self.select_cards_for_route(player, route, chosen_color)
        if cards is None:
            # Should not happen if validator passed — guard against logic drift.
            return ValidationResult(
                ok=False,
                reason="Card selection failed unexpectedly.",
                hint="This is likely a bug — please report it.",
            )

        self.remove_cards_from_hand(player, cards)
        self.train_deck.discard(cards)

        route.owner_player = player
        player.trains -= route.length
        player.score += _ROUTE_POINTS.get(route.length, route.length)

        if (
            player.trains <= _LAST_ROUND_THRESHOLD
            and not self.last_round_triggered
        ):
            self.last_round_triggered = True
            self.last_player_index = self.current_player_index

        route_desc = f"{route.city_a} – {route.city_b}"
        if route.color is None and chosen_color:
            message = (
                f"{player.name} claimed {route_desc} "
                f"using {chosen_color.title()} cards."
            )
        else:
            message = f"{player.name} claimed {route_desc}."

        self.next_player()
        return ValidationResult(ok=True, reason=message)

    # -------------------------------------------------------- destination tickets

    def _build_destination_deck(self) -> None:
        self.destination_deck = [
            DestinationTicket("King's Cross", "Waterloo", 5),
            DestinationTicket("Baker Street", "Big Ben", 5),
            DestinationTicket("Regent's Park", "Tower of London", 8),
            DestinationTicket("Hyde Park", "Brick Lane", 7),
            DestinationTicket("Buckingham Palace", "Elephant & Castle", 6),
            DestinationTicket("Covent Garden", "St Paul's", 4),
            DestinationTicket("Baker Street", "Tower of London", 9),
            DestinationTicket("Hyde Park", "Globe Theatre", 8),
            DestinationTicket("King's Cross", "Elephant & Castle", 9),
            DestinationTicket("Regent's Park", "Big Ben", 5),
            DestinationTicket("Baker Street", "Trafalgar Square", 4),
            DestinationTicket("The Charterhouse", "Buckingham Palace", 7),
            DestinationTicket("Piccadilly Circus", "Tower of London", 6),
            DestinationTicket("Trafalgar Square", "Brick Lane", 7),
            DestinationTicket("Hyde Park", "St Paul's", 6),
            DestinationTicket("British Museum", "Elephant & Castle", 5),
            DestinationTicket("King's Cross", "Globe Theatre", 7),
            DestinationTicket("Waterloo", "Brick Lane", 6),
            DestinationTicket("Buckingham Palace", "The Charterhouse", 7),
            DestinationTicket("Baker Street", "Elephant & Castle", 8),
        ]
        random.shuffle(self.destination_deck)

    def draw_destination_tickets(
        self, count: int = 3
    ) -> list[DestinationTicket]:
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

    def _dfs(
        self, player: Player, current: str, target: str, visited: set
    ) -> bool:
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
        graph: dict[str, list[tuple[str, int, int]]] = {}
        owned_routes: list[tuple[int, Route]] = [
            (idx, route)
            for idx, route in enumerate(self.routes)
            if route.owner_player == player
        ]

        for route_id, route in owned_routes:
            graph.setdefault(route.city_a, []).append(
                (route.city_b, route.length, route_id)
            )
            graph.setdefault(route.city_b, []).append(
                (route.city_a, route.length, route_id)
            )

        best = 0
        used_route_ids: set[int] = set()

        def dfs(city: str, total_length: int) -> None:
            nonlocal best
            best = max(best, total_length)
            for nxt, weight, route_id in graph.get(city, []):
                if route_id in used_route_ids:
                    continue
                used_route_ids.add(route_id)
                dfs(nxt, total_length + weight)
                used_route_ids.remove(route_id)

        for start_city in graph:
            dfs(start_city, 0)

        return best

    @staticmethod
    def _standings_key(player: Player) -> tuple[int, int, int, str]:
        return (
            player.score,
            player.completed_tickets,
            player.trains,
            player.name.lower(),
        )

    def _end_game(self) -> None:
        self.game_over = True
        self._calculate_destination_scores()

        route_lengths = {
            p: self._longest_route_length(p) for p in self.players
        }
        max_len = max(route_lengths.values(), default=0)
        for p, length in route_lengths.items():
            if length == max_len:
                p.score += 10

        self.final_standings = sorted(
            self.players,
            key=self._standings_key,
            reverse=True,
        )

        if self.on_game_end:
            self.on_game_end(route_lengths)