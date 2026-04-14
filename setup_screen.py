import tkinter as tk
from tkinter import messagebox

from game_screen import GameScreen


class SetupScreen:
    def __init__(self, root, game):
        self.root = root
        self.game = game
        self.game_screen = None

        self.frame = tk.Frame(self.root, padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Ticket to Ride", font=("Arial", 18, "bold")).pack(pady=(0, 10))
        tk.Label(self.frame, text="Enter 2 to 5 player names").pack(pady=(0, 10))

        self.entries = []
        for i in range(5):
            row = tk.Frame(self.frame)
            row.pack(fill="x", pady=5)

            tk.Label(row, text=f"Player {i + 1}:", width=12, anchor="w").pack(side="left")
            entry = tk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            self.entries.append(entry)

        tk.Button(self.frame, text="Start Game", command=self.start_game).pack(pady=15)

    def start_game(self):
        names = [entry.get().strip() for entry in self.entries]
        names = [name for name in names if name]

        if len(names) < 2:
            messagebox.showerror("Error", "Please enter at least 2 player names.")
            return

        if len(names) != len(set(names)):
            messagebox.showerror("Error", "Player names must be unique.")
            return

        self.game.players.clear()

        for name in names[:5]:
            self.game.add_player(name)

        try:
            self.game.start()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self.frame.destroy()
        self.root.current_screen = GameScreen(self.root, self.game)