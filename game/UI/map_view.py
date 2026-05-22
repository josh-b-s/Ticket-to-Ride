from __future__ import annotations

import math
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageEnhance, ImageTk

_ASSETS = Path(__file__).parent.parent
_END_GAP = 18
_MID_GAP = 6
_ROUTE_OFFSET = 12

_FERRY_MARKER_BG = "#0d2237"
_FERRY_MARKER_FG = "#e8f4fc"
_GRAY_SLOT = "#B0B0B3"

# Darker player colours for train pieces drawn on the map.
# Intentionally separate from theme._PLAYER_COLORS (which uses lighter
# One Dark palette tones for sidebar text/badges).
_TRAIN_PIECE_HEX: dict[str, str] = {
    "red": "#c01800",
    "yellow": "#c49200",
    "green": "#27862a",
    "black": "#2a2a2a",
    "blue": "#1966d2",
}


def _to_hex(color: str) -> str:
    return _TRAIN_PIECE_HEX.get(color.lower(), "#808080")


def _adjust(hex_color: str, factor: float) -> str:
    h = hex_color.lstrip("#")
    r = min(255, max(0, int(int(h[0:2], 16) * factor)))
    g = min(255, max(0, int(int(h[2:4], 16) * factor)))
    b = min(255, max(0, int(int(h[4:6], 16) * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


class MapView:
    def __init__(self, parent, game, on_route_click) -> None:
        self.parent = parent
        self.game = game
        self.on_route_click = on_route_click

        self.bg_image_original = Image.open(_ASSETS / "map.png")
        self.bg_photo = None

        self.canvas = tk.Canvas(self.parent, bg="#E4C897", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind(
            "<Configure>",
            lambda e: self.draw() if e.width > 10 and e.height > 10 else None,
        )

    #  Public 

    def draw(self) -> None:
        self.canvas.delete("all")
        self._draw_gradient_background()
        self._draw_background()
        scale, ox, oy = self._get_transform()
        self._draw_routes(scale, ox, oy)
        self._draw_cities(scale, ox, oy)

    #  Transform 

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

    #  Route drawing 

    def _draw_routes(self, scale: float, ox: float, oy: float) -> None:
        board = self.game.board  # single-hop via game.board property
        for idx, route in enumerate(board.routes):
            x1, y1 = self._scale_point(*board.cities[route.city_a], scale, ox, oy)
            x2, y2 = self._scale_point(*board.cities[route.city_b], scale, ox, oy)
            if x1 == x2 and y1 == y2:
                continue

            offset = self._parallel_offset(route, idx, scale)
            x1o, y1o, x2o, y2o = self._offset_line(x1, y1, x2, y2, offset)
            segments = self._segment_data(x1o, y1o, x2o, y2o, route.length)
            if not segments:
                continue

            tag = f"route_{idx}"
            self._draw_route_outline(x1o, y1o, x2o, y2o, scale, tag)
            self._draw_route_segments(segments, route, scale, tag)

            if route.is_ferry():
                self._draw_ferry_markers(segments[: route.ferry_locos], scale, tag)

            self.canvas.tag_bind(
                tag, "<Button-1>", lambda e, r=route: self.on_route_click(r)
            )

    def _parallel_offset(self, route, idx: int, scale: float) -> float:
        """Perpendicular pixel offset for routes that share the same city pair."""
        group = self._route_group(route)
        group_index = next((i for i, (gi, _) in enumerate(group) if gi == idx), 0)
        return (group_index - (len(group) - 1) / 2) * (_ROUTE_OFFSET * scale)

    def _draw_route_outline(
            self, x1: float, y1: float, x2: float, y2: float, scale: float, tag: str
    ) -> None:
        """White halo that forms the visible slot border for all segments."""
        self.canvas.create_line(
            x1, y1, x2, y2,
            fill="white", width=max(12, int(14 * scale)),
            capstyle="round", tags=(tag,),
        )

    def _draw_route_segments(self, segments, route, scale: float, tag: str) -> None:
        """Fill each slot — claimed routes show a train piece, empty show the route colour."""
        slot_fill_w = max(8, int(10 * scale))
        hitbox_w = max(18, int(20 * scale))

        for sx, sy, ex, ey in segments:
            self.canvas.create_line(  # wide invisible hitbox for easy clicking
                sx, sy, ex, ey,
                fill="", width=hitbox_w, capstyle="round", tags=(tag,),
            )
            if route.is_claimed():
                self._draw_train_piece(
                    sx, sy, ex, ey,
                    color=_to_hex(route.owner_player.color or "black"),
                    scale=scale, tag=tag,
                )
            else:
                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill=route.color_hex or _GRAY_SLOT,
                    width=slot_fill_w, capstyle="butt", tags=(tag,),
                )

    def _draw_train_piece(
            self,
            sx: float, sy: float, ex: float, ey: float,
            color: str, scale: float, tag: str,
    ) -> None:
        """Shadow → body → highlight layers give each carriage a 3-D look."""
        dx, dy = ex - sx, ey - sy
        length = math.hypot(dx, dy)
        if length == 0:
            return

        ux, uy = dx / length, dy / length
        px, py = -uy, ux  # perpendicular unit vector

        inset = max(2, int(3 * scale))
        sx_i, sy_i = sx + ux * inset, sy + uy * inset
        ex_i, ey_i = ex - ux * inset, ey - uy * inset

        piece_w = max(6, int(8 * scale))
        border_w = piece_w + max(2, int(2.5 * scale))
        highlight_w = max(1, int(1.5 * scale))
        perp_off = max(1, int(1.5 * scale))

        hex_color = color if color.startswith("#") else _to_hex(color)

        self.canvas.create_line(sx_i, sy_i, ex_i, ey_i,  # 1. shadow
                                fill=_adjust(hex_color, 0.55), width=border_w, capstyle="round", tags=(tag,))
        self.canvas.create_line(sx_i, sy_i, ex_i, ey_i,  # 2. body
                                fill=hex_color, width=piece_w, capstyle="round", tags=(tag,))
        self.canvas.create_line(  # 3. highlight ridge
            sx_i + px * perp_off, sy_i + py * perp_off,
            ex_i + px * perp_off, ey_i + py * perp_off,
            fill=_adjust(hex_color, 1.45), width=highlight_w, capstyle="round", tags=(tag,))

    def _draw_ferry_markers(
            self, loco_segments: list, scale: float, route_tag: str
    ) -> None:
        badge_r = max(5, int(7 * scale))
        font_size = max(6, int(7 * scale))
        for sx, sy, ex, ey in loco_segments:
            cx, cy = (sx + ex) / 2, (sy + ey) / 2
            self.canvas.create_oval(
                cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r,
                fill=_FERRY_MARKER_BG, outline=_FERRY_MARKER_FG, width=1, tags=(route_tag,))
            self.canvas.create_text(
                cx, cy, text="⚓", fill=_FERRY_MARKER_FG,
                font=("Arial", font_size), tags=(route_tag,))

    #  City drawing 

    def _draw_cities(self, scale: float, ox: float, oy: float) -> None:
        for city, (cx, cy) in self.game.board.cities.items():
            x, y = self._scale_point(cx, cy, scale, ox, oy)
            r = max(4, int(9 * scale))
            self.canvas.create_oval(x - r - 2, y - r - 2, x + r + 2, y + r + 2, fill="white", outline="")
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black", outline="")
            self._draw_outlined_text(x, y - 14 * scale, city,
                                     font=("Georgia", max(6, int(6 * scale)), "bold"))

    def _draw_outlined_text(
            self, x: float, y: float, text: str, font,
            fill: str = "black", outline: str = "white",
    ) -> None:
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]:
            self.canvas.create_text(x + dx, y + dy, text=text, font=font, fill=outline)
        self.canvas.create_text(x, y, text=text, font=font, fill=fill)

    #  Static helpers 

    def _route_group(self, route) -> list:
        key = tuple(sorted([route.city_a, route.city_b]))
        return [
            (i, r)
            for i, r in enumerate(self.game.board.routes)
            if tuple(sorted([r.city_a, r.city_b])) == key
        ]

    @staticmethod
    def _offset_line(x1, y1, x2, y2, offset) -> tuple:
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return x1, y1, x2, y2
        px, py = -dy / length, dx / length
        return (x1 + px * offset, y1 + py * offset,
                x2 + px * offset, y2 + py * offset)

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
            segments.append((x1o + ux * t, y1o + uy * t,
                             x1o + ux * (t + seg_len), y1o + uy * (t + seg_len)))
            t += seg_len + _MID_GAP
        return segments

    #  Backgrounds 

    def _draw_background(self) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return
        img = ImageEnhance.Brightness(
            ImageEnhance.Contrast(self.bg_image_original.copy()).enhance(0.95)
        ).enhance(1.02)
        iw, ih = img.size
        scale = min(w / iw, h / ih)
        new_w, new_h = max(1, int(iw * scale)), max(1, int(ih * scale))
        self.bg_photo = ImageTk.PhotoImage(img.resize((new_w, new_h), Image.Resampling.LANCZOS))
        self.canvas.create_image((w - new_w) // 2, (h - new_h) // 2,
                                 image=self.bg_photo, anchor="nw")

    def _draw_gradient_background(self) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return
        top, bottom = (50, 56, 66), (31, 35, 41)
        for y in range(h):
            t = y / h
            r = int(top[0] + (bottom[0] - top[0]) * t)
            g = int(top[1] + (bottom[1] - top[1]) * t)
            b = int(top[2] + (bottom[2] - top[2]) * t)
            self.canvas.create_line(0, y, w, y, fill=f"#{r:02x}{g:02x}{b:02x}")
