# turn_manager.py
from __future__ import annotations

from game_state import GameState


class TurnManager:
    def __init__(self, state: GameState):
        self.state = state

    def current_player(self):
        if not self.state.players:
            return None
        return self.state.players[self.state.current_player_index]

    def next_player(self) -> None:
        if not self.state.players:
            return

        self.state.current_player_index = (
            self.state.current_player_index + 1
        ) % len(self.state.players)

        if (
            self.state.last_round_triggered
            and self.state.current_player_index == self.state.last_player_index
        ):
            self.state.game_over = True