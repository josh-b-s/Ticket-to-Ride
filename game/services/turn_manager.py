# turn_manager.py
from __future__ import annotations

from game.services.game_state import GameState


class TurnManager:
    def __init__(self, state: GameState):
        self.state = state

    def current_player(self):
        if not self.state.players:
            return None
        return self.state.players[self.state.current_player_index]

    def next_player(self) -> None:
        """Advance the turn index only.

        Last-round detection and _end_game() are deliberately handled by
        Game.next_player() so that scoring always runs before game_over is set.
        This method must not set game_over itself.
        """
        if not self.state.players:
            return
        self.state.current_player_index = (
            self.state.current_player_index + 1
        ) % len(self.state.players)