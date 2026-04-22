from player import Player
from board import Board
from route import Route
from train_deck import TrainDeck
from destination_ticket import DestinationTicket
import random


class Game:
    ROUTE_POINTS = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}

    def __init__(self):
        self.players = []
        self.current_player_index = 0
        self.board = Board()
        self.train_deck = TrainDeck()
        self.destination_deck = []
        self.last_round_triggered = False
        self.last_player_index = None

    @property
    def cities(self): return self.board.cities

    @property
    def routes(self): return self.board.routes

    def get_routes(self, city_a, city_b): return self.board.get_routes(city_a, city_b)
    def get_bounds(self): return self.board.get_bounds()

    def add_player(self, name):
        name = name.strip()
        if not name or any(p.name.lower() == name.lower() for p in self.players):
            return None
        player = Player(name)
        self.players.append(player)
        return player

    def get_players(self): return self.players

    def start(self):
        if len(self.players) < 2:
            raise ValueError("At least 2 players are required.")

        self.board = Board()
        self.train_deck = TrainDeck()
        self.current_player_index = 0
        self.last_round_triggered = False
        self.last_player_index = None

        for p in self.players:
            p.score = 0
            p.trains = 45
            p.train_cards.clear()
            p.destination_tickets.clear()

        self.build_destination_deck()
        self.deal_initial_tickets()
        self.deal_initial_train_cards()

    def deal_initial_train_cards(self):
        for p in self.players:
            for _ in range(4):
                card = self.train_deck.draw()
                if card:
                    p.train_cards.append(card)

    def current_player(self):
        return self.players[self.current_player_index] if self.players else None

    def next_player(self):
        if not self.players:
            return
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.last_round_triggered and self.current_player_index == self.last_player_index:
            self.end_game()

    def draw_train_card_from_deck(self, player):
        card = self.train_deck.draw()
        if card:
            player.train_cards.append(card)
        return card

    def draw_train_card_from_face_up(self, player, index):
        card = self.train_deck.draw_face_up(index)
        if card:
            player.train_cards.append(card)
        return card

    def select_cards_for_route(self, player, route, chosen_color=None):
        required_color = route.color if route.color is not None else chosen_color
        if required_color is None:
            return None

        chosen = [c for c in player.train_cards if c.color == required_color]
        if len(chosen) >= route.length:
            return chosen[:route.length]

        chosen.extend(c for c in player.train_cards if c.is_locomotive())
        return chosen[:route.length] if len(chosen) >= route.length else None

    def remove_cards_from_hand(self, player, cards):
        for card in cards:
            player.train_cards.remove(card)

    def claim_route(self, route: Route, chosen_color=None):
        player = self.current_player()
        if player is None:
            return False, "No current player."
        if route.is_claimed():
            return False, "That route is already claimed."

        same_routes = [r for r in self.routes if {r.city_a, r.city_b} == {route.city_a, route.city_b}]
        if len(self.players) <= 3 and any(r.is_claimed() for r in same_routes):
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

        if player.trains <= 2 and not self.last_round_triggered:
            self.last_round_triggered = True
            self.last_player_index = self.current_player_index

        self.next_player()
        return True, "Route claimed."

    def build_destination_deck(self):
        self.destination_deck = [
            DestinationTicket("King's Cross", "Waterloo", 5),
            DestinationTicket("Baker Street", "Big Ben", 5),
            DestinationTicket("Regent's Park", "Tower of London", 8),
            DestinationTicket("Hyde Park", "Brick Lane", 7),
            DestinationTicket("Buckingham Palace", "Elephant & Castle", 6),
            DestinationTicket("Covent Garden", "St Paul's", 4),
        ]
        random.shuffle(self.destination_deck)

    def deal_initial_tickets(self):
        for p in self.players:
            for _ in range(2):
                if self.destination_deck:
                    p.destination_tickets.append(self.destination_deck.pop())

    def calculate_destination_scores(self):
        for player in self.players:
            for ticket in player.destination_tickets:
                player.score += ticket.points if self.is_connected(player, ticket.city_a, ticket.city_b) else -ticket.points

    def is_connected(self, player, start, end):
        return self._dfs(player, start, end, set())

    def _dfs(self, player, current, target, visited):
        if current == target:
            return True
        visited.add(current)

        for route in self.routes:
            if route.owner_player != player:
                continue
            next_city = route.city_b if route.city_a == current else route.city_a if route.city_b == current else None
            if next_city and next_city not in visited and self._dfs(player, next_city, target, visited):
                return True
        return False

    def end_game(self):
        self.calculate_destination_scores()
        winner = max(self.players, key=lambda p: p.score)
        print("Game Over!")
        print(f"Winner: {winner.name} with {winner.score} points")