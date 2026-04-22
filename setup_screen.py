import tkinter as tk
from tkinter import messagebox

from game_screen import GameScreen


class SetupScreen:
    PLAYER_SLOTS = [
        ("red", "Red"),
        ("yellow", "Yellow"),
        ("green", "Green"),
        ("black", "Black"),
        ("blue", "Blue"),
    ]

    def __init__(self, root, game):
        self.root = root
        self.game = game

        self.frame = tk.Frame(self.root, padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)

        tk.Label(
            self.frame,
            text="Ticket to Ride",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 10))

        tk.Label(
            self.frame,
            text="Enter 2 to 5 player names"
        ).pack(pady=(0, 15))

        self.input_row = tk.Frame(self.frame)
        self.input_row.pack(pady=10)

        self.entries = []

        for color_name, label in self.PLAYER_SLOTS:
            col_frame = tk.Frame(self.input_row, padx=10)
            col_frame.pack(side="left")

            tk.Label(
                col_frame,
                text=label,
                font=("Arial", 10, "bold"),
                fg=color_name
            ).pack()

            entry = tk.Entry(col_frame, width=12, justify="center")
            entry.pack(pady=5)

            self.entries.append((color_name, entry))

        tk.Button(
            self.frame,
            text="Start Game",
            command=self.start_game
        ).pack(pady=20)

    def start_game(self):
        self.game.players.clear()

        names = [entry.get().strip() for _, entry in self.entries]
        names = [name for name in names if name]

        if len(names) < 2:
            messagebox.showerror("Error", "Please enter at least 2 player names.")
            return

        if len(names) != len(set(names)):
            messagebox.showerror("Error", "Player names must be unique.")
            return

        for color_name, entry in self.entries:
            name = entry.get().strip()
            if name:
                player = self.game.add_player(name)
                if player is not None:
                    player.color = color_name

        try:
            self.game.start()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self.frame.destroy()
        self.root.current_screen = GameScreen(self.root, self.game)