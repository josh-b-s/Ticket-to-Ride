"""sidebar.py — SidebarPanel: player roster, turn info, and action buttons."""
from __future__ import annotations

import tkinter as tk

from game.UI.theme import (
    ACCENT_GOLD, ACCENT_RED, BG_PANEL, BG_SURFACE, BTN_HOVER,
    FG_HINT, FG_MUTED, FG_PRIMARY, FONT_BODY, FONT_BUTTON,
    FONT_HINT, FONT_LABEL, GOLD_DIM, _PLAYER_COLORS,
)


class SidebarPanel:
    """
    Right-hand sidebar containing the player roster, turn status, and
    action buttons.

    ``callbacks`` must contain:
        ``on_draw_cards``    – called when "Draw Train Cards" is clicked
        ``on_draw_tickets``  – called when "Draw Destination Tickets" is clicked
    """

    def __init__(self, parent: tk.Frame, callbacks: dict) -> None:
        self._cbs = callbacks
        self._build(parent)

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self, parent: tk.Frame) -> None:
        self._section_header(parent, "Players")

        self.player_canvas = tk.Canvas(
            parent, bg=BG_SURFACE,
            highlightthickness=1, highlightbackground=GOLD_DIM,
        )
        self.player_canvas.pack(fill="x")

        self.player_rows_frame = tk.Frame(self.player_canvas, bg=BG_SURFACE)
        self.player_canvas.create_window(
            (0, 0), window=self.player_rows_frame, anchor="nw", width=260,
        )

        self._section_header(parent, "Turn Info")

        self.info_label = tk.Label(
            parent, text="", wraplength=250,
            justify="left", anchor="w",
            bg=BG_PANEL, fg=FG_PRIMARY, font=FONT_BODY,
        )
        self.info_label.pack(fill="x", pady=(0, 2))

        self.hint_label = tk.Label(
            parent, text="", wraplength=250,
            justify="left", anchor="w",
            bg=BG_SURFACE, fg=FG_HINT, font=FONT_HINT, padx=8, pady=5,
        )

        tk.Frame(parent, height=1, bg=GOLD_DIM).pack(fill="x", pady=(4, 0))
        self._section_header(parent, "Actions")

        self.action_frame = tk.Frame(parent, bg=BG_PANEL)
        self.action_frame.pack(fill="x", pady=4)

    @staticmethod
    def _section_header(parent: tk.Frame, title: str) -> None:
        tk.Label(
            parent, text=title.upper(), font=FONT_LABEL,
            bg=BG_PANEL, fg=ACCENT_GOLD, anchor="w",
        ).pack(anchor="w", pady=(12, 4))

    # ── Public update ─────────────────────────────────────────────────────────

    def update(
            self,
            players: list,
            current_player,
            message: str = "",
            hint: str = "",
            game_over: bool = False,
    ) -> None:
        """Redraw the full sidebar for the current game state."""
        self._refresh_players(players, current_player)
        self.info_label.config(text=message)
        self._set_hint(hint)
        self._render_actions(game_over)

    # ── Player list ───────────────────────────────────────────────────────────

    def _refresh_players(self, players: list, current_player) -> None:
        for w in self.player_rows_frame.winfo_children():
            w.destroy()

        for p in players:
            color    = _PLAYER_COLORS.get(p.color or "", FG_PRIMARY)
            is_curr  = p is current_player
            row_bg   = "#3A404B" if is_curr else BG_SURFACE

            row = tk.Frame(self.player_rows_frame, bg=row_bg, padx=8, pady=6)
            row.pack(fill="x", pady=2)

            tk.Label(row, text="◆", bg=row_bg, fg=color,
                     font=("Segoe UI Symbol", 11)).pack(side="left", padx=(0, 10))
            tk.Label(row, text=p.name, bg=row_bg, fg=color,
                     font=FONT_BODY, anchor="w").pack(side="left")
            tk.Label(row, text=f"{p.score} pts · {p.trains} trains",
                     bg=row_bg, fg=FG_MUTED, font=FONT_HINT).pack(side="right")

        self.player_rows_frame.update_idletasks()
        self.player_canvas.config(height=len(players) * 38 + 8)

    # ── Hint label ────────────────────────────────────────────────────────────

    def _set_hint(self, text: str) -> None:
        if text:
            self.hint_label.config(text=f"ℹ  {text}")
            self.hint_label.pack(fill="x", pady=(0, 6))
        else:
            self.hint_label.config(text="")
            self.hint_label.pack_forget()

    # ── Action buttons ────────────────────────────────────────────────────────

    def _render_actions(self, game_over: bool) -> None:
        for w in self.action_frame.winfo_children():
            w.destroy()

        if game_over:
            tk.Label(
                self.action_frame, text="Game finished.",
                bg=BG_PANEL, fg=FG_MUTED, font=FONT_BODY,
            ).pack(anchor="w", pady=4)
            return

        tk.Label(
            self.action_frame, text="Choose an action for this turn:",
            bg=BG_PANEL, fg=FG_MUTED, font=FONT_BODY,
        ).pack(anchor="w", pady=(0, 6))

        self._action_btn("Draw Train Cards",        self._cbs["on_draw_cards"])
        self._action_btn("Draw Destination Tickets", self._cbs["on_draw_tickets"])

    def _action_btn(self, text: str, command) -> tk.Button:
        btn = tk.Button(
            self.action_frame, text=text, command=command,
            bg=ACCENT_RED, fg="#ffffff",
            activebackground=BTN_HOVER, activeforeground="#ffffff",
            font=FONT_BUTTON, relief="flat", bd=0,
            cursor="hand2", highlightthickness=0,
        )
        btn.pack(fill="x", pady=3, ipady=4)
        btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=ACCENT_RED))
        return btn