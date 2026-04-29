import math
import tkinter as tk

_END_GAP = 14  # gap at start/end of each route segment cluster
_MID_GAP = 6  # gap between individual segments
_ROUTE_OFFSET = 12  # lateral offset between parallel routes (scaled)


class MapView:
    def __init__(self, parent, game, on_route_click):
        self.parent = parent
        self.game = game
        self.on_route_click = on_route_click

        self.canvas = tk.Canvas(self.parent, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw() if e.width > 10 else None)

    # ---------------------------------------------------------------- public

    def draw(self) -> None:
        self.canvas.delete("all")
        scale, ox, oy = self._get_transform()
        self._draw_routes(scale, ox, oy)
        self._draw_cities(scale, ox, oy)

    # -------------------------------------------------------------- transform

    def _get_transform(self) -> tuple[float, float, float]:
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        min_x, min_y, map_w, map_h = self.game.get_bounds()
        padding = max(80, int(min(w, h) * 0.2))
        scale = min((w - padding) / map_w, (h - padding) / map_h)
        ox = (w - map_w * scale) / 2 - min_x * scale
        oy = (h - map_h * scale) / 2 - min_y * scale
        return scale, ox, oy

    def _scale_point(self, x: float, y: float, scale: float, ox: float, oy: float):
        return x * scale + ox, y * scale + oy

    # -------------------------------------------------------------- drawing

    def _draw_routes(self, scale: float, ox: float, oy: float) -> None:
        for idx, route in enumerate(self.game.routes):
            x1, y1 = self._scale_point(*self.game.cities[route.city_a], scale, ox, oy)
            x2, y2 = self._scale_point(*self.game.cities[route.city_b], scale, ox, oy)
            if x1 == x2 and y1 == y2:
                continue

            group = self._route_group(route)
            group_index = next(
                (i for i, (gi, _) in enumerate(group) if gi == idx), 0
            )
            offset = (group_index - (len(group) - 1) / 2) * (_ROUTE_OFFSET * scale)
            x1o, y1o, x2o, y2o = self._offset_line(x1, y1, x2, y2, offset)

            segments = self._segment_data(x1o, y1o, x2o, y2o, route.length)
            if not segments:
                continue

            color = self._route_color(route)
            tag = f"route_{idx}"

            for sx, sy, ex, ey in segments:
                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill="", width=max(18, int(20 * scale)),
                    capstyle="round", tags=(tag,)
                )
            for sx, sy, ex, ey in segments:
                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill=color, width=max(10, int(10 * scale)),
                    capstyle="butt", tags=(tag,)
                )

            self.canvas.tag_bind(
                tag, "<Button-1>", lambda e, r=route: self.on_route_click(r)
            )

    def _draw_cities(self, scale: float, ox: float, oy: float) -> None:
        for city, (cx, cy) in self.game.cities.items():
            x, y = self._scale_point(cx, cy, scale, ox, oy)
            r = max(4, int(9 * scale))
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r, fill="black", outline="white"
            )
            self._draw_outlined_text(
                x, y - 14 * scale, city,
                font=("Arial", max(6, int(6 * scale)), "bold"),
            )

    def _draw_outlined_text(
            self, x: float, y: float, text: str, font, fill: str = "black", outline: str = "white"
    ) -> None:
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]:
            self.canvas.create_text(x + dx, y + dy, text=text, font=font, fill=outline)
        self.canvas.create_text(x, y, text=text, font=font, fill=fill)

    # -------------------------------------------------------------- helpers

    def _route_group(self, route) -> list:
        key = tuple(sorted([route.city_a, route.city_b]))
        return [
            (i, r) for i, r in enumerate(self.game.routes)
            if tuple(sorted([r.city_a, r.city_b])) == key
        ]

    def _route_color(self, route) -> str:
        if route.is_claimed():
            return route.owner_player.color or "black"
        return route.color or "lightgray"

    @staticmethod
    def _offset_line(x1, y1, x2, y2, offset) -> tuple:
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return x1, y1, x2, y2
        px, py = -dy / length, dx / length
        return x1 + px * offset, y1 + py * offset, x2 + px * offset, y2 + py * offset

    @staticmethod
    def _segment_data(x1o, y1o, x2o, y2o, route_length: int) -> list:
        dx, dy = x2o - x1o, y2o - y1o
        length = math.hypot(dx, dy)
        if length == 0:
            return []

        ux, uy = dx / length, dy / length
        usable = length - (2 * _END_GAP) - (_MID_GAP * (route_length - 1))
        if usable <= 0:
            return []

        seg_len = usable / route_length
        segments = []
        t = _END_GAP
        for _ in range(route_length):
            sx, sy = x1o + ux * t, y1o + uy * t
            ex, ey = x1o + ux * (t + seg_len), y1o + uy * (t + seg_len)
            segments.append((sx, sy, ex, ey))
            t += seg_len + _MID_GAP
        return segments
