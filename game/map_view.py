import math
import tkinter as tk

from PIL import Image, ImageTk, ImageEnhance

_END_GAP = 18
_MID_GAP = 6
_ROUTE_OFFSET = 12

# Ferry badge colours.
_FERRY_MARKER_BG = "#0d2237"
_FERRY_MARKER_FG = "#e8f4fc"

# -- Player color lookup
# Route slot colors come directly from RouteColor.value (hex strings).
# This table covers only player token colors (plain strings from SetupScreen)
# and locomotive cards.
_PLAYER_COLOR_HEX: dict[str, str] = {
    "red": "#c01800",
    "yellow": "#c49200",
    "green": "#27862a",
    "black": "#2a2a2a",
    "blue": "#1966d2",
    "locomotive": "#4a4a4a",
}

_GRAY_SLOT = "#B0B0B3"


def _to_hex(color: str) -> str:
    """Return hex for a player token color string, falling back to gray."""
    return _PLAYER_COLOR_HEX.get(color.lower(), "#808080")


def _adjust(hex_color: str, factor: float) -> str:
    """
    Lighten (factor > 1) or darken (factor < 1) a hex colour.
    Returns a '#rrggbb' string, clamped to [0, 255].
    """
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


class MapView:
    def __init__(self, parent, game, on_route_click):
        self.parent = parent
        self.game = game
        self.on_route_click = on_route_click

        self.bg_image_original = Image.open("map.png")
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
            slot_w = max(12, int(14 * scale))  # white outline (the slot border)
            slot_fill_w = max(8, int(10 * scale))  # gray or route-color fill

            # ── White outline for the whole route line ──
            self.canvas.create_line(
                x1o, y1o, x2o, y2o,
                fill="white",
                width=slot_w,
                capstyle="round",
                tags=(tag,),
            )

            # ── Draw each segment ──
            for seg_idx, (sx, sy, ex, ey) in enumerate(segments):

                # Wide invisible hitbox for easy clicking.
                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill="",
                    width=max(18, int(20 * scale)),
                    capstyle="round",
                    tags=(tag,),
                )

                if route.is_claimed():
                    player_color = route.owner_player.color or "black"

                    slot_color = _to_hex(player_color)

                    self._draw_train_piece(
                        sx, sy, ex, ey,
                        color=slot_color,
                        scale=scale,
                        tag=tag,
                    )
                else:
                    # Empty slot — always use route base colour or gray
                    slot_color = route.color_hex or _GRAY_SLOT

                    self.canvas.create_line(
                        sx, sy, ex, ey,
                        fill=slot_color,
                        width=slot_fill_w,
                        capstyle="butt",
                        tags=(tag,),
                    )

            # ── Ferry anchor badges ──
            if route.is_ferry():
                self._draw_ferry_markers(
                    segments[: route.ferry_locos], scale, tag
                )

            self.canvas.tag_bind(
                tag, "<Button-1>", lambda e, r=route: self.on_route_click(r)
            )

    def _draw_train_piece(
            self,
            sx: float,
            sy: float,
            ex: float,
            ey: float,
            color: str,
            scale: float,
            tag: str,
    ) -> None:
        """
        Draw a single train carriage piece centred on the segment sx,sy→ex,ey.

        Layers (bottom to top):
          1. Dark shadow border — slightly wider, darkened colour, round caps.
          2. Main carriage body — player colour, round caps, inset from ends.
          3. Highlight line — thin, lightened colour, offset toward the
             perpendicular "up" direction for a subtle raised-surface look.
        """
        dx, dy = ex - sx, ey - sy
        length = math.hypot(dx, dy)
        if length == 0:
            return

        # Unit vectors along and perpendicular to the route.
        ux, uy = dx / length, dy / length
        px, py = -uy, ux  # perpendicular (rotated 90°)

        # Inset the piece endpoints so there is a visible gap at each end,
        # making individual carriages clearly distinct.
        inset = max(2, int(3 * scale))
        sx_i = sx + ux * inset
        sy_i = sy + uy * inset
        ex_i = ex - ux * inset
        ey_i = ey - uy * inset

        piece_w = max(6, int(8 * scale))
        border_w = piece_w + max(2, int(2.5 * scale))
        highlight_w = max(1, int(1.5 * scale))
        perp_offset = max(1, int(1.5 * scale))

        hex_color = color if color.startswith("#") else _to_hex(color)
        dark_color = _adjust(hex_color, 0.55)
        light_color = _adjust(hex_color, 1.45)

        # 1. Shadow / border — drawn first so it sits under the piece.
        self.canvas.create_line(
            sx_i, sy_i, ex_i, ey_i,
            fill=dark_color,
            width=border_w,
            capstyle="round",
            tags=(tag,),
        )

        # 2. Main carriage body.
        self.canvas.create_line(
            sx_i, sy_i, ex_i, ey_i,
            fill=hex_color,
            width=piece_w,
            capstyle="round",
            tags=(tag,),
        )

        # 3. Highlight — offset perpendicular to the route direction by
        #    perp_offset pixels, giving the illusion of a curved top surface.
        hx1 = sx_i + px * perp_offset
        hy1 = sy_i + py * perp_offset
        hx2 = ex_i + px * perp_offset
        hy2 = ey_i + py * perp_offset

        self.canvas.create_line(
            hx1, hy1, hx2, hy2,
            fill=light_color,
            width=highlight_w,
            capstyle="round",
            tags=(tag,),
        )

    def _draw_ferry_markers(
            self,
            loco_segments: list,
            scale: float,
            route_tag: str,
    ) -> None:
        """Draw a small anchor badge on each ferry loco slot."""
        badge_r = max(5, int(7 * scale))
        font_size = max(6, int(7 * scale))

        for sx, sy, ex, ey in loco_segments:
            cx = (sx + ex) / 2
            cy = (sy + ey) / 2

            self.canvas.create_oval(
                cx - badge_r, cy - badge_r,
                cx + badge_r, cy + badge_r,
                fill=_FERRY_MARKER_BG,
                outline=_FERRY_MARKER_FG,
                width=1,
                tags=(route_tag,),
            )
            self.canvas.create_text(
                cx, cy,
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
                fill="white", outline="",
            )
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="black", outline="",
            )
            self._draw_outlined_text(
                x, y - 14 * scale, city,
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

    @staticmethod
    def _offset_line(x1, y1, x2, y2, offset) -> tuple:
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return x1, y1, x2, y2
        px, py = -dy / length, dx / length
        return (
            x1 + px * offset, y1 + py * offset,
            x2 + px * offset, y2 + py * offset,
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

        x_pos = (w - new_w) // 2
        y_pos = (h - new_h) // 2
        self.canvas.create_image(x_pos, y_pos, image=self.bg_photo, anchor="nw")

    def _draw_wood_background(self) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        img = self.wood_bg_original.resize(
            (w, h), Image.Resampling.LANCZOS
        )
        self.wood_bg_photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(
            0, 0, image=self.wood_bg_photo, anchor="nw"
        )
