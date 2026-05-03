from __future__ import annotations


class Player:
    def __init__(self, name: str):
        self.name = name
        self.score: int = 0
        self.trains: int = 45
        self.train_cards: list = []
        self.destination_tickets: list = []
        self.color: str | None = None
        self.stations: int = 3
        self.completed_tickets: int = 0

    def __str__(self) -> str:
        return f"{self.name}  |  Score: {self.score}  |  Trains: {self.trains}"

    def __repr__(self) -> str:
        return f"Player({self.name!r})"

    def card_color_summary(self) -> list[str]:
        """Return distinct non-locomotive colors in hand (sorted)."""
        colors = {card.color for card in self.train_cards if card.color != "locomotive"}
        return sorted(colors)
