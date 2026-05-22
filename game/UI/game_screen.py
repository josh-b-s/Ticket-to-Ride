"""game_screen.py — main game screen: layout + turn management."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from game.UI.bottom_bar import BottomBar
from game.UI.dialogs import ask_card_draw, ask_gray_route_color, ask_ticket_choice
from game.UI.map_view import MapView
from game.UI.sidebar import SidebarPanel
from game.UI.theme import BG_DARK, BG_MAIN, BG_PANEL, GOLD_DIM


class GameScreen:
    def __init__(self, root: tk.Tk, game) -> None:
        self.root = root
        self.game = game

        self.root.configure(bg=BG_MAIN)
        self.root.title("Ticket to Ride: London")

        self._build_layout()
        self.game.on_game_end = self._on_game_end
        self._deal_initial_tickets()
        self._refresh()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        outer = tk.Frame(self.root, bg=BG_MAIN)
        outer.pack(fill="both", expand=True)

        main_area = tk.Frame(outer, bg=BG_MAIN)
        main_area.pack(fill="both", expand=True)

        board_frame = tk.Frame(
            main_area, bg=BG_DARK,
            highlightbackground=GOLD_DIM, highlightthickness=1,
        )
        board_frame.pack(side="left", fill="both", expand=True)

        side_frame = tk.Frame(
            main_area, width=290, padx=14, pady=10, bg=BG_PANEL,
            highlightbackground=GOLD_DIM, highlightthickness=1,
        )
        side_frame.pack(side="right", fill="y")
        side_frame.pack_propagate(False)

        bottom_frame = tk.Frame(
            outer, height=200, bg=BG_DARK,
            highlightbackground=GOLD_DIM, highlightthickness=1,
        )
        bottom_frame.pack(side="bottom", fill="x")
        bottom_frame.pack_propagate(False)

        self.map_view  = MapView(board_frame, self.game,
                                 on_route_click=self._on_route_click)
        self.sidebar   = SidebarPanel(side_frame, callbacks={
            "on_draw_cards":   self._start_draw_action,
            "on_draw_tickets": self._start_ticket_draw,
        })
        self.bottom_bar = BottomBar(bottom_frame)

    # ── UI refresh ────────────────────────────────────────────────────────────

    def _refresh(self, message: str = "", hint: str = "") -> None:
        """Sync the full UI to the current game state."""
        self.sidebar.update(
            players=self.game.get_players(),
            current_player=self.game.current_player(),
            message=message,
            hint=hint,
            game_over=self.game.state.game_over,
        )
        self.bottom_bar.update(self.game.current_player())

    # ── Draw train cards ──────────────────────────────────────────────────────

    def _start_draw_action(self) -> None:
        if self.game.state.game_over:
            return

        player         = self.game.current_player()
        draws_remaining = 2

        while draws_remaining > 0:
            face_up = self.game.get_face_up_cards()
            choice  = ask_card_draw(self.root, player.name, face_up, draws_remaining)

            if choice is None:           # "Cancel" — only shown on the first pick
                return

            if choice == "deck":
                card = self.game.draw_train_card_from_deck(player)
                if card is None:
                    messagebox.showinfo("Deck", "No cards available.")
                    if draws_remaining == 2:
                        return           # nothing drawn yet — abort the action
                    break                # already drew one card — end turn

            else:
                idx  = int(choice.split("_")[1])
                card = self.game.draw_train_card_from_face_up(player, idx)
                if card is None:
                    messagebox.showinfo("Error", "Could not draw that card.")
                    if draws_remaining == 2:
                        return
                    break

                if card.is_locomotive():
                    draws_remaining = 0  # locomotive costs both draws
                    break

            draws_remaining -= 1

        self.game.next_player()
        self._refresh("Train cards drawn.")

    # ── Draw destination tickets ──────────────────────────────────────────────

    def _start_ticket_draw(self) -> None:
        if self.game.state.game_over:
            return

        tickets = self.game.draw_destination_tickets()
        if not tickets:
            messagebox.showinfo("Tickets", "No tickets left in the deck.")
            return

        player = self.game.current_player()
        chosen = ask_ticket_choice(self.root, player.name, tickets, min_keep=1)

        if not chosen:
            # Player closed the dialog — return cards to the top of the deck
            self.game.state.destination_deck = tickets + self.game.state.destination_deck
            return

        self.game.keep_destination_tickets(player, chosen, tickets, advance_turn=True)
        self.map_view.draw()
        self._refresh("Tickets chosen.")

    # ── Deal initial tickets ──────────────────────────────────────────────────

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
        if self.game.state.game_over:
            return

        chosen_color = None
        if route.is_gray():
            player   = self.game.current_player()
            playable = self.game.available_colors_for_gray_route(player, route.length)
            chosen_color = ask_gray_route_color(self.root, player.name, playable)
            if not chosen_color:
                return

        result = self.game.claim_route(route, chosen_color)
        if not result.ok:
            messagebox.showinfo("Cannot Claim Route", result.reason)
            self._refresh(result.reason, hint=result.hint)
            return

        self.map_view.draw()
        self._refresh(result.reason)

    # ── Game end ──────────────────────────────────────────────────────────────

    def _on_game_end(self, route_lengths: dict) -> None:
        lines = ["Game Over!\n"]

        standings = (
            self.game.state.final_standings
            or sorted(self.game.get_players(), key=lambda p: p.score, reverse=True)
        )

        for p in standings:
            lines.append(
                f"{p.name}: {p.score} pts  "
                f"(tickets: {getattr(p, 'completed_tickets', 0)}, "
                f"longest: {route_lengths.get(p, 0)})"
            )

        if not standings:
            lines.append("\nNo winner.")
        else:
            top  = standings[0]
            ties = [p for p in standings
                    if self.game._standings_key(p) == self.game._standings_key(top)]
            lines.append(
                f"\nWinner: {top.name}!" if len(ties) == 1
                else "\nWinners (tie): " + ", ".join(p.name for p in ties)
            )

        messagebox.showinfo("Game Over", "\n".join(lines))