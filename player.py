class Player:
    def __init__(self, name: str):
        self.name = name
        self.score = 0
        self.trains = 45
        self.cards = []
        self.tickets = []

    def __str__(self):
        return f"{self.name} | Score: {self.score} | Trains: {self.trains}"