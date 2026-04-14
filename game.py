from player import Player
from route import Route


class Game:
    def __init__(self):
        self.players = []
        self.current_player_index = 0

        self.cities = {
            "King's Cross": (200, 50),
            "Regent's Park": (100, 50),
            "Baker Street": (40, 100),
            "The Charterhouse": (300, 100),
            "Brick Lane": (450, 110),
            "British Museum": (200, 140),
            "St Paul's": (340, 170),
            "Tower of London": (460, 220),
            "Piccadilly Circus": (150, 200),
            "Covent Garden": (220, 200),
            "Trafalgar Square": (200, 250),
            "Globe Theatre": (350, 240),
            "Waterloo": (270, 260),
            "Hyde Park": (60, 270),
            "Buckingham Palace": (120, 300),
            "Big Ben": (220, 300),
            "Elephant & Castle": (340, 330),
        }

        self.routes = [
            Route("Regent's Park", "Baker Street", 2, "blue"),
            Route("Waterloo", "Big Ben", 1, "blue"),
            Route("The Charterhouse", "British Museum", 4, "blue"),
            Route("Brick Lane", "Tower of London", 3, "blue"),

            Route("King's Cross", "Regent's Park", 3, "green"),
            Route("Buckingham Palace", "Big Ben", 2, "green"),
            Route("Globe Theatre", "Elephant & Castle", 2, "green"),
            Route("Brick Lane", "The Charterhouse", 3, "green"),


            Route("King's Cross", "British Museum", 2, "black"),
            Route("Baker Street", "Hyde Park", 4, "black"),
            Route("The Charterhouse", "St Paul's", 1, "black"),
            Route("Tower of London", "Elephant & Castle", 4, "black"),


            Route("Regent's Park", "British Museum", 3, "yellow"),
            Route("Big Ben", "Elephant & Castle", 3, "yellow"),


            Route("Baker Street", "British Museum", 4, "orange"),
            Route("Waterloo", "Elephant & Castle", 2, "orange"),
            Route("Brick Lane", "St Paul's", 3, "orange"),


            Route("Buckingham Palace", "Piccadilly Circus", 2, "pink"),
            Route("Waterloo", "Globe Theatre", 2, "pink"),
            Route("The Charterhouse", "King's Cross", 3, "pink"),


            Route("Baker Street", "Piccadilly Circus", 4),
            Route("Buckingham Palace", "Trafalgar Square", 2),
            Route("Piccadilly Circus", "British Museum", 2),
            Route("Trafalgar Square", "Waterloo", 2),
            Route("Trafalgar Square", "Big Ben", 1),
            Route("Globe Theatre", "Tower of London", 3),


            Route("Hyde Park", "Piccadilly Circus", 2),
            Route("Hyde Park", "Piccadilly Circus", 2, "blue"), 

            Route("Hyde Park", "Buckingham Palace", 1, "orange"),
            Route("Hyde Park", "Buckingham Palace", 1, "yellow"), 

            Route("Piccadilly Circus", "Covent Garden", 1, "green"),
            Route("Piccadilly Circus", "Covent Garden", 1, "yellow"), 

            Route("Piccadilly Circus", "Trafalgar Square", 1, "blue"),
            Route("Piccadilly Circus", "Trafalgar Square", 1, "orange"), 

            Route("Covent Garden", "British Museum", 1),
            Route("Covent Garden", "British Museum", 1),

            Route("Covent Garden", "Trafalgar Square", 1, "black"),
            Route("Covent Garden", "Trafalgar Square", 1, "pink"), 

            Route("Globe Theatre", "St Paul's", 1),
            Route("Globe Theatre", "St Paul's", 1), 

            Route("St Paul's", "Tower of London", 3, "yellow"),
            Route("St Paul's", "Tower of London", 3, "pink"), 

            Route("St Paul's", "Covent Garden", 3),
            Route("St Paul's", "Covent Garden", 3),
        ]

    def add_player(self, name: str):
        name = name.strip()
        if not name:
            return False
        if any(p.name.lower() == name.lower() for p in self.players):
            return False
        self.players.append(Player(name))
        return True

    def get_players(self):
        return self.players

    def start(self):
        if len(self.players) < 2:
            raise ValueError("At least 2 players are required.")
        self.current_player_index = 0

    def current_player(self):
        if not self.players:
            return None
        return self.players[self.current_player_index]

    def next_player(self):
        if self.players:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def get_routes(self, city_a: str, city_b: str):
        return [
            r for r in self.routes
            if r.connects(city_a, city_b)
        ]

    def claim_route(self, route: Route):
        player = self.current_player()
        if player is None:
            return False, "No current player."

        if route.is_claimed():
            return False, "That route is already claimed."

        if player.trains < route.length:
            return False, "Not enough trains."

        route.claimed_by = player.name
        player.trains -= route.length
        player.score += route.length
        self.next_player()
        return True, "Route claimed."