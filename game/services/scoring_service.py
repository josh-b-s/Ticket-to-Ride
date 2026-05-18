# scoring_service.py
from __future__ import annotations

from game.classes.player import Player
from game.services.game_state import GameState


class ScoringService:
    def __init__(self, state: GameState):
        self.state = state

    def calculate_destination_scores(self) -> None:
        for player in self.state.players:
            player.completed_tickets = 0
            for ticket in player.destination_tickets:
                if self.is_connected(player, ticket.city_a, ticket.city_b):
                    player.score += ticket.points
                    player.completed_tickets += 1
                else:
                    player.score -= ticket.points

    def is_connected(self, player: Player, start: str, end: str) -> bool:
        return self._dfs(player, start, end, set())

    def _dfs(self, player: Player, current: str, target: str, visited: set) -> bool:
        if current == target:
            return True

        visited.add(current)
        for route in self.state.board.routes:
            if route.owner_player != player:
                continue

            if route.city_a == current:
                nxt = route.city_b
            elif route.city_b == current:
                nxt = route.city_a
            else:
                continue

            if nxt not in visited and self._dfs(player, nxt, target, visited):
                return True

        return False

    def longest_route_length(self, player: Player) -> int:
        graph: dict[str, list[tuple[str, int, int]]] = {}
        owned_routes = [
            (idx, route)
            for idx, route in enumerate(self.state.board.routes)
            if route.owner_player == player
        ]

        for route_id, route in owned_routes:
            graph.setdefault(route.city_a, []).append((route.city_b, route.length, route_id))
            graph.setdefault(route.city_b, []).append((route.city_a, route.length, route_id))

        best = 0
        used_route_ids: set[int] = set()

        def dfs(city: str, total_length: int) -> None:
            nonlocal best
            best = max(best, total_length)
            for nxt, weight, route_id in graph.get(city, []):
                if route_id in used_route_ids:
                    continue
                used_route_ids.add(route_id)
                dfs(nxt, total_length + weight)
                used_route_ids.remove(route_id)

        for start_city in graph:
            dfs(start_city, 0)

        return best