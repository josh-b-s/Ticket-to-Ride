"""bottom_bar.py — BottomBar: current player's hand and tickets."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from game.UI.dialogs import card_hex, text_for_bg
from game.UI.theme import (
    ACCENT_GOLD, BG_DARK, BG_PANEL, BG_SURFACE, BTN_HOVER,
    FG_MUTED, FG_PRIMARY, FONT_LABEL, FONT_PLAYER, FONT_SMALL,
    FONT_STATS, GOLD_DIM, _PLAYER_COLORS,
)
from game.classes.train_card import TrainCard


class BottomBar:
    """
    Bottom panel showing the active player's train-card hand and
    destination tickets.
    """

    def __init__(self, parent: tk.Frame) -> None:
        self._build(parent)

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self, parent: tk.Frame) -> None:
        inner = tk.Frame(parent, bg=BG_DARK, padx=14, pady=10)
        inner.pack(fill="both", expand=True)

        self._build_header(inner)
        tk.Frame(inner, height=1, bg=GOLD_DIM).pack(fill="x", pady=(0, 8))
        self._build_content(inner)

    def _build_header(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 8))

        badge = tk.Frame(header, bg=BG_DARK)
        badge.pack(side="left")

        self.dot = tk.Label(
            badge, text="◆", bg=BG_DARK, fg=ACCENT_GOLD,
            font=("Segoe UI Symbol", 11),
        )
        self.dot.pack(side="left", padx=(0, 8))

        self.name_label = tk.Label(
            badge, text="", fg=ACCENT_GOLD, bg=BG_DARK, font=FONT_PLAYER,
        )
        self.name_label.pack(side="left")

        self.stats_label = tk.Label(
            header, text="", fg=FG_MUTED, bg=BG_DARK, font=FONT_STATS,
        )
        self.stats_label.pack(side="left", padx=(14, 0))

    def _build_content(self, parent: tk.Frame) -> None:
        content = tk.Frame(parent, bg=BG_DARK)
        content.pack(fill="both", expand=True)

        self._build_cards_section(content)
        self._build_tickets_section(content)

    def _build_cards_section(self, parent: tk.Frame) -> None:
        section = tk.Frame(parent, bg=BG_DARK)
        section.pack(side="left", fill="both", expand=True, padx=(0, 6))

        tk.Label(
            section, text="TRAIN CARDS", bg=BG_DARK, fg=ACCENT_GOLD,
            font=FONT_LABEL, anchor="w",
        ).pack(fill="x", pady=(0, 3))

        outer = tk.Frame(
            section, bg=BG_SURFACE,
            highlightbackground=GOLD_DIM, highlightthickness=1,
        )
        outer.pack(fill="both", expand=True)

        self.card_frame = tk.Frame(outer, bg=BG_SURFACE, padx=6, pady=6)
        self.card_frame.pack(fill="both", expand=True)

    def _build_tickets_section(self, parent: tk.Frame) -> None:
        section = tk.Frame(parent, bg=BG_DARK)
        section.pack(side="left", fill="both", expand=True)

        tk.Label(
            section, text="DESTINATION TICKETS", bg=BG_DARK, fg=ACCENT_GOLD,
            font=FONT_LABEL, anchor="w",
        ).pack(fill="x", pady=(0, 3))

        outer = tk.Frame(
            section, bg=BG_SURFACE,
            highlightbackground=GOLD_DIM, highlightthickness=1,
        )
        outer.pack(fill="both", expand=True)

        # Styled scrollbar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.Vertical.TScrollbar",
            background=BG_PANEL, troughcolor=BG_DARK, bordercolor=BG_DARK,
            arrowcolor=FG_MUTED, darkcolor=BG_PANEL, lightcolor=BG_PANEL,
            gripcount=0, relief="flat", borderwidth=0,
        )
        style.map("Dark.Vertical.TScrollbar",
                  background=[("active", BTN_HOVER)])

        self.ticket_canvas = tk.Canvas(
            outer, bg=BG_SURFACE, highlightthickness=0, bd=0,
        )
        ticket_scroll = ttk.Scrollbar(
            outer, orient="vertical",
            command=self.ticket_canvas.yview,
            style="Dark.Vertical.TScrollbar",
        )
        self.ticket_canvas.configure(yscrollcommand=ticket_scroll.set)

        ticket_scroll.pack(side="right", fill="y")
        self.ticket_canvas.pack(side="left", fill="both", expand=True)

        self.ticket_frame = tk.Frame(self.ticket_canvas, bg=BG_SURFACE)
        self.ticket_canvas.create_window((0, 0), window=self.ticket_frame, anchor="nw")

        self.ticket_frame.bind(
            "<Configure>",
            lambda e: self.ticket_canvas.configure(
                scrollregion=self.ticket_canvas.bbox("all"),
            ),
        )

        self._bind_mousewheel(outer,               self.ticket_canvas)
        self._bind_mousewheel(self.ticket_canvas,  self.ticket_canvas)

    # ── Public update ─────────────────────────────────────────────────────────

    def update(self, player) -> None:
        """Redraw the bottom bar for *player*."""
        if player is None:
            return
        self._update_header(player)
        self._update_cards(player.train_cards)
        self._update_tickets(player.destination_tickets)

    # ── Header ────────────────────────────────────────────────────────────────

    def _update_header(self, player) -> None:
        color = _PLAYER_COLORS.get(player.color or "", ACCENT_GOLD)
        self.dot.config(fg=color)
        self.name_label.config(text=player.name, fg=color)
        self.stats_label.config(
            text=(
                f"Score: {player.score}   Trains: {player.trains}   "
                f"Cards: {len(player.train_cards)}   "
                f"Tickets: {len(player.destination_tickets)}"
            )
        )

    # ── Train cards ───────────────────────────────────────────────────────────

    def _update_cards(self, train_cards: list) -> None:
        for w in self.card_frame.winfo_children():
            w.destroy()

        summary = self._card_summary(train_cards)
        if not summary:
            tk.Label(
                self.card_frame, text="No cards",
                bg=BG_SURFACE, fg=FG_MUTED, font=FONT_SMALL,
            ).pack(anchor="w", padx=10, pady=6)
            return

        for col, (color, count) in enumerate(summary):
            bg = card_hex(color)
            tk.Label(
                self.card_frame,
                text=f"{color.title()} ×{count}",
                bg=bg, fg=text_for_bg(bg),
                font=FONT_SMALL, padx=8, pady=3,
            ).grid(row=0, column=col, padx=4, pady=4, sticky="ew")
            self.card_frame.grid_columnconfigure(col, weight=1)

    @staticmethod
    def _card_summary(cards: list) -> list[tuple[str, int]]:
        order  = TrainCard.COLORS + ["locomotive"]
        counts = {c: 0 for c in order}
        for card in cards:
            if card.color in counts:
                counts[card.color] += 1
        return [(c, counts[c]) for c in order if counts[c] > 0]

    # ── Destination tickets ───────────────────────────────────────────────────

    def _update_tickets(self, tickets: list) -> None:
        for w in self.ticket_frame.winfo_children():
            w.destroy()

        if not tickets:
            tk.Label(
                self.ticket_frame, text="No tickets",
                bg=BG_SURFACE, fg=FG_MUTED, font=FONT_SMALL,
            ).pack(anchor="w", padx=10, pady=6)
            return

        for ticket in tickets:
            tk.Label(
                self.ticket_frame, text=str(ticket),
                bg=BG_SURFACE, fg=FG_PRIMARY, font=FONT_SMALL,
                anchor="w", justify="left", padx=6, pady=2,
            ).pack(fill="x", padx=3, pady=1)

    # ── Mouse-wheel scrolling ─────────────────────────────────────────────────

    @staticmethod
    def _bind_mousewheel(widget: tk.Widget, canvas: tk.Canvas) -> None:
        def _scroll(event):
            canvas.yview_scroll(int(-event.delta / 120), "units")

        widget.bind("<Enter>", lambda e: (
            widget.bind_all("<MouseWheel>", _scroll),
            widget.bind_all("<Button-4>", lambda ev: canvas.yview_scroll(-1, "units")),
            widget.bind_all("<Button-5>", lambda ev: canvas.yview_scroll( 1, "units")),
        ))
        widget.bind("<Leave>", lambda e: (
            widget.unbind_all("<MouseWheel>"),
            widget.unbind_all("<Button-4>"),
            widget.unbind_all("<Button-5>"),
        ))