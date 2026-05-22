from __future__ import annotations

from typing import Callable

from game.classes.board import Board
from game.classes.player import Player
from game.classes.train_deck import TrainDeck
from game.services.card_service import CardService
from game.services.game_state import GameState
from game.services.move_validator import ValidationResult
from game.services.route_service import RouteService
from game.services.scoring_service import ScoringService
from game.services.ticket_service import TicketService
from game.services.turn_manager import TurnManager


class Game:
    """
    Facade over the game services.

    Exposes only *actions* and lightweight *queries*.  Raw state is on
    ``game.state``; the board is accessible via the ``game.board`` shortcut
    (one hop, not two) so UI code stays readable without needing 14 proxies.

    Removed proxies compared to the original:
      - players, cities, routes, train_deck, destination_deck,
        game_over, final_standings  →  access via game.state directly.
    Kept as properties:
      - board  →  game.state.board  (map view needs this frequently enough
                  that game.state.board.cities is an unwanted chain).
    """

    def __init__(self) -> None:
        self.state = GameState()
        self.state.board = Board()

        self.turns = TurnManager(self.state)
        self.cards = CardService(self.state)
        self.tickets = TicketService(self.state)
        self.scoring = ScoringService(self.state)
        self.routes_service = RouteService(self.state, self.cards, self.turns)

        self.on_game_end: Callable | None = None

    #  Single-hop shortcut (not a full proxy) 

    @property
    def board(self):
        return self.state.board

    #  Queries 

    def get_players(self) -> list[Player]:
        return self.state.players

    def current_player(self) -> Player | None:
        return self.turns.current_player()

    def get_routes(self, city_a: str, city_b: str):
        return self.state.board.get_routes(city_a, city_b)

    def get_bounds(self) -> tuple[int, int, int, int]:
        return self.state.board.get_bounds()

    def get_face_up_cards(self):
        return self.state.train_deck.get_face_up()

    #  Setup 

    def reset_players(self) -> None:
        """Clear the player list before a new setup phase."""
        self.state.players.clear()

    def add_player(self, name: str) -> Player | None:
        name = name.strip()
        if not name or any(p.name.lower() == name.lower() for p in self.state.players):
            return None
        player = Player(name)
        self.state.players.append(player)
        return player

    def start(self) -> None:
        if len(self.state.players) < 2:
            raise ValueError("At least 2 players are required.")

        self.state.board = Board()
        self.state.train_deck = TrainDeck()
        self.state.current_player_index = 0
        self.state.last_round_triggered = False
        self.state.last_player_index = None
        self.state.game_over = False
        self.state.final_standings = []

        for p in self.state.players:
            p.score = 0
            p.trains = 45
            p.train_cards.clear()
            p.destination_tickets.clear()
            p.completed_tickets = 0

        self.tickets.build_destination_deck()

        for p in self.state.players:
            for _ in range(4):
                card = self.state.train_deck.draw()
                if card:
                    p.train_cards.append(card)

    #  Turn flow 

    def next_player(self) -> None:
        """Advance to the next player and trigger end-game if appropriate."""
        if not self.state.players:
            return
        self.turns.next_player()
        if (
                self.state.last_round_triggered
                and self.state.current_player_index == self.state.last_player_index
                and not self.state.game_over
        ):
            self._end_game()

    #  Actions 

    def draw_train_card_from_deck(self, player: Player):
        return self.cards.draw_from_deck(player)

    def draw_train_card_from_face_up(self, player: Player, index: int):
        return self.cards.draw_from_face_up(player, index)

    def available_colors_for_gray_route(self, player: Player, route_length: int) -> list[str]:
        return self.cards.available_colors_for_gray_route(player, route_length)

    def claim_route(self, route, chosen_color: str | None = None) -> ValidationResult:
        """Claim a route and advance the turn on success."""
        result = self.routes_service.claim_route(route, chosen_color)
        if result.ok:
            self.next_player()
        return result

    def draw_destination_tickets(self, count: int = 3):
        return self.tickets.draw(count)

    def keep_destination_tickets(
            self, player: Player, chosen, drawn, advance_turn: bool = True
    ):
        ok, reason = self.tickets.keep_tickets(player, chosen, drawn)
        if advance_turn:
            self.next_player()
        return ok, reason

    #  End game 

    def _standings_key(self, player: Player) -> tuple:
        return (player.score, player.completed_tickets, -player.trains, player.name.lower())

    def _end_game(self) -> None:
        self.state.game_over = True
        self.scoring.calculate_destination_scores()
        route_lengths = self.scoring.apply_longest_route_bonus()  # all scoring in one service
        self.state.final_standings = sorted(
            self.state.players, key=self._standings_key, reverse=True
        )
        if self.on_game_end:
            self.on_game_end(route_lengths)
