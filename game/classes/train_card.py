class TrainCard:
    COLORS = ["red", "blue", "green", "yellow", "black", "orange", "pink"]

    def __init__(self, color: str) -> None:
        if color not in self.COLORS and color != "locomotive":
            raise ValueError(f"Invalid color: {color!r}")
        self.color = color

    def is_locomotive(self) -> bool:
        return self.color == "locomotive"

    def __str__(self) -> str:
        return f"{self.color.title()} Card"

    def __repr__(self) -> str:
        return f"TrainCard({self.color!r})"
