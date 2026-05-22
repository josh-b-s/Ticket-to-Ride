from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.classes.board import Board
    from game.classes.destination_ticket import DestinationTicket
    from game.classes.player import Player
    from game.classes.train_deck import TrainDeck


class GameState:
    def __init__(self) -> None:
        self.players: list[Player] = []
        self.board: Board | None = None
        self.train_deck: TrainDeck | None = None
        self.destination_deck: list[DestinationTicket] = []
        self.current_player_index: int = 0
        self.last_round_triggered: bool = False
        self.last_player_index: int | None = None
        self.game_over: bool = False
        self.final_standings: list[Player] = []
