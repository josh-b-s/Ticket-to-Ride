import math
import tkinter as tk
from tkinter import messagebox

from helpers import offset_line


class GameScreen:
    def __init__(self, root, game):
        self.root = root
        self.game = game

        self.player_colors = {}
        palette = ["red", "blue", "green", "purple", "orange"]
        for i, player in enumerate(self.game.get_players()):
            self.player_colors[player.name] = palette[i % len(palette)]

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.board_frame = tk.Frame(self.frame)
        self.board_frame.pack(side="left", fill="both", expand=True)

        self.side_frame = tk.Frame(self.frame, width=260, padx=10, pady=10)
        self.side_frame.pack(side="right", fill="y")
        self.side_frame.pack_propagate(False)

        tk.Label(self.side_frame, text="Game Screen", font=("Arial", 18, "bold")).pack(pady=(0, 10))

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

        self.info_label = tk.Label(self.side_frame, text="", wraplength=220, justify="left")
        self.info_label.pack(pady=10)

        self.canvas = tk.Canvas(self.board_frame, bg="white", width=900, height=650)
        self.canvas.pack(fill="both", expand=True)

        self.draw_board()
        self.update_sidebar()

    def city_radius(self):
        return 9

    def draw_board(self):
        self.canvas.delete("all")

        for idx, route in enumerate(self.game.routes):
            x1, y1 = self.game.cities[route.city_a]
            x2, y2 = self.game.cities[route.city_b]

            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)

            if length == 0:
                continue

            # ---- FIND PARALLEL ROUTES ----
            key = tuple(sorted([route.city_a, route.city_b]))

            same_routes = [
                (i, r) for i, r in enumerate(self.game.routes)
                if tuple(sorted([r.city_a, r.city_b])) == key
            ]

            for group_index, (original_i, r) in enumerate(same_routes):
                if original_i == idx:
                    break

            offset = (group_index - (len(same_routes) - 1) / 2) * 12

            # apply offset
            x1o, y1o, x2o, y2o = offset_line(x1, y1, x2, y2, offset)

            # ---- RECOMPUTE DIRECTION AFTER OFFSET (IMPORTANT FIX) ----
            dxo = x2o - x1o
            dyo = y2o - y1o
            length_o = math.sqrt(dxo * dxo + dyo * dyo)

            if length_o == 0:
                continue

            ux = dxo / length_o
            uy = dyo / length_o

            # color
            if route.is_claimed():
                color = self.player_colors.get(route.claimed_by, "black")
            else:
                color = route.color if route.color else "lightgray"

            tag = f"route_{idx}"

            # clickable hitbox
            self.canvas.create_line(
                x1o, y1o, x2o, y2o,
                fill="",
                width=20,
                tags=(tag,)
            )

            self.canvas.tag_bind(
                tag,
                "<Button-1>",
                lambda e, r=route: self.on_route_click(r)
            )

            # ---- SEGMENTS (CENTERED + CORRECT) ----
            segments = route.length
            segment_gap = length_o / segments
            segment_len = segment_gap * 0.6
            offset_in = (segment_gap - segment_len) / 2

            for i in range(segments):
                t_start = segment_gap * i + offset_in
                t_end = t_start + segment_len

                sx = x1o + ux * t_start
                sy = y1o + uy * t_start

                ex = x1o + ux * t_end
                ey = y1o + uy * t_end

                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill=color,
                    width=10,
                    capstyle="butt"
                )

        # cities on top
        for city, (x, y) in self.game.cities.items():
            r = self.city_radius()
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="black",
                outline="white",
                width=1
            )
            self.canvas.create_text(
                x, y - 16,
                text=city,
                font=("Arial", 10, "bold")
            )

    def update_sidebar(self, message=""):
        current = self.game.current_player()
        current_name = current.name if current else "None"
        self.current_label.config(text=f"Current player: {current_name}")

        self.player_list.delete(0, "end")
        for player in self.game.get_players():
            self.player_list.insert("end", str(player))

        self.info_label.config(text=message)

    def on_route_click(self, route):
        success, message = self.game.claim_route(route)
        if not success:
            messagebox.showinfo("Route", message)
            return

        self.draw_board()
        self.update_sidebar(message)