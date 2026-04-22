from player import Player
from board import Board
from route import Route
from train_deck import TrainDeck


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
        self.train_deck = TrainDeck()

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

        self.board = Board()
        self.train_deck = TrainDeck()

        self.current_player_index = 0
        self.last_round_triggered = False
        self.last_player_index = None

        for player in self.players:
            player.score = 0
            player.trains = 45
            player.train_cards.clear()
            player.destination_tickets.clear()

        self.deal_initial_train_cards()

    def deal_initial_train_cards(self):
        for player in self.players:
            for _ in range(4):
                card = self.train_deck.draw()
                if card is not None:
                    player.train_cards.append(card)

    def current_player(self):
        if not self.players:
            return None
        return self.players[self.current_player_index]

    def next_player(self):
        if self.players:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def draw_train_card_from_deck(self, player):
        card = self.train_deck.draw()
        if card is None:
            return None

        player.train_cards.append(card)
        return card

    def draw_train_card_from_face_up(self, player, index):
        card = self.train_deck.draw_face_up(index)
        if card is None:
            return None

        player.train_cards.append(card)
        return card

    def select_cards_for_route(self, player, route, chosen_color=None):
        required_color = route.color if route.color is not None else chosen_color

        if required_color is None:
            return None

        chosen = []

        for card in player.train_cards:
            if card.color == required_color:
                chosen.append(card)
                if len(chosen) == route.length:
                    return chosen

        for card in player.train_cards:
            if card.is_locomotive():
                chosen.append(card)
                if len(chosen) == route.length:
                    return chosen

        return None

    def remove_cards_from_hand(self, player, cards):
        for card in cards:
            player.train_cards.remove(card)

    def claim_route(self, route: Route, chosen_color=None):
        player = self.current_player()
        if player is None:
            return False, "No current player."

        if route.is_claimed():
            return False, "That route is already claimed."

        same_routes = [
            r for r in self.routes
            if {r.city_a, r.city_b} == {route.city_a, route.city_b}
        ]

        if len(self.players) <= 3:
            if any(r.is_claimed() for r in same_routes):
                return False, "Route blocked in 2–3 player game."

        if player.trains < route.length:
            return False, "Not enough trains."

        cards = self.select_cards_for_route(player, route, chosen_color)
        if not cards:
            return False, "You do not have the required cards."

        self.remove_cards_from_hand(player, cards)
        self.train_deck.discard(cards)

        route.owner_player = player
        player.trains -= route.length
        player.score += self.ROUTE_POINTS.get(route.length, route.length)

        self.next_player()
        return True, "Route claimed."