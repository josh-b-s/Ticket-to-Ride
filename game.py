from player import Player
from board import Board
from route import Route


class Game:
    def __init__(self):
        self.players = []
        self.current_player_index = 0
        self.board = Board()

    @property
    def cities(self):
        return self.board.cities

    @property
    def routes(self):
        return self.board.routes

    def get_routes(self, city_a: str, city_b: str):
        return self.board.get_routes(city_a, city_b)

    def get_bounds(self):
        return self.board.get_bounds()

    def add_player(self, name: str):
        name = name.strip()
        if not name:
            return None
        if any(p.name.lower() == name.lower() for p in self.players):
            return None

        player = Player(name)
        self.players.append(player)
        return player

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

    def claim_route(self, route: Route):
        player = self.current_player()
        if player is None:
            return False, "No current player."

        if route.is_claimed():
            return False, "That route is already claimed."

        if player.trains < route.length:
            return False, "Not enough trains."

        route.claimed_by = player.name
        route.claimed_color = player.color or "black"
        player.trains -= route.length
        player.score += route.length
        self.next_player()
        return True, "Route claimed."