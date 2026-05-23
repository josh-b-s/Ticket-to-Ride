from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.classes.game import Game


class TurnManager:
    def __init__(self, game: Game) -> None:
        self.game = game

    def current_player(self):
        if not self.game.players:
            return None
        return self.game.players[self.game.current_player_index]

    def next_player(self) -> None:
        """Advance the turn index only.

        Last-round detection and _end_game() are handled by Game.next_player
        so scoring always runs before game_over is set.
        """
        if not self.game.players:
            return
        self.game.current_player_index = (
            self.game.current_player_index + 1
        ) % len(self.game.players)