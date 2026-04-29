import math
import tkinter as tk


class MapView:
    def __init__(self, parent, game, on_route_click):
        self.parent = parent
        self.game = game
        self.on_route_click = on_route_click

        self.canvas = tk.Canvas(self.parent, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        if event.width < 10 or event.height < 10:
            return
        self.draw()

    def get_map_bounds(self):
        xs = [x for x, _ in self.game.cities.values()]
        ys = [y for _, y in self.game.cities.values()]
        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)

    def get_transform(self):
        self.canvas.update_idletasks()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        min_x, min_y, map_w, map_h = self.get_map_bounds()
        padding = max(80, int(min(w, h) * 0.2))

        scale = min(
            (w - padding) / map_w,
            (h - padding) / map_h
        )

        ox = (w - map_w * scale) / 2 - min_x * scale
        oy = (h - map_h * scale) / 2 - min_y * scale

        return scale, ox, oy

    def scale_point(self, x, y, scale, ox, oy):
        return x * scale + ox, y * scale + oy

    def draw(self):
        self.canvas.delete("all")

        scale, ox, oy = self.get_transform()
        self.draw_routes(scale, ox, oy)
        self.draw_cities(scale, ox, oy)

    def get_route_group(self, route):
        key = tuple(sorted([route.city_a, route.city_b]))
        return [
            (i, r) for i, r in enumerate(self.game.routes)
            if tuple(sorted([r.city_a, r.city_b])) == key
        ]

    def get_group_index(self, group, idx):
        for i, (original_i, _) in enumerate(group):
            if original_i == idx:
                return i
        return 0

    def get_route_color(self, route):
        if route.is_claimed():
            return route.owner_player.color if route.owner_player else "black"
        return route.color or "lightgray"

    @staticmethod
    def offset_line(x1, y1, x2, y2, offset):
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return x1, y1, x2, y2

        ux = dx / length
        uy = dy / length

        px = -uy
        py = ux

        return (
            x1 + px * offset,
            y1 + py * offset,
            x2 + px * offset,
            y2 + py * offset
        )

    def build_segment_data(self, x1o, y1o, x2o, y2o, route_length):
        dx = x2o - x1o
        dy = y2o - y1o
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return []

        ux = dx / length
        uy = dy / length

        end_gap = 14  # bigger gaps at both ends
        mid_gap = 6  # smaller gaps between segments

        usable_length = length - (2 * end_gap) - (mid_gap * (route_length - 1))
        if usable_length <= 0:
            return []

        segment_len = usable_length / route_length

        data = []
        t = end_gap

        for _ in range(route_length):
            sx = x1o + ux * t
            sy = y1o + uy * t
            ex = x1o + ux * (t + segment_len)
            ey = y1o + uy * (t + segment_len)

            data.append((sx, sy, ex, ey))
            t += segment_len + mid_gap

        return data

    def draw_routes(self, scale, ox, oy):
        for idx, route in enumerate(self.game.routes):
            x1, y1 = self.scale_point(*self.game.cities[route.city_a], scale, ox, oy)
            x2, y2 = self.scale_point(*self.game.cities[route.city_b], scale, ox, oy)

            if x1 == x2 and y1 == y2:
                continue

            group = self.get_route_group(route)
            group_index = self.get_group_index(group, idx)

            offset = (group_index - (len(group) - 1) / 2) * (12 * scale)
            x1o, y1o, x2o, y2o = self.offset_line(x1, y1, x2, y2, offset)

            color = self.get_route_color(route)
            hit_tag = f"route_{idx}"

            segments_data = self.build_segment_data(x1o, y1o, x2o, y2o, route.length)
            if not segments_data:
                continue

            # hitbox layer first
            for sx, sy, ex, ey in segments_data:
                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill="",
                    width=max(18, int(20 * scale)),
                    capstyle="round",
                    tags=(hit_tag,)
                )

            # visible layer second, same tag so the line itself is clickable
            for sx, sy, ex, ey in segments_data:
                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill=color,
                    width=max(10, int(10 * scale)),
                    capstyle="butt",
                    tags=(hit_tag,)
                )

            self.canvas.tag_bind(
                hit_tag,
                "<Button-1>",
                lambda e, r=route: self.on_route_click(r)
            )

    def draw_cities(self, scale, ox, oy):
        for city, (x, y) in self.game.cities.items():
            x, y = self.scale_point(x, y, scale, ox, oy)
            r = max(4, int(9 * scale))

            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="black",
                outline="white"
            )

            self.draw_outlined_text(
                x,
                y - 14 * scale,
                city,
                font=("Arial", max(6, int(6 * scale)), "bold"),
                fill="black",
                outline="white"
            )

    def draw_outlined_text(self, x, y, text, font, fill="black", outline="white"):
        offsets = [
            (-1, -1), (1, -1), (-1, 1), (1, 1),
            (-2, 0), (2, 0), (0, -2), (0, 2)
        ]

        for ox, oy in offsets:
            self.canvas.create_text(
                x + ox,
                y + oy,
                text=text,
                font=font,
                fill=outline
            )

        self.canvas.create_text(
            x,
            y,
            text=text,
            font=font,
            fill=fill
        )