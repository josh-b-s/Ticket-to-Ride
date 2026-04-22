class TrainCard:
    COLORS = [
        "red", "blue", "green", "yellow",
        "black", "orange", "pink", "white"
    ]

    def __init__(self, color: str):
        if color not in self.COLORS and color != "locomotive":
            raise ValueError(f"Invalid color: {color}")

        self.color = color

    def is_locomotive(self):
        return self.color == "locomotive"

    def __str__(self):
        return f"{self.color.title()} Card"
