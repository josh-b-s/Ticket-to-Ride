"""Reusable modal dialogs — styled for the One Dark theme."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from game.UI.theme import (
    ACCENT_GOLD, ACCENT_RED, BG_DARK, BG_MAIN, BG_SURFACE,
    BTN_HOVER, BTN_OFF, FG_HINT, FG_MUTED, FG_PRIMARY, GOLD_DIM,
    FONT_BODY, FONT_BUTTON, FONT_HINT, FONT_LABEL, FONT_TITLE,
)
from game.classes.route import RouteColor

#  Card colour helpers (shared with sidebar / bottom-bar) 

CARD_COLORS: dict[str, str] = {
    "blue":       RouteColor.BLUE.value,
    "green":      RouteColor.GREEN.value,
    "yellow":     RouteColor.YELLOW.value,
    "black":      RouteColor.BLACK.value,
    "orange":     RouteColor.ORANGE.value,
    "pink":       RouteColor.PINK.value,
    "locomotive": "#666666",
}


def card_hex(color: str | None) -> str:
    """Return background hex for a card colour name."""
    return CARD_COLORS.get((color or "").lower(), BTN_OFF)


def text_for_bg(hex_color: str) -> str:
    """Return black or white foreground for readability on *hex_color*."""
    h = hex_color.lstrip("#")
    lum = 0.299 * int(h[0:2], 16) + 0.587 * int(h[2:4], 16) + 0.114 * int(h[4:6], 16)
    return "#000000" if lum > 160 else "#ffffff"


#  Private helpers 

def _dialog(root: tk.Tk, title: str) -> tk.Toplevel:
    win = tk.Toplevel(root)
    win.title(title)
    win.configure(bg=BG_MAIN)
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    return win


def _header(win: tk.Toplevel, title: str, subtitle: str = "") -> None:
    hf = tk.Frame(win, bg=BG_DARK, padx=16, pady=12)
    hf.pack(fill="x")
    tk.Label(hf, text=title, bg=BG_DARK, fg=ACCENT_GOLD,
             font=FONT_TITLE, anchor="w").pack(fill="x")
    if subtitle:
        tk.Label(hf, text=subtitle, bg=BG_DARK, fg=FG_MUTED,
                 font=FONT_HINT, anchor="w").pack(fill="x")
    tk.Frame(win, height=1, bg=GOLD_DIM).pack(fill="x")


def _footer(win: tk.Toplevel) -> tk.Frame:
    tk.Frame(win, height=1, bg=GOLD_DIM).pack(fill="x")
    f = tk.Frame(win, bg=BG_MAIN, padx=16, pady=10)
    f.pack(fill="x")
    return f


def _btn(parent: tk.Widget, text: str, command, primary: bool = True) -> tk.Button:
    bg    = ACCENT_RED if primary else BTN_OFF
    hover = BTN_HOVER  if primary else "#4A5060"
    b = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg="#ffffff",
        activebackground=hover, activeforeground="#ffffff",
        font=FONT_BUTTON, relief="flat", bd=0,
        cursor="hand2", highlightthickness=0, padx=16, pady=6,
    )
    b.bind("<Enter>", lambda e: b.config(bg=hover))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


#  Public dialogs 

def ask_ticket_choice(
        root: tk.Tk,
        player_name: str,
        tickets: list,
        min_keep: int = 1,
) -> list:
    """
    Modal: choose which destination tickets to keep.

    Returns the kept tickets (len ≥ min_keep), or [] if closed without
    confirming.
    """
    win = _dialog(root, "Destination Tickets")
    win.result = []

    _header(
        win,
        f"{player_name} — Destination Tickets",
        f"Select tickets to keep  (keep at least {min_keep})",
    )

    body = tk.Frame(win, bg=BG_MAIN, padx=16, pady=10)
    body.pack(fill="both", expand=True)

    vars_and_tickets = [(tk.BooleanVar(value=True), t) for t in tickets]

    for var, ticket in vars_and_tickets:
        row = tk.Frame(
            body, bg=BG_SURFACE, padx=10, pady=7,
            highlightbackground=GOLD_DIM, highlightthickness=1,
        )
        row.pack(fill="x", pady=3)

        tk.Checkbutton(
            row, variable=var,
            bg=BG_SURFACE, fg=FG_PRIMARY, selectcolor=BG_DARK,
            activebackground=BG_SURFACE, activeforeground=FG_PRIMARY,
            highlightthickness=0, bd=0,
        ).pack(side="left")

        tk.Label(
            row, text=str(ticket),
            bg=BG_SURFACE, fg=FG_PRIMARY, font=FONT_BODY, anchor="w",
        ).pack(side="left", padx=(4, 0))

        pts = getattr(ticket, "value", getattr(ticket, "points", None))
        if pts is not None:
            tk.Label(row, text=f"{pts} pts",
                     bg=BG_SURFACE, fg=ACCENT_GOLD, font=FONT_HINT).pack(side="right")

    footer = _footer(win)

    def confirm() -> None:
        chosen = [t for v, t in vars_and_tickets if v.get()]
        if len(chosen) < min_keep:
            messagebox.showerror(
                "Cannot Confirm",
                f"You must keep at least {min_keep} ticket(s).",
                parent=win,
            )
            return
        win.result = chosen
        win.destroy()

    _btn(footer, "Confirm", confirm, primary=True).pack(side="right")

    # During the initial deal (min_keep >= 2) there is no escape — mirror the
    # original behaviour where only Confirm existed.  For mid-game draws
    # (min_keep == 1) a Cancel lets the player decline and return all tickets.
    if min_keep > 1:
        win.protocol("WM_DELETE_WINDOW", lambda: None)   # block the × button
    else:
        _btn(footer, "Cancel", win.destroy, primary=False).pack(side="right", padx=(0, 8))

    root.wait_window(win)
    return win.result


def ask_card_draw(
        root: tk.Tk,
        player_name: str,
        face_up_cards: list,
        draws_remaining: int,
) -> str | None:
    """
    Modal: pick one train card to draw this step.

    Returns:
        ``'deck'``    – draw from the hidden deck
        ``'face_N'``  – take face-up card at index N
        ``None``      – cancelled (only possible when draws_remaining == 2)
    """
    win = _dialog(root, "Draw Train Card")
    win.result = None

    draw_word = "draws" if draws_remaining != 1 else "draw"
    _header(
        win,
        f"{player_name} — Draw Train Card",
        f"{draws_remaining} {draw_word} remaining — click a card to take it",
    )

    body = tk.Frame(win, bg=BG_MAIN, padx=16, pady=10)
    body.pack(fill="both", expand=True)

    def _pick(value: str) -> None:
        win.result = value
        win.destroy()

    #  Face-up cards 
    tk.Label(body, text="FACE-UP CARDS", bg=BG_MAIN, fg=ACCENT_GOLD,
             font=FONT_LABEL, anchor="w").pack(fill="x", pady=(0, 6))

    for i, card in enumerate(face_up_cards):
        is_loco  = card is not None and card.is_locomotive()
        blocked  = card is None or (is_loco and draws_remaining < 2)
        color    = None if card is None else getattr(card, "color", None)
        label    = "Empty" if card is None else str(card)

        if is_loco and draws_remaining < 2:
            label += "  (must be drawn first)"

        bg = card_hex(color) if not blocked else BTN_OFF
        fg = text_for_bg(bg)  if not blocked else FG_HINT

        btn = tk.Button(
            body, text=label,
            bg=bg, fg=fg,
            activebackground=bg, activeforeground=fg,
            font=FONT_BUTTON, relief="flat", bd=0, pady=7,
            cursor="hand2" if not blocked else "arrow",
            highlightthickness=0,
            state="normal" if not blocked else "disabled",
            command=lambda idx=i: _pick(f"face_{idx}"),
        )
        btn.pack(fill="x", pady=2)

    tk.Frame(body, height=1, bg=GOLD_DIM).pack(fill="x", pady=8)

    #  Deck 
    tk.Label(body, text="DECK", bg=BG_MAIN, fg=ACCENT_GOLD,
             font=FONT_LABEL, anchor="w").pack(fill="x", pady=(0, 6))

    deck_btn = tk.Button(
        body, text="Draw from Deck  (random card)",
        bg=BTN_OFF, fg=FG_PRIMARY,
        activebackground=BTN_HOVER, activeforeground="#ffffff",
        font=FONT_BUTTON, relief="flat", bd=0, pady=7,
        cursor="hand2", highlightthickness=0,
        command=lambda: _pick("deck"),
    )
    deck_btn.pack(fill="x", pady=2)
    deck_btn.bind("<Enter>", lambda e: deck_btn.config(bg=BTN_HOVER, fg="#ffffff"))
    deck_btn.bind("<Leave>", lambda e: deck_btn.config(bg=BTN_OFF,   fg=FG_PRIMARY))

    # Cancel only on the first draw
    if draws_remaining == 2:
        footer = _footer(win)
        _btn(footer, "Cancel", win.destroy, primary=False).pack(side="right")

    root.wait_window(win)
    return win.result


def ask_gray_route_color(
        root: tk.Tk,
        player_name: str,
        available_colors: list[str],
) -> str | None:
    """
    Modal: choose a colour to spend on a gray (wild) route.

    Returns the chosen colour in lowercase, or None if cancelled.
    """
    if not available_colors:
        messagebox.showinfo("Gray Route", "No valid colour available for this route.")
        return None

    win = _dialog(root, "Gray Route Colour")
    win.result = None

    _header(
        win,
        f"{player_name} — Gray Route",
        "Choose which colour cards to spend",
    )

    body = tk.Frame(win, bg=BG_MAIN, padx=16, pady=10)
    body.pack(fill="both", expand=True)

    selected = tk.StringVar(value=available_colors[0])

    for color in available_colors:
        row = tk.Frame(
            body, bg=BG_SURFACE, padx=10, pady=7,
            highlightbackground=GOLD_DIM, highlightthickness=1,
        )
        row.pack(fill="x", pady=3)

        tk.Label(row, text="  ", bg=card_hex(color), width=2).pack(side="left", padx=(0, 10))

        tk.Radiobutton(
            row, text=color.title(), value=color, variable=selected,
            bg=BG_SURFACE, fg=FG_PRIMARY, selectcolor=BG_DARK,
            activebackground=BG_SURFACE, activeforeground=FG_PRIMARY,
            highlightthickness=0, bd=0, font=FONT_BODY,
        ).pack(side="left")

    footer = _footer(win)

    def confirm() -> None:
        win.result = selected.get().strip().lower()
        win.destroy()

    _btn(footer, "Confirm", confirm, primary=True).pack(side="right")
    _btn(footer, "Cancel",  win.destroy, primary=False).pack(side="right", padx=(0, 8))

    root.wait_window(win)
    return win.result