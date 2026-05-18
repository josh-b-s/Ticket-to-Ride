import math
import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance

_END_GAP = 18
_MID_GAP = 6
_ROUTE_OFFSET = 12

# Ferry loco slot appearance.
_FERRY_LOCO_COLOR = "#1a3a5c"   # dark navy for loco slots
_FERRY_MARKER_BG = "#0d2237"    # even darker for the anchor badge
_FERRY_MARKER_FG = "#e8f4fc"    # light text


class MapView:
    def __init__(self, parent, game, on_route_click):
        self.parent = parent
        self.game = game
        self.on_route_click = on_route_click

        self.bg_image_original = Image.open("london_map.png")
        self.bg_photo = None

        self.wood_bg_original = Image.open("wood.jpg")
        self.wood_bg_photo = None

        self.canvas = tk.Canvas(
            self.parent, bg="#E4C897", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind(
            "<Configure>",
            lambda e: self.draw() if e.width > 10 and e.height > 10 else None,
        )

    # ---------------------------------------------------------------- public

    def draw(self) -> None:
        self.canvas.delete("all")
        self._draw_wood_background()
        self._draw_background()
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

    def _scale_point(
        self, x: float, y: float, scale: float, ox: float, oy: float
    ):
        return x * scale + ox, y * scale + oy

    # -------------------------------------------------------------- drawing

    def _draw_routes(self, scale: float, ox: float, oy: float) -> None:
        for idx, route in enumerate(self.game.routes):
            x1, y1 = self._scale_point(
                *self.game.cities[route.city_a], scale, ox, oy
            )
            x2, y2 = self._scale_point(
                *self.game.cities[route.city_b], scale, ox, oy
            )
            if x1 == x2 and y1 == y2:
                continue

            group = self._route_group(route)
            group_index = next(
                (i for i, (gi, _) in enumerate(group) if gi == idx), 0
            )
            offset = (
                (group_index - (len(group) - 1) / 2) * (_ROUTE_OFFSET * scale)
            )
            x1o, y1o, x2o, y2o = self._offset_line(x1, y1, x2, y2, offset)

            segments = self._segment_data(x1o, y1o, x2o, y2o, route.length)
            if not segments:
                continue

            tag = f"route_{idx}"
            outline_width = max(12, int(14 * scale))
            route_width = max(8, int(10 * scale))
            hitbox_width = max(18, int(20 * scale))

            # White outline for the full route line.
            self.canvas.create_line(
                x1o, y1o, x2o, y2o,
                fill="white",
                width=outline_width,
                capstyle="round",
                tags=(tag,),
            )

            # Draw each segment — ferry loco slots get a distinct colour.
            for seg_idx, (sx, sy, ex, ey) in enumerate(segments):
                is_loco_slot = (
                    route.is_ferry() and seg_idx < route.ferry_locos
                )
                fill_color = (
                    _FERRY_LOCO_COLOR
                    if is_loco_slot
                    else self._route_color(route)
                )

                # Invisible wide hitbox for easier clicking.
                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill="",
                    width=hitbox_width,
                    capstyle="round",
                    tags=(tag,),
                )
                # Visible coloured segment.
                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill=fill_color,
                    width=route_width,
                    capstyle="butt",
                    tags=(tag,),
                )

            # Anchor badge on each loco slot.
            if route.is_ferry():
                self._draw_ferry_markers(
                    segments[: route.ferry_locos], scale, tag
                )

            self.canvas.tag_bind(
                tag, "<Button-1>", lambda e, r=route: self.on_route_click(r)
            )

    def _draw_ferry_markers(
        self,
        loco_segments: list,
        scale: float,
        route_tag: str,
    ) -> None:
        """
        Draw a small anchor badge in the centre of each ferry loco slot.
        The badge is a dark oval with an anchor character inside.
        """
        badge_r = max(5, int(7 * scale))
        font_size = max(6, int(7 * scale))

        for sx, sy, ex, ey in loco_segments:
            cx = (sx + ex) / 2
            cy = (sy + ey) / 2

            # Dark oval badge.
            self.canvas.create_oval(
                cx - badge_r,
                cy - badge_r,
                cx + badge_r,
                cy + badge_r,
                fill=_FERRY_MARKER_BG,
                outline=_FERRY_MARKER_FG,
                width=1,
                tags=(route_tag,),
            )
            # Anchor symbol — ⚓ renders on most platforms; fallback to "L".
            self.canvas.create_text(
                cx,
                cy,
                text="⚓",
                fill=_FERRY_MARKER_FG,
                font=("Arial", font_size),
                tags=(route_tag,),
            )

    def _draw_cities(self, scale: float, ox: float, oy: float) -> None:
        for city, (cx, cy) in self.game.cities.items():
            x, y = self._scale_point(cx, cy, scale, ox, oy)
            r = max(4, int(9 * scale))

            self.canvas.create_oval(
                x - r - 2, y - r - 2,
                x + r + 2, y + r + 2,
                fill="white",
                outline="",
            )
            self.canvas.create_oval(
                x - r, y - r,
                x + r, y + r,
                fill="black",
                outline="",
            )
            self._draw_outlined_text(
                x,
                y - 14 * scale,
                city,
                font=("Georgia", max(6, int(6 * scale)), "bold"),
            )

    def _draw_outlined_text(
        self,
        x: float,
        y: float,
        text: str,
        font,
        fill: str = "black",
        outline: str = "white",
    ) -> None:
        for dx, dy in [
            (-1, -1), (1, -1), (-1, 1), (1, 1),
            (-2, 0), (2, 0), (0, -2), (0, 2),
        ]:
            self.canvas.create_text(
                x + dx, y + dy, text=text, font=font, fill=outline
            )
        self.canvas.create_text(x, y, text=text, font=font, fill=fill)

    # -------------------------------------------------------------- helpers

    def _route_group(self, route) -> list:
        key = tuple(sorted([route.city_a, route.city_b]))
        return [
            (i, r)
            for i, r in enumerate(self.game.routes)
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
        return (
            x1 + px * offset,
            y1 + py * offset,
            x2 + px * offset,
            y2 + py * offset,
        )

    @staticmethod
    def _segment_data(x1o, y1o, x2o, y2o, route_length: int) -> list:
        dx, dy = x2o - x1o, y2o - y1o
        length = math.hypot(dx, dy)
        if length == 0:
            return []

        ux, uy = dx / length, dy / length
        usable = (
            length - (2 * _END_GAP) - (_MID_GAP * (route_length - 1))
        )
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

    # -------------------------------------------------------------- backgrounds

    def _draw_background(self) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        img = self.bg_image_original.copy()
        img = ImageEnhance.Contrast(img).enhance(0.95)
        img = ImageEnhance.Brightness(img).enhance(1.02)

        iw, ih = img.size
        scale = min(w / iw, h / ih)
        new_w = max(1, int(iw * scale))
        new_h = max(1, int(ih * scale))

        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized)

        x = (w - new_w) // 2
        y = (h - new_h) // 2
        self.canvas.create_image(x, y, image=self.bg_photo, anchor="nw")

    def _draw_wood_background(self) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        img = self.wood_bg_original.resize(
            (w, h), Image.Resampling.LANCZOS
        )
        self.wood_bg_photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self.wood_bg_photo, anchor="nw")