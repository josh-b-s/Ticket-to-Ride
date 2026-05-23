from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.classes.game import Game

from game.classes.destination_ticket import DestinationTicket
from game.classes.player import Player


class TicketService:
    def __init__(self, game: Game) -> None:
        self.game = game

    def build_destination_deck(self) -> None:
        self.game.destination_deck = [
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
        random.shuffle(self.game.destination_deck)

    def draw(self, count: int = 3) -> list[DestinationTicket]:
        drawn = []
        for _ in range(count):
            if self.game.destination_deck:
                drawn.append(self.game.destination_deck.pop())
        return drawn

    def keep_tickets(
        self,
        player: Player,
        chosen: list[DestinationTicket],
        drawn: list[DestinationTicket],
    ) -> tuple[bool, str]:
        if not chosen:
            return False, "You must keep at least 1 ticket."
        for ticket in chosen:
            player.destination_tickets.append(ticket)
        returned = [t for t in drawn if t not in chosen]
        self.game.destination_deck = returned + self.game.destination_deck
        return True, "Tickets chosen."