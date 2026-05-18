import tkinter as tk
from tkinter import messagebox

from game_screen import GameScreen

# ── Palette (matches game_screen exactly) ─────────────────────────────────────
BG          = "#160d08"   # espresso – window fill
BG_PANEL    = "#221409"   # dark card / row background
BG_ENTRY    = "#0f0804"   # entry field bg
ACCENT_RED  = "#9e2020"   # TTR signal red
ACCENT_GOLD = "#c49a3c"   # railway gold
GOLD_DIM    = "#5a3e10"   # dimmed gold for dividers / borders
FG_PRIMARY  = "#f0e6d0"   # warm cream
FG_MUTED    = "#7a5c3a"   # secondary / hint text

FONT_HERO  = ("Georgia", 28, "bold")
FONT_CITY  = ("Georgia", 12)
FONT_LABEL = ("Georgia", 10, "bold")
FONT_ENTRY = ("Georgia", 11)
FONT_BTN   = ("Georgia", 11, "bold")
FONT_HINT  = ("Georgia", 8)

_SLOTS = [
    ("red",    "#c43030", "RED"),
    ("yellow", "#c49a3c", "YELLOW"),
    ("green",  "#2e8c2e", "GREEN"),
    ("black",  "#aaaaaa", "BLACK"),
    ("blue",   "#2255d4", "BLUE"),
]


class SetupScreen:
    def __init__(self, root: tk.Tk, game):
        self.root = root
        self.game = game
        self.root.configure(bg=BG)

        self.frame = tk.Frame(self.root, bg=BG)
        self.frame.pack(fill="both", expand=True)

        self._build_ui()

    # ─────────────────────────────────────────────────────────────── build UI ─

    def _build_ui(self) -> None:
        # Vertically & horizontally centred column
        centre = tk.Frame(self.frame, bg=BG)
        centre.place(relx=0.5, rely=0.5, anchor="center")

        # ── Title ─────────────────────────────────────────────────────────────
        tk.Label(
            centre,
            text="TICKET TO RIDE",
            font=FONT_HERO,
            bg=BG,
            fg=ACCENT_GOLD,
        ).pack()

        tk.Label(
            centre,
            text="L  O  N  D  O  N",
            font=FONT_CITY,
            bg=BG,
            fg=FG_MUTED,
        ).pack(pady=(4, 0))

        # Gold rule
        tk.Frame(centre, height=1, bg=ACCENT_GOLD).pack(fill="x", pady=22)

        # ── Instruction ───────────────────────────────────────────────────────
        tk.Label(
            centre,
            text="Enter 2 – 5 player names to begin",
            font=FONT_HINT,
            bg=BG,
            fg=FG_MUTED,
        ).pack(pady=(0, 14))

        # ── Player slots ──────────────────────────────────────────────────────
        self.entries: list[tuple[str, tk.Entry]] = []

        for color_name, hex_color, label in _SLOTS:
            row = tk.Frame(centre, bg=BG_PANEL, pady=10, padx=16)
            row.pack(fill="x", pady=3)

            # Colour dot
            dot = tk.Canvas(
                row, width=12, height=12,
                bg=BG_PANEL, highlightthickness=0,
            )
            dot.create_oval(0, 0, 12, 12, fill=hex_color, outline="")
            dot.pack(side="left", padx=(0, 10))

            # Colour label
            tk.Label(
                row,
                text=label,
                font=FONT_LABEL,
                width=7,
                anchor="w",
                bg=BG_PANEL,
                fg=hex_color,
            ).pack(side="left")

            # Thin vertical separator
            tk.Frame(row, width=1, bg=GOLD_DIM).pack(
                side="left", fill="y", padx=(10, 14),
            )

            # Entry field
            entry = tk.Entry(
                row,
                width=22,
                font=FONT_ENTRY,
                bg=BG_ENTRY,
                fg=FG_PRIMARY,
                insertbackground=ACCENT_GOLD,
                relief="flat",
                highlightthickness=1,
                highlightcolor=ACCENT_GOLD,
                highlightbackground=GOLD_DIM,
            )
            entry.pack(side="left", ipady=3)

            # Subtle focus highlight on the whole row
            entry.bind("<FocusIn>",  lambda e, r=row: r.config(bg="#2e1c0e"))
            entry.bind("<FocusOut>", lambda e, r=row: r.config(bg=BG_PANEL))

            self.entries.append((color_name, entry))

        # Gold rule
        tk.Frame(centre, height=1, bg=ACCENT_GOLD).pack(fill="x", pady=22)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = tk.Frame(centre, bg=BG)
        btn_row.pack()

        start = tk.Button(
            btn_row,
            text="START GAME",
            font=FONT_BTN,
            bg=ACCENT_RED,
            fg=FG_PRIMARY,
            activebackground="#b52828",
            activeforeground=FG_PRIMARY,
            relief="flat",
            padx=30,
            pady=10,
            cursor="hand2",
            bd=0,
            highlightthickness=0,
            command=self._start_game,
        )
        start.pack(side="left", padx=(0, 10))
        start.bind("<Enter>", lambda e: start.config(bg="#b52828"))
        start.bind("<Leave>", lambda e: start.config(bg=ACCENT_RED))

        clear = tk.Button(
            btn_row,
            text="CLEAR",
            font=FONT_BTN,
            bg=BG_PANEL,
            fg=FG_MUTED,
            activebackground="#2e1c0e",
            activeforeground=FG_PRIMARY,
            relief="flat",
            padx=18,
            pady=10,
            cursor="hand2",
            bd=0,
            highlightthickness=0,
            command=self._clear_inputs,
        )
        clear.pack(side="left")
        clear.bind("<Enter>", lambda e: clear.config(fg=FG_PRIMARY))
        clear.bind("<Leave>", lambda e: clear.config(fg=FG_MUTED))

    # ───────────────────────────────────────────────────────── event handlers ─

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