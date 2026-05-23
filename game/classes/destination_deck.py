"""destination_deck.py — manages the destination ticket draw pile."""
from __future__ import annotations

import random

from game.classes.destination_ticket import DestinationTicket


class DestinationDeck:
    """
    Encapsulates the destination ticket pile.

    Mirrors TrainDeck's role for train cards: owns the draw and
    return logic so neither Game nor TicketService needs to manipulate
    a raw list directly.
    """

    def __init__(self) -> None:
        self._cards: list[DestinationTicket] = []

    #  Loading 

    def load(self, tickets: list[DestinationTicket]) -> None:
        """Replace the deck contents and shuffle."""
        self._cards = list(tickets)
        random.shuffle(self._cards)

    #  Drawing 

    def draw(self, count: int = 3) -> list[DestinationTicket]:
        """Draw up to *count* tickets from the top of the deck."""
        drawn = []
        for _ in range(count):
            if self._cards:
                drawn.append(self._cards.pop())
        return drawn

    #  Returning 

    def return_to_bottom(self, tickets: list[DestinationTicket]) -> None:
        """Place unchosen tickets at the bottom of the deck."""
        self._cards = tickets + self._cards

    #  Helpers 

    def __len__(self) -> int:
        return len(self._cards)

    def __bool__(self) -> bool:
        return bool(self._cards)