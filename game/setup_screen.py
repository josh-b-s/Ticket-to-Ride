import tkinter as tk
from tkinter import messagebox

from game_screen import GameScreen

_PLAYER_SLOTS = [
    ("red", "Red"),
    ("yellow", "Yellow"),
    ("green", "Green"),
    ("black", "Black"),
    ("blue", "Blue"),
]


class SetupScreen:
    def __init__(self, root: tk.Tk, game):
        self.root = root
        self.game = game

        self.frame = tk.Frame(self.root, padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Ticket to Ride", font=("Arial", 18, "bold")).pack(
            pady=(0, 10)
        )
        tk.Label(
            self.frame,
            text="Sprint 2 Prototype - London Map",
            font=("Arial", 11),
        ).pack(pady=(0, 3))
        tk.Label(self.frame, text="Enter 2 to 5 unique player names").pack(pady=(0, 12))
        tk.Label(
            self.frame,
            text="Each player uses the colour shown above their input box.",
            fg="#333",
        ).pack(pady=(0, 15))

        row = tk.Frame(self.frame)
        row.pack(pady=10)

        self.entries: list[tuple[str, tk.Entry]] = []
        for color_name, label in _PLAYER_SLOTS:
            col = tk.Frame(row, padx=10)
            col.pack(side="left")
            tk.Label(col, text=label, font=("Arial", 10, "bold"), fg=color_name).pack()
            entry = tk.Entry(col, width=12, justify="center")
            entry.insert(0, "")
            entry.pack(pady=5)
            self.entries.append((color_name, entry))

        button_row = tk.Frame(self.frame)
        button_row.pack(pady=20)
        tk.Button(button_row, text="Start Game", command=self._start_game, width=14).pack(
            side="left", padx=6
        )
        tk.Button(button_row, text="Clear", command=self._clear_inputs, width=14).pack(
            side="left", padx=6
        )

    def _clear_inputs(self) -> None:
        for _, entry in self.entries:
            entry.delete(0, "end")

    def _start_game(self) -> None:
        self.game.players.clear()

        filled = [
            (color, entry.get().strip())
            for color, entry in self.entries
            if entry.get().strip()
        ]

        if len(filled) < 2:
            messagebox.showerror("Error", "Please enter at least 2 player names.")
            return

        names = [name for _, name in filled]
        if len(names) != len(set(names)):
            messagebox.showerror("Error", "Player names must be unique.")
            return

        for color_name, name in filled:
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
