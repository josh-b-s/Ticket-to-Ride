# game.py
from __future__ import annotations

from board import Board
from card_service import CardService
from game_state import GameState
from move_validator import ValidationResult
from player import Player
from route_service import RouteService
from scoring_service import ScoringService
from ticket_service import TicketService
from train_deck import TrainDeck
from turn_manager import TurnManager


class Game:
    def __init__(self):
        self.state = GameState()
        self.state.board = Board()

        self.turns = TurnManager(self.state)
        self.cards = CardService(self.state)
        self.tickets = TicketService(self.state)
        self.scoring = ScoringService(self.state)
        self.routes_service = RouteService(self.state, self.cards, self.turns)

        self.on_game_end = None

    @property
    def train_deck(self):
        return self.state.train_deck

    @train_deck.setter
    def train_deck(self, value):
        self.state.train_deck = value

    @property
    def players(self):
        return self.state.players

    @property
    def cities(self):
        return self.state.board.cities

    @property
    def routes(self):
        return self.state.board.routes

    @property
    def destination_deck(self):
        return self.state.destination_deck

    @destination_deck.setter
    def destination_deck(self, value):
        self.state.destination_deck = value

    @property
    def game_over(self):
        return self.state.game_over

    @game_over.setter
    def game_over(self, value):
        self.state.game_over = value

    @property
    def final_standings(self):
        return self.state.final_standings

    @final_standings.setter
    def final_standings(self, value):
        self.state.final_standings = value

    def get_players(self):
        return self.state.players

    def get_routes(self, city_a: str, city_b: str):
        return self.state.board.get_routes(city_a, city_b)

    def get_bounds(self):
        return self.state.board.get_bounds()

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

    def current_player(self):
        return self.turns.current_player()

    def next_player(self):
        self.turns.next_player()
        if self.state.game_over:
            self._end_game()

    def draw_train_card_from_deck(self, player):
        return self.cards.draw_from_deck(player)

    def draw_train_card_from_face_up(self, player, index):
        return self.cards.draw_from_face_up(player, index)

    def available_colors_for_gray_route(self, player, route_length):
        return self.cards.available_colors_for_gray_route(player, route_length)

    def claim_route(self, route, chosen_color=None) -> ValidationResult:
        return self.routes_service.claim_route(route, chosen_color)

    def draw_destination_tickets(self, count=3):
        return self.tickets.draw(count)

    def keep_destination_tickets(self, player, chosen, drawn, advance_turn=True):
        ok, reason = self.tickets.keep_tickets(player, chosen, drawn, advance_turn)
        if advance_turn:
            self.turns.next_player()
        return ok, reason

    def _end_game(self) -> None:
        self.state.game_over = True
        self.scoring.calculate_destination_scores()

        route_lengths = {
            p: self.scoring.longest_route_length(p) for p in self.state.players
        }
        max_len = max(route_lengths.values(), default=0)
        for p, length in route_lengths.items():
            if length == max_len:
                p.score += 10

        self.state.final_standings = sorted(
            self.state.players,
            key=lambda p: (p.score, p.completed_tickets, -p.trains, p.name.lower()),
            reverse=True,
        )

        if self.on_game_end:
            self.on_game_end(route_lengths)

