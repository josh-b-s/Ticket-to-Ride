# game_screen.py
"""Main game screen: layout + turn management."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from game.UI.dialogs import ask_gray_route_color, ask_ticket_choice
from game.UI.map_view import MapView
from game.UI.theme import (
    ACCENT_GOLD, ACCENT_RED, BG_DARK, BG_MAIN, BG_PANEL, BG_SURFACE,
    BTN_HOVER, BTN_OFF, FG_HINT, FG_MUTED, FG_PRIMARY, FONT_BODY,
    FONT_BUTTON, FONT_HINT, FONT_PLAYER, FONT_SMALL, FONT_STATS,
    FONT_TITLE, GOLD_DIM, _PLAYER_COLORS,
)
from game.classes.train_card import TrainCard


class GameScreen:
    def __init__(self, root: tk.Tk, game):
        self.root = root
        self.game = game

        self.root.configure(bg=BG_MAIN)
        self.root.title("Ticket to Ride: London")

        self._action_mode: str = "main"
        self._draws_remaining: int = 0
        self._cards_drawn_this_turn: int = 0
        self._pending_tickets: list = []

        self._build_layout()
        self.game.on_game_end = self._on_game_end
        self._deal_initial_tickets()
        self.update_sidebar()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        self.frame = tk.Frame(self.root, bg=BG_MAIN)
        self.frame.pack(fill="both", expand=True)

        main_area = tk.Frame(self.frame, bg=BG_MAIN)
        main_area.pack(fill="both", expand=True)

        board_frame = tk.Frame(
            main_area, bg=BG_DARK,
            highlightbackground=GOLD_DIM, highlightthickness=1,
        )
        board_frame.pack(side="left", fill="both", expand=True)

        self.side_frame = tk.Frame(
            main_area, width=290, padx=14, pady=10, bg=BG_PANEL,
            highlightbackground=GOLD_DIM, highlightthickness=1,
        )
        self.side_frame.pack(side="right", fill="y")
        self.side_frame.pack_propagate(False)

        self.bottom_bar = tk.Frame(
            self.frame, height=200, bg=BG_DARK,
            highlightbackground=GOLD_DIM, highlightthickness=1,
        )
        self.bottom_bar.pack(side="bottom", fill="x")
        self.bottom_bar.pack_propagate(False)

        self.map_view = MapView(board_frame, self.game, on_route_click=self._on_route_click)
        self._build_sidebar()
        self._build_bottom_bar()

    def _build_sidebar(self) -> None:
        self._section_header("Players")

        self.player_list = tk.Listbox(
            self.side_frame, height=6, bg=BG_SURFACE, fg=FG_PRIMARY,
            font=FONT_BODY, bd=0, relief="flat",
            selectbackground=ACCENT_RED, selectforeground=FG_PRIMARY,
            highlightthickness=1, highlightbackground=GOLD_DIM,
            highlightcolor=ACCENT_GOLD, activestyle="none",
        )
        self.player_list.pack(fill="x")

        self._divider()
        self._section_header("Turn Info")

        self.info_label = tk.Label(
            self.side_frame, text="", wraplength=250,
            justify="left", anchor="w", bg=BG_PANEL, fg=FG_PRIMARY, font=FONT_BODY,
        )
        self.info_label.pack(fill="x", pady=(0, 2))

        self.hint_label = tk.Label(
            self.side_frame, text="", wraplength=250,
            justify="left", anchor="w", bg=BG_SURFACE, fg=FG_HINT,
            font=FONT_HINT, padx=8, pady=5,
        )

        self._divider()
        self._section_header("Actions")

        self.action_frame = tk.Frame(self.side_frame, bg=BG_PANEL)
        self.action_frame.pack(fill="x", pady=4)

    def _build_bottom_bar(self) -> None:
        inner = tk.Frame(self.bottom_bar, bg=BG_DARK, padx=14, pady=10)
        inner.pack(fill="both", expand=True)

        header = tk.Frame(inner, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 8))

        self.bottom_player_label = tk.Label(
            header, text="", fg=ACCENT_GOLD, bg=BG_DARK, font=FONT_PLAYER,
        )
        self.bottom_player_label.pack(side="left")

        self.bottom_stats_label = tk.Label(
            header, text="", fg=FG_MUTED, bg=BG_DARK, font=FONT_STATS,
        )
        self.bottom_stats_label.pack(side="left", padx=(14, 0))

        tk.Frame(inner, height=1, bg=GOLD_DIM).pack(fill="x", pady=(0, 8))

        content = tk.Frame(inner, bg=BG_DARK)
        content.pack(fill="both", expand=True)

        list_opts = dict(
            height=5, bg=BG_SURFACE, fg=FG_PRIMARY, font=FONT_SMALL,
            bd=0, relief="flat", selectbackground=ACCENT_RED,
            selectforeground=FG_PRIMARY, highlightthickness=1,
            highlightbackground=GOLD_DIM, highlightcolor=ACCENT_GOLD,
            activestyle="none",
        )

        self.card_list = tk.Listbox(content, **list_opts)
        self.card_list.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.ticket_list_bottom = tk.Listbox(content, **list_opts)
        self.ticket_list_bottom.pack(side="left", fill="both", expand=True)

    # ── Sidebar helpers ───────────────────────────────────────────────────────

    def _section_header(self, title: str) -> None:
        tk.Label(
            self.side_frame, text=title.upper(),
            font=("Georgia", 9, "bold"), bg=BG_PANEL, fg=ACCENT_GOLD, anchor="w",
        ).pack(anchor="w", pady=(12, 4))

    def _divider(self) -> None:
        tk.Frame(self.side_frame, height=1, bg=GOLD_DIM).pack(fill="x", pady=(4, 0))

    def _styled_button(self, parent, primary: bool = True, **kwargs) -> tk.Button:
        bg_normal = ACCENT_RED if primary else BTN_OFF
        bg_hover  = BTN_HOVER  if primary else "#3d2814"
        fg_normal = FG_PRIMARY if primary else FG_MUTED

        btn = tk.Button(
            parent, bg=bg_normal, fg=fg_normal, font=FONT_BUTTON,
            relief="flat", bd=0, activebackground=bg_hover,
            activeforeground=FG_PRIMARY, cursor="hand2",
            highlightthickness=0, disabledforeground=FG_MUTED, **kwargs,
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=bg_hover)   if btn["state"] == "normal" else None)
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_normal)  if btn["state"] == "normal" else None)
        return btn

    def _set_hint(self, text: str) -> None:
        if text:
            self.hint_label.config(text=f"\u2551  {text}")
            self.hint_label.pack(fill="x", pady=(0, 6))
        else:
            self.hint_label.config(text="")
            self.hint_label.pack_forget()

    # ── Sidebar update ────────────────────────────────────────────────────────

    def update_sidebar(self, message: str = "", hint: str = "") -> None:
        self.player_list.delete(0, "end")
        for i, p in enumerate(self.game.get_players()):
            color_label = p.color.title() if p.color else "\u2014"
            self.player_list.insert("end", f"  {color_label:<8}  {p}")
            fg = _PLAYER_COLORS.get(p.color or "", FG_PRIMARY)
            self.player_list.itemconfig(i, fg=fg)

        self.info_label.config(text=message)
        self._set_hint(hint)
        self._render_actions()
        self._update_bottom_bar()

    # ── Action panel rendering ────────────────────────────────────────────────

    def _render_actions(self) -> None:
        for w in self.action_frame.winfo_children():
            w.destroy()

        if self._action_mode == "main":
            self._render_main_actions()
        elif self._action_mode == "draw":
            self._render_draw_actions()

    def _render_main_actions(self) -> None:
        if getattr(self.game, "game_over", False):
            tk.Label(
                self.action_frame, text="Game finished.",
                bg=BG_PANEL, fg=FG_MUTED, font=FONT_BODY,
            ).pack(anchor="w", pady=4)
            return

        tk.Label(
            self.action_frame, text="Choose an action for this turn:",
            bg=BG_PANEL, fg=FG_MUTED, font=("Georgia", 9),
        ).pack(anchor="w", pady=(0, 6))

        self._styled_button(
            self.action_frame, primary=True,
            text="Draw Train Cards", command=self._start_draw_action,
        ).pack(fill="x", pady=3, ipady=4)

        self._styled_button(
            self.action_frame, primary=False,
            text="Draw Destination Tickets", command=self._start_ticket_draw,
        ).pack(fill="x", pady=3, ipady=4)

    def _render_draw_actions(self) -> None:
        tk.Label(
            self.action_frame, text=f"Draws remaining: {self._draws_remaining}",
            bg=BG_PANEL, fg=ACCENT_GOLD, font=FONT_TITLE,
        ).pack(pady=(0, 6))

        self._styled_button(
            self.action_frame, primary=True,
            text="Draw From Deck", command=self._draw_from_deck,
        ).pack(fill="x", pady=3, ipady=4)

        cancel_label = "Cancel" if self._cards_drawn_this_turn == 0 else "Finish Turn"
        self._styled_button(
            self.action_frame, primary=False,
            text=cancel_label, command=self._cancel_or_finish_draw,
        ).pack(fill="x", pady=3, ipady=4)

        tk.Label(
            self.action_frame, text="Face-up cards:",
            bg=BG_PANEL, fg=FG_MUTED, font=("Georgia", 9),
        ).pack(anchor="w", pady=(10, 4))

        face_up = self.game.get_face_up_cards()
        for i, card in enumerate(face_up):
            can_pick = card is not None and not (card.is_locomotive() and self._draws_remaining < 2)
            self._styled_button(
                self.action_frame, primary=can_pick,
                text="Empty" if card is None else str(card),
                state="normal" if can_pick else "disabled",
                command=lambda idx=i: self._draw_from_face_up(idx),
            ).pack(fill="x", pady=2, ipady=3)

    # ── Bottom bar ────────────────────────────────────────────────────────────

    def _update_bottom_bar(self) -> None:
        player = self.game.current_player()
        if not player:
            return

        self.bottom_player_label.config(text=player.name)
        self.bottom_stats_label.config(
            text=(
                f"Score: {player.score}   Trains: {player.trains}   "
                f"Cards: {len(player.train_cards)}   Tickets: {len(player.destination_tickets)}"
            )
        )

        self.card_list.delete(0, "end")
        self.card_list.insert("end", "  TRAIN CARDS")
        self.card_list.insert("end", "  " + "\u2500" * 20)
        summary = self._build_card_summary(player.train_cards)
        if not summary:
            self.card_list.insert("end", "  No cards")
        for color, count in summary:
            self.card_list.insert("end", f"  {color.title():<13} \u00d7{count}")

        self.ticket_list_bottom.delete(0, "end")
        self.ticket_list_bottom.insert("end", "  DESTINATION TICKETS")
        self.ticket_list_bottom.insert("end", "  " + "\u2500" * 20)
        if not player.destination_tickets:
            self.ticket_list_bottom.insert("end", "  No tickets")
        for t in player.destination_tickets:
            self.ticket_list_bottom.insert("end", f"  {t}")

    @staticmethod
    def _build_card_summary(cards: list) -> list[tuple[str, int]]:
        order = TrainCard.COLORS + ["locomotive"]
        counts = {color: 0 for color in order}
        for card in cards:
            if card.color in counts:
                counts[card.color] += 1
        return [(color, counts[color]) for color in order if counts[color] > 0]

    # ── Draw actions ──────────────────────────────────────────────────────────

    def _start_draw_action(self) -> None:
        if getattr(self.game, "game_over", False):
            return
        self._action_mode = "draw"
        self._draws_remaining = 2
        self._cards_drawn_this_turn = 0
        self.update_sidebar("Draw up to 2 train cards.")

    def _draw_from_deck(self) -> None:
        if self._action_mode != "draw":
            return
        player = self.game.current_player()
        card = self.game.draw_train_card_from_deck(player)
        if card is None:
            messagebox.showinfo("Deck", "No cards available.")
            return
        self._register_draw(str(card))

    def _draw_from_face_up(self, index: int) -> None:
        if self._action_mode != "draw":
            return

        face_up = self.game.get_face_up_cards()
        if not (0 <= index < len(face_up)):
            return

        card = face_up[index]
        if card is None:
            return

        if card.is_locomotive() and self._draws_remaining < 2:
            messagebox.showinfo(
                "Rule Reminder",
                "A locomotive must be drawn first \u2014 it uses both draws.",
            )
            return

        drawn = self.game.draw_train_card_from_face_up(self.game.current_player(), index)
        if drawn is None:
            return

        if drawn.is_locomotive():
            self._finish_draw_action(f"Drew {drawn}. Turn ends.")
            return

        self._register_draw(str(drawn))

    def _register_draw(self, card_label: str) -> None:
        self._cards_drawn_this_turn += 1
        self._draws_remaining -= 1
        if self._draws_remaining <= 0:
            self._finish_draw_action(f"Drew {card_label}. Turn ends.")
        else:
            self.update_sidebar(f"Drew {card_label}. {self._draws_remaining} draw left.")

    def _finish_draw_action(self, message: str = "") -> None:
        self._action_mode = "main"
        self._draws_remaining = 0
        self._cards_drawn_this_turn = 0
        self.game.next_player()
        self.update_sidebar(message)

    def _cancel_or_finish_draw(self) -> None:
        if self._cards_drawn_this_turn == 0:
            self._action_mode = "main"
            self._draws_remaining = 0
            self.update_sidebar()
        else:
            self._finish_draw_action("Finished drawing train cards.")

    # ── Ticket actions ────────────────────────────────────────────────────────

    def _start_ticket_draw(self) -> None:
        if getattr(self.game, "game_over", False) or self._action_mode != "main":
            return

        tickets = self.game.draw_destination_tickets()
        if not tickets:
            messagebox.showinfo("Tickets", "No tickets left in the deck.")
            return

        self._pending_tickets = tickets
        player = self.game.current_player()
        chosen = ask_ticket_choice(self.root, player.name, tickets, min_keep=1)

        if not chosen:
            self.game.destination_deck = tickets + self.game.destination_deck
            self._pending_tickets = []
            return

        self.game.keep_destination_tickets(player, chosen, tickets, advance_turn=True)
        self._pending_tickets = []
        self.map_view.draw()
        self.update_sidebar("Tickets chosen.")

    def _deal_initial_tickets(self) -> None:
        for player in self.game.get_players():
            drawn = self.game.draw_destination_tickets(3)
            if not drawn:
                break
            chosen = ask_ticket_choice(self.root, player.name, drawn, min_keep=2)
            if not chosen:
                chosen = drawn[:min(2, len(drawn))]
            self.game.keep_destination_tickets(player, chosen, drawn, advance_turn=False)

    # ── Route click ───────────────────────────────────────────────────────────

    def _on_route_click(self, route) -> None:
        if getattr(self.game, "game_over", False):
            return
        if self._action_mode != "main":
            messagebox.showinfo("Turn", "Finish your current action first.")
            return

        self._set_hint("")

        chosen_color = None
        if route.is_gray():
            player = self.game.current_player()
            playable_colors = self.game.available_colors_for_gray_route(player, route.length)
            chosen_color = ask_gray_route_color(self.root, player.name, playable_colors)
            if not chosen_color:
                return

        result = self.game.claim_route(route, chosen_color)

        if not result.ok:
            messagebox.showinfo("Cannot Claim Route", result.reason)
            self.update_sidebar(result.reason, hint=result.hint)
            return

        self.map_view.draw()
        self.update_sidebar(result.reason)

    # ── Game end ──────────────────────────────────────────────────────────────

    def _on_game_end(self, route_lengths: dict) -> None:
        lines = ["Game Over!\n"]

        sorted_players = (
            self.game.final_standings
            if getattr(self.game, "final_standings", None)
            else sorted(self.game.get_players(), key=lambda p: p.score, reverse=True)
        )

        for p in sorted_players:
            lines.append(
                f"{p.name}: {p.score} pts  "
                f"(tickets: {getattr(p, 'completed_tickets', 0)}, "
                f"longest: {route_lengths.get(p, 0)})"
            )

        if not sorted_players:
            lines.append("\nNo winner.")
        else:
            top = sorted_players[0]
            # Use Game._standings_key so tie logic is consistent with sorting
            ties = [p for p in sorted_players if self.game._standings_key(p) == self.game._standings_key(top)]
            if len(ties) == 1:
                lines.append(f"\nWinner: {top.name}!")
            else:
                lines.append("\nWinners (tie): " + ", ".join(p.name for p in ties))

        messagebox.showinfo("Game Over", "\n".join(lines))