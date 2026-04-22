from player import Player
from board import Board
from route import Route


class Game:
    ROUTE_POINTS = {
        1: 1,
        2: 2,
        3: 4,
        4: 7,
        5: 10,
        6: 15,
    }

    def __init__(self):
        self.players = []
        self.current_player_index = 0
        self.board = Board()
        self.last_round_triggered = False
        self.last_player_index = None

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

        if not self.can_claim_route(player, route):
            return False, "Not enough cards."

        if player.trains < route.length:
            return False, "Not enough trains."

        same_routes = [
            r for r in self.routes
            if {r.city_a, r.city_b} == {route.city_a, route.city_b}
        ]

        if len(self.players) <= 3:
            if any(r.is_claimed() for r in same_routes):
                return False, "Route blocked in 2–3 player game."

        route.owner_player = player
        player.trains -= route.length
        player.score += self.ROUTE_POINTS.get(route.length, route.length)
        self.next_player()
        return True, "Route claimed."

    def can_claim_route(self, player, route):
        # TODO: check cards
        return True