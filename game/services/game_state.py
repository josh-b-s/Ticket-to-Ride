# game_state.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GameState:
    def __init__(self):
        self.players = []
        self.board = None
        self.train_deck = None
        self.destination_deck = []
        self.current_player_index = 0
        self.last_round_triggered = False
        self.last_player_index = None
        self.game_over = False
        self.final_standings = []