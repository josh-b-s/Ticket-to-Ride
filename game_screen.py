import tkinter as tk
from tkinter import messagebox
from map_view import MapView


class GameScreen:
    def __init__(self, root, game):
        self.root = root
        self.game = game

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.board_frame = tk.Frame(self.frame)
        self.board_frame.pack(side="left", fill="both", expand=True)

        self.side_frame = tk.Frame(self.frame, width=260, padx=10, pady=10)
        self.side_frame.pack(side="right", fill="y")
        self.side_frame.pack_propagate(False)

        # NEW: map view
        self.map_view = MapView(
            self.board_frame,
            self.game,
            on_route_click=self.on_route_click
        )

        self.build_sidebar()
        self.update_sidebar()

    # ---------- SIDEBAR ----------
    def build_sidebar(self):
        tk.Label(
            self.side_frame,
            text="Game Screen",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 10))

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

    # ---------- GAME UI ----------
    def update_sidebar(self, message=""):
        current = self.game.current_player()

        self.current_label.config(
            text=f"Current player: {current.name if current else 'None'}"
        )

        self.player_list.delete(0, "end")
        for p in self.game.get_players():
            self.player_list.insert("end", str(p))

        self.info_label.config(text=message)

    # ---------- EVENTS ----------
    def on_route_click(self, route):
        success, message = self.game.claim_route(route)

        if not success:
            messagebox.showinfo("Route", message)
            return

        self.map_view.draw()
        self.update_sidebar(message)