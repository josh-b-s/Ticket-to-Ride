class DestinationTicket:
    def __init__(self, city_a: str, city_b: str, points: int, is_long: bool = False):
        self.city_a = city_a
        self.city_b = city_b
        self.points = points
        self.is_long = is_long

    def __str__(self):
        type_label = "Long" if self.is_long else "Short"
        return f"{self.city_a} → {self.city_b} ({self.points}) [{type_label}]"

    def __repr__(self):
        return (
            f"DestinationTicket({self.city_a!r}, {self.city_b!r}, "
            f"{self.points!r}, is_long={self.is_long!r})"
        )