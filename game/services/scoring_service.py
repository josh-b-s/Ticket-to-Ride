from __future__ import annotations

from game.classes.player import Player
from game.services.game_state import GameState

_LONGEST_ROUTE_BONUS = 10


class ScoringService:
    def __init__(self, state: GameState) -> None:
        self.state = state

    def calculate_destination_scores(self) -> None:
        """Add or subtract ticket points for every player."""
        for player in self.state.players:
            player.completed_tickets = 0
            for ticket in player.destination_tickets:
                if self._is_connected(player, ticket.city_a, ticket.city_b):
                    player.score += ticket.points
                    player.completed_tickets += 1
                else:
                    player.score -= ticket.points

    def apply_longest_route_bonus(self, bonus: int = _LONGEST_ROUTE_BONUS) -> dict[Player, int]:
        """
        Award *bonus* points to the player(s) with the longest continuous
        route.  Returns a ``{player: route_length}`` mapping (needed by the
        end-game display).

        Keeping this here rather than in ``Game._end_game`` means all
        scoring logic lives in one service.
        """
        route_lengths = {p: self.longest_route_length(p) for p in self.state.players}
        max_len = max(route_lengths.values(), default=0)
        for player, length in route_lengths.items():
            if length == max_len:
                player.score += bonus
        return route_lengths

    def is_connected(self, player: Player, start: str, end: str) -> bool:
        return self._is_connected(player, start, end)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _is_connected(self, player: Player, start: str, end: str) -> bool:
        return self._dfs(player, start, end, visited=set())

    def _dfs(self, player: Player, current: str, target: str, visited: set) -> bool:
        if current == target:
            return True
        visited.add(current)
        for route in self.state.board.routes:
            if route.owner_player is not player:
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
        """Return the length of the player's longest continuous route chain."""
        graph: dict[str, list[tuple[str, int, int]]] = {}
        owned = [
            (idx, r)
            for idx, r in enumerate(self.state.board.routes)
            if r.owner_player is player
        ]
        for route_id, route in owned:
            graph.setdefault(route.city_a, []).append((route.city_b, route.length, route_id))
            graph.setdefault(route.city_b, []).append((route.city_a, route.length, route_id))

        best: int = 0
        used: set[int] = set()

        def dfs(city: str, total: int) -> None:
            nonlocal best
            best = max(best, total)
            for nxt, weight, route_id in graph.get(city, []):
                if route_id not in used:
                    used.add(route_id)
                    dfs(nxt, total + weight)
                    used.remove(route_id)

        for start in graph:
            dfs(start, 0)

        return best
