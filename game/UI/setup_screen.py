import tkinter as tk
from tkinter import messagebox

from game.UI.game_screen import GameScreen
from game.UI.theme import (
    ACCENT_GOLD, ACCENT_RED, BG_ENTRY, BG_MAIN as BG, BG_PANEL,
    BTN_HOVER, BTN_OFF, FG_MUTED, FG_PRIMARY, FONT_BTN, FONT_CITY,
    FONT_ENTRY, FONT_HERO, FONT_HINT, FONT_LABEL, GOLD_DIM, PLAYER_SLOTS,
)


class SetupScreen:
    def __init__(self, root: tk.Tk, game):
        self.root = root
        self.game = game
        self.root.configure(bg=BG)

        self.frame = tk.Frame(self.root, bg=BG)
        self.frame.pack(fill="both", expand=True)

        self._build_ui()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        centre = tk.Frame(self.frame, bg=BG)
        centre.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tk.Label(centre, text="TICKET TO RIDE", font=FONT_HERO, bg=BG, fg=ACCENT_GOLD).pack()
        tk.Label(centre, text="L  O  N  D  O  N", font=FONT_CITY, bg=BG, fg=FG_MUTED).pack(pady=(4, 0))

        tk.Frame(centre, height=1, bg=ACCENT_GOLD).pack(fill="x", pady=22)

        tk.Label(
            centre, text="Enter 2 \u2013 5 player names to begin",
            font=FONT_HINT, bg=BG, fg=FG_MUTED,
        ).pack(pady=(0, 14))

        # Player slots
        self.entries: list[tuple[str, tk.Entry]] = []

        for color_name, hex_color, label in PLAYER_SLOTS:
            row = tk.Frame(centre, bg=BG_PANEL, pady=10, padx=16)
            row.pack(fill="x", pady=3)

            dot = tk.Canvas(row, width=12, height=12, bg=BG_PANEL, highlightthickness=0)
            dot.create_oval(0, 0, 12, 12, fill=hex_color, outline="")
            dot.pack(side="left", padx=(0, 10))

            tk.Label(
                row, text=label, font=FONT_LABEL, width=7, anchor="w",
                bg=BG_PANEL, fg=hex_color,
            ).pack(side="left")

            tk.Frame(row, width=1, bg=GOLD_DIM).pack(side="left", fill="y", padx=(10, 14))

            entry = tk.Entry(
                row, width=22, font=FONT_ENTRY, bg=BG_ENTRY, fg=FG_PRIMARY,
                insertbackground=ACCENT_GOLD, relief="flat",
                highlightthickness=1, highlightcolor=ACCENT_GOLD, highlightbackground=GOLD_DIM,
            )
            entry.pack(side="left", ipady=3)
            entry.bind("<FocusIn>",  lambda e, r=row: r.config(bg="#363B45"))
            entry.bind("<FocusOut>", lambda e, r=row: r.config(bg=BG_PANEL))

            self.entries.append((color_name, entry))

        tk.Frame(centre, height=1, bg=ACCENT_GOLD).pack(fill="x", pady=22)

        # Buttons
        btn_row = tk.Frame(centre, bg=BG)
        btn_row.pack()

        start = tk.Button(
            btn_row, text="START GAME", font=FONT_BTN,
            bg=ACCENT_RED, fg="#ffffff",
            activebackground=BTN_HOVER, activeforeground="#ffffff",
            relief="flat", padx=30, pady=10, cursor="hand2", bd=0,
            highlightthickness=0, command=self._start_game,
        )
        start.pack(side="left", padx=(0, 10))
        start.bind("<Enter>", lambda e: start.config(bg=BTN_HOVER))
        start.bind("<Leave>", lambda e: start.config(bg=ACCENT_RED))

        clear = tk.Button(
            btn_row, text="CLEAR", font=FONT_BTN,
            bg=BTN_OFF, fg=FG_MUTED,
            activebackground=GOLD_DIM, activeforeground=FG_PRIMARY,
            relief="flat", padx=18, pady=10, cursor="hand2", bd=0,
            highlightthickness=0, command=self._clear_inputs,
        )
        clear.pack(side="left")
        clear.bind("<Enter>", lambda e: clear.config(fg=FG_PRIMARY))
        clear.bind("<Leave>", lambda e: clear.config(fg=FG_MUTED))

    # ── Event handlers ────────────────────────────────────────────────────────

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