"""board.py — loads map data from JSON and generates destination tickets."""
from __future__ import annotations

import heapq
import json
import random
from typing import Any

from game.classes.destination_ticket import DestinationTicket
from game.classes.route import Route, RouteColor

# Tickets whose shortest-path distance falls below this are too trivial.
_MIN_TICKET_DISTANCE = 5
# How many tickets to generate per game session.
_TICKET_COUNT = 20


class Board:
    def __init__(self, path: str = "board.json") -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.cities: dict[str, tuple[Any, ...]] = {
            name: tuple(coords) for name, coords in data["cities"].items()
        }
        self.routes: list[Route] = [
            self._parse_route(r) for r in data["routes"]
        ]

    #  Parsing 

    @staticmethod
    def _parse_route(r: dict) -> Route:
        color_name = r.get("color", "GRAY").upper()
        try:
            color = RouteColor[color_name]
        except KeyError:
            raise ValueError(
                f"Unknown route color {color_name!r} in board data."
            )
        return Route(
            r["a"], r["b"], r["length"], color,
            ferry_locos=r.get("ferry_locos", 0),
        )

    #  Queries 

    def get_routes(self, city_a: str, city_b: str) -> list[Route]:
        return [r for r in self.routes if r.connects(city_a, city_b)]

    def get_bounds(self) -> tuple[int, int, int, int]:
        xs = [x for x, _ in self.cities.values()]
        ys = [y for _, y in self.cities.values()]
        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)

    #  Ticket generation 

    def generate_tickets(
        self,
        min_distance: int = _MIN_TICKET_DISTANCE,
        count: int = _TICKET_COUNT,
    ) -> list[DestinationTicket]:
        """
        Auto-generate destination tickets from the board's city graph.

        Algorithm:
        1. Compute all-pairs shortest paths using Dijkstra, weighting edges
           by route length (the minimum-length route between two cities).
        2. Produce one candidate ticket per city pair whose shortest-path
           distance is at least *min_distance*.
        3. Set the ticket's point value equal to that distance — pairs that
           are harder to connect across the map are worth more.
        4. Shuffle and return up to *count* tickets.

        This means adding a new city to board.json automatically produces
        appropriate tickets on the next game start with no code changes.
        """
        distances = self._all_pairs_shortest_paths()
        cities = list(self.cities.keys())

        candidates: list[DestinationTicket] = []
        for i, city_a in enumerate(cities):
            for city_b in cities[i + 1:]:
                dist = distances[city_a].get(city_b, float("inf"))
                if dist >= min_distance:
                    candidates.append(
                        DestinationTicket(city_a, city_b, int(dist))
                    )

        random.shuffle(candidates)
        return candidates[:count]

    def _all_pairs_shortest_paths(self) -> dict[str, dict[str, float]]:
        """
        Run Dijkstra from every city.

        Parallel routes between the same city pair contribute the
        minimum-length edge for pathfinding purposes.
        """
        # Build adjacency list: city → [(neighbour, weight)]
        graph: dict[str, list[tuple[str, int]]] = {
            city: [] for city in self.cities
        }
        for route in self.routes:
            graph[route.city_a].append((route.city_b, route.length))
            graph[route.city_b].append((route.city_a, route.length))

        all_distances: dict[str, dict[str, float]] = {}

        for source in self.cities:
            dist: dict[str, float] = {
                city: float("inf") for city in self.cities
            }
            dist[source] = 0
            heap: list[tuple[float, str]] = [(0, source)]

            while heap:
                d, u = heapq.heappop(heap)
                if d > dist[u]:
                    continue
                for v, weight in graph[u]:
                    candidate = dist[u] + weight
                    if candidate < dist[v]:
                        dist[v] = candidate
                        heapq.heappush(heap, (candidate, v))

            all_distances[source] = dist

        return all_distances