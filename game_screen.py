import math
import tkinter as tk
from tkinter import messagebox
from helpers import offset_line


class GameScreen:
    def __init__(self, root, game):
        self.root = root
        self.game = game

        self.player_colors = self.build_player_colors()

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.board_frame = tk.Frame(self.frame)
        self.board_frame.pack(side="left", fill="both", expand=True)

        self.side_frame = tk.Frame(self.frame, width=260, padx=10, pady=10)
        self.side_frame.pack(side="right", fill="y")
        self.side_frame.pack_propagate(False)

        self.build_sidebar()
        self.build_canvas()

        self.canvas.bind("<Configure>", self.on_resize)

    def build_sidebar(self):
        tk.Label(self.side_frame, text="Game Screen",
                 font=("Arial", 18, "bold")).pack(pady=(0, 10))

        self.current_label = tk.Label(self.side_frame, text="")
        self.current_label.pack(pady=5)

        tk.Label(self.side_frame, text="Players:").pack(anchor="w", pady=(15, 5))

        self.player_list = tk.Listbox(self.side_frame, height=10)
        self.player_list.pack(fill="x")

        tk.Label(
            self.side_frame,
            text="Click a route on the board to claim it.",
            fg="gray",
            wraplength=220
        ).pack(pady=15)

        self.info_label = tk.Label(self.side_frame, text="", wraplength=220)
        self.info_label.pack(pady=10)

    def build_canvas(self):
        self.canvas = tk.Canvas(self.board_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)


    def build_player_colors(self):
        palette = ["red", "blue", "green", "purple", "orange"]
        return {
            p.name: palette[i % len(palette)]
            for i, p in enumerate(self.game.get_players())
        }


    def on_resize(self, event):
        if event.width < 10 or event.height < 10:
            return
        self.draw_board()
        self.update_sidebar()

    def get_transform(self):
        self.canvas.update_idletasks()

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
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

    def get_map_bounds(self):
        xs = [x for x, _ in self.game.cities.values()]
        ys = [y for _, y in self.game.cities.values()]

        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


    def draw_board(self):
        self.canvas.delete("all")

        scale, ox, oy = self.get_transform()

        self.draw_routes(scale, ox, oy)
        self.draw_cities(scale, ox, oy)


    def draw_routes(self, scale, ox, oy):
        for idx, route in enumerate(self.game.routes):

            x1, y1 = self.scale_point(*self.game.cities[route.city_a], scale, ox, oy)
            x2, y2 = self.scale_point(*self.game.cities[route.city_b], scale, ox, oy)

            if x1 == x2 and y1 == y2:
                continue

            group = self.get_route_group(route)

            group_index = self.get_group_index(group, idx)

            offset = (group_index - (len(group) - 1) / 2) * (12 * scale)

            x1o, y1o, x2o, y2o = offset_line(x1, y1, x2, y2, offset)

            dx, dy = x2o - x1o, y2o - y1o
            length = math.sqrt(dx * dx + dy * dy)
            if length == 0:
                continue

            ux, uy = dx / length, dy / length

            color = self.get_route_color(route)

            segments = route.length
            segment_gap = length / segments
            segment_len = segment_gap * 0.6
            offset_in = (segment_gap - segment_len) / 2

            self.draw_segmented_route(
                x1o, y1o, ux, uy,
                segments, segment_gap, segment_len, offset_in,
                color, scale, route, idx
            )

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
            return self.player_colors.get(route.claimed_by, "black")
        return route.color or "lightgray"

    def draw_segmented_route(
        self,
        x, y, ux, uy,
        segments, gap, seg_len, offset_in,
        color, scale, route, idx
    ):
        tag = f"route_{idx}"

        for i in range(segments):
            t0 = gap * i + offset_in
            t1 = t0 + seg_len

            sx, sy = x + ux * t0, y + uy * t0
            ex, ey = x + ux * t1, y + uy * t1

            seg_tag = f"{tag}_{i}"

            self.canvas.create_line(
                sx, sy, ex, ey,
                fill=color,
                width=max(2, int(10 * scale)),
                capstyle="butt",
                tags=(seg_tag,)
            )

            self.canvas.create_line(
                sx, sy, ex, ey,
                fill="",
                width=max(10, int(20 * scale)),
                tags=(seg_tag,)
            )

            self.canvas.tag_bind(
                seg_tag,
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


    def update_sidebar(self, message=""):
        current = self.game.current_player()
        self.current_label.config(
            text=f"Current player: {current.name if current else 'None'}"
        )

        self.player_list.delete(0, "end")
        for p in self.game.get_players():
            self.player_list.insert("end", str(p))

        self.info_label.config(text=message)


    def on_route_click(self, route):
        success, message = self.game.claim_route(route)

        if not success:
            messagebox.showinfo("Route", message)
            return

        self.draw_board()
        self.update_sidebar(message)

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