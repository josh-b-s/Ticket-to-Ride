from __future__ import annotations

from pathlib import Path
from typing import Callable

from game.classes.board import Board
from game.classes.destination_deck import DestinationDeck
from game.classes.player import Player
from game.classes.train_deck import TrainDeck
from game.services.card_service import CardService
from game.services.move_validator import ValidationResult
from game.services.route_service import RouteService
from game.services.scoring_service import ScoringService
from game.services.ticket_service import TicketService
from game.services.turn_manager import TurnManager


class Game:
    """
    Facade over the game services.

    All mutable state lives directly on this class. Services receive a
    reference to Game and read/write fields via self.game.xyz.
    """

    def __init__(self) -> None:
        # --- State ---
        self.players:               list[Player]      = []
        self.board:                 Board | None      = None
        self.train_deck:            TrainDeck | None  = None
        self.destination_deck:      DestinationDeck   = DestinationDeck()
        self.map_folder:            Path | None       = None
        self.current_player_index:  int               = 0
        self.last_round_triggered:  bool              = False
        self.last_player_index:     int | None        = None
        self.game_over:             bool              = False
        self.final_standings:       list[Player]      = []

        # --- Services ---
        self._turns          = TurnManager(self)
        self._cards          = CardService(self)
        self._tickets        = TicketService(self)
        self._scoring        = ScoringService(self)
        self._routes_service = RouteService(self)

        self.on_game_end: Callable | None = None

    # --- Queries ---

    def get_players(self) -> list[Player]:
        return self.players

    def current_player(self) -> Player | None:
        return self._turns.current_player()

    def get_bounds(self) -> tuple[int, int, int, int]:
        return self.board.get_bounds()

    def get_face_up_cards(self):
        return self.train_deck.get_face_up()

    # --- Setup ---

    def reset_players(self) -> None:
        self.players.clear()

    def add_player(self, name: str) -> Player | None:
        name = name.strip()
        if not name or any(
            p.name.lower() == name.lower() for p in self.players
        ):
            return None
        player = Player(name)
        self.players.append(player)
        return player

    def start(self, map_folder: Path) -> None:
        if len(self.players) < 2:
            raise ValueError("At least 2 players are required.")

        self.map_folder       = map_folder
        self.board            = Board(str(map_folder / "board.json"))
        self.train_deck       = TrainDeck()
        self.destination_deck = DestinationDeck()

        self.current_player_index = 0
        self.last_round_triggered = False
        self.last_player_index    = None
        self.game_over            = False
        self.final_standings      = []

        self._tickets.build_destination_deck()

        for p in self.players:
            for _ in range(2):
                card = self.train_deck.draw()
                if card:
                    p.train_cards.append(card)

    # --- Turn flow ---

    def next_player(self) -> None:
        if not self.players:
            return
        self._turns.next_player()
        if (
            self.last_round_triggered
            and self.current_player_index == self.last_player_index
            and not self.game_over
        ):
            self._end_game()

    # --- Actions ---

    def return_tickets_to_deck(self, tickets: list) -> None:
        self.destination_deck.return_to_bottom(tickets)

    def draw_train_card_from_deck(self, player: Player):
        return self._cards.draw_from_deck(player)

    def draw_train_card_from_face_up(self, player: Player, index: int):
        return self._cards.draw_from_face_up(player, index)

    def available_colors_for_gray_route(
        self, player: Player, route_length: int
    ) -> list[str]:
        return self._cards.available_colors_for_gray_route(player, route_length)

    def claim_route(
        self, route, chosen_color: str | None = None
    ) -> ValidationResult:
        result = self._routes_service.claim_route(route, chosen_color)
        if result.ok:
            self.next_player()
        return result

    def draw_destination_tickets(self, count: int = 2):
        return self._tickets.draw(count)

    def keep_destination_tickets(
        self, player: Player, chosen, drawn, advance_turn: bool = True
    ) -> None:
        self._tickets.keep_tickets(player, chosen, drawn)
        if advance_turn:
            self.next_player()

    # --- End game ---

    def standings_key(self, player: Player) -> tuple:
        """Sort key: score, completed tickets, trains used, name."""
        return (
            player.score,
            player.completed_tickets,
            -player.trains,
            player.name.lower(),
        )

    def _end_game(self) -> None:
        self.game_over = True
        self._scoring.calculate_destination_scores()
        route_lengths = self._scoring.apply_longest_route_bonus()
        self.final_standings = sorted(
            self.players, key=self.standings_key, reverse=True
        )
        if self.on_game_end:
            self.on_game_end(route_lengths)