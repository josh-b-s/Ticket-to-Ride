from dataclasses import dataclass


@dataclass
class DestinationTicket:
    city_a: str
    city_b: str
    points: int

    def __str__(self) -> str:
        return f"{self.city_a} \u2192 {self.city_b} ({self.points} pts)"