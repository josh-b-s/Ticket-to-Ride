from dataclasses import dataclass


@dataclass
class DestinationTicket:
    city_a: str
    city_b: str
    points: int
    is_long: bool = False

    def __str__(self) -> str:
        kind = "Long" if self.is_long else "Short"
        return f"{self.city_a} → {self.city_b} ({self.points}) [{kind}]"
