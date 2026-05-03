"""Main game screen: layout + turn management."""
import tkinter as tk
from tkinter import messagebox

from dialogs import ask_gray_route_color, ask_ticket_choice
from map_view import MapView
from train_card import TrainCard


class GameScreen:
    def __init__(self, root: tk.Tk, game):
        self.root = root
        self.game = game

        # Turn state
        self._action_mode: str = "main"  # "main" | "draw" | "tickets"
        self._draws_remaining: int = 0
        self._cards_drawn_this_turn: int = 0
        self._pending_tickets: list = []

        self._build_layout()
        self.game.on_game_end = self._on_game_end
        self._deal_initial_tickets()
        self.update_sidebar()

    # ================================================================ layout

    def _build_layout(self) -> None:
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        main_area = tk.Frame(self.frame)
        main_area.pack(fill="both", expand=True)

        board_frame = tk.Frame(main_area)
        board_frame.pack(side="left", fill="both", expand=True)

        self.side_frame = tk.Frame(main_area, width=260, padx=10, pady=10)
        self.side_frame.pack(side="right", fill="y")
        self.side_frame.pack_propagate(False)

        self.bottom_bar = tk.Frame(self.frame, height=190, bg="#222")
        self.bottom_bar.pack(side="bottom", fill="x")
        self.bottom_bar.pack_propagate(False)

        self.map_view = MapView(board_frame, self.game, on_route_click=self._on_route_click)
        self._build_sidebar()
        self._build_bottom_bar()

    def _build_sidebar(self) -> None:
        tk.Label(
            self.side_frame, text="Players", font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(10, 5))

        self.player_list = tk.Listbox(self.side_frame, height=8)
        self.player_list.pack(fill="x")

        tk.Label(
            self.side_frame, text="Turn Information", font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(12, 4))
        self.info_label = tk.Label(
            self.side_frame, text="", wraplength=220, justify="left", anchor="w"
        )
        self.info_label.pack(fill="x", pady=(0, 8))

        tk.Label(
            self.side_frame, text="Actions", font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(4, 2))
        self.action_frame = tk.Frame(self.side_frame)
        self.action_frame.pack(fill="x", pady=10)

    def _build_bottom_bar(self) -> None:
        inner = tk.Frame(self.bottom_bar, bg="#222", padx=10, pady=10)
        inner.pack(fill="both", expand=True)

        self.bottom_player_label = tk.Label(
            inner, text="", fg="white", bg="#222", font=("Arial", 12, "bold")
        )
        self.bottom_player_label.pack(anchor="w")

        self.bottom_stats_label = tk.Label(inner, text="", fg="white", bg="#222")
        self.bottom_stats_label.pack(anchor="w", pady=(0, 8))

        content = tk.Frame(inner, bg="#222")
        content.pack(fill="both", expand=True)

        self.card_list = tk.Listbox(content, height=8)
        self.card_list.pack(side="left", fill="both", expand=True)

        self.ticket_list_bottom = tk.Listbox(content, height=8)
        self.ticket_list_bottom.pack(side="left", fill="both", expand=True)

    # ================================================================ sidebar updates

    def update_sidebar(self, message: str = "") -> None:
        self.player_list.delete(0, "end")
        for p in self.game.get_players():
            color_label = p.color.title() if p.color else "Unassigned"
            self.player_list.insert("end", f"[{color_label}] {p}")

        self.info_label.config(text=message)
        self._render_actions()
        self._update_bottom_bar()

    def _render_actions(self) -> None:
        for w in self.action_frame.winfo_children():
            w.destroy()

        if self._action_mode == "main":
            self._render_main_actions()
        elif self._action_mode == "draw":
            self._render_draw_actions()

    def _render_main_actions(self) -> None:
        if self.game.game_over:
            tk.Label(self.action_frame, text="Game finished. No actions available.").pack(
                pady=4
            )
            return

        tk.Label(
            self.action_frame,
            text="Choose one action for this turn:",
            justify="left",
        ).pack(anchor="w", pady=(0, 4))

        tk.Button(
            self.action_frame,
            text="Draw Train Cards",
            command=self._start_draw_action,
        ).pack(fill="x", pady=2)

        tk.Button(
            self.action_frame,
            text="Draw Destination Tickets",
            command=self._start_ticket_draw,
        ).pack(fill="x", pady=2)

    def _render_draw_actions(self) -> None:
        tk.Label(
            self.action_frame, text=f"Draws remaining: {self._draws_remaining}"
        ).pack(pady=4)

        tk.Button(
            self.action_frame,
            text="Draw From Deck",
            command=self._draw_from_deck,
        ).pack(fill="x", pady=2)

        cancel_label = "Cancel (Back)" if self._cards_drawn_this_turn == 0 else "Finish Turn"
        tk.Button(
            self.action_frame,
            text=cancel_label,
            command=self._cancel_or_finish_draw,
        ).pack(fill="x", pady=2)

        tk.Label(self.action_frame, text="Face-up cards:").pack(pady=(8, 2))
        for i, card in enumerate(self.game.train_deck.get_face_up()):
            can_pick = card is not None and not (
                    card.is_locomotive() and self._draws_remaining < 2
            )
            tk.Button(
                self.action_frame,
                text="Empty" if card is None else str(card),
                state="normal" if can_pick else "disabled",
                command=lambda idx=i: self._draw_from_face_up(idx),
            ).pack(fill="x", pady=1)

    def _update_bottom_bar(self) -> None:
        player = self.game.current_player()
        if not player:
            return

        self.bottom_player_label.config(text=f"{player.name}'s Turn")
        self.bottom_stats_label.config(
            text=(
                f"Score: {player.score}  |  Trains: {player.trains}  |  "
                f"Train cards: {len(player.train_cards)}  |  Tickets: {len(player.destination_tickets)}"
            )
        )

        self.card_list.delete(0, "end")
        self.card_list.insert("end", "Train Cards Summary")
        self.card_list.insert("end", "-" * 24)
        summary = self._build_card_summary(player.train_cards)
        if not summary:
            self.card_list.insert("end", "No cards")
        for color, count in summary:
            self.card_list.insert("end", f"{color.title():<12} x{count}")

        self.ticket_list_bottom.delete(0, "end")
        self.ticket_list_bottom.insert("end", "Destination Tickets")
        self.ticket_list_bottom.insert("end", "-" * 24)
        if not player.destination_tickets:
            self.ticket_list_bottom.insert("end", "No tickets")
        for t in player.destination_tickets:
            self.ticket_list_bottom.insert("end", str(t))

    @staticmethod
    def _build_card_summary(cards: list) -> list[tuple[str, int]]:
        order = TrainCard.COLORS + ["locomotive"]
        counts = {color: 0 for color in order}
        for card in cards:
            if card.color in counts:
                counts[card.color] += 1
        return [(color, counts[color]) for color in order if counts[color] > 0]

    # ================================================================ actions

    # ---- draw train cards ----

    def _start_draw_action(self) -> None:
        if self.game.game_over:
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
        card = self.game.train_deck.face_up[index]
        if card is None:
            return
        if card.is_locomotive() and self._draws_remaining < 2:
            messagebox.showinfo("Rule", "Locomotive must be the first draw.")
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
            self.update_sidebar(f"Drew {card_label}. {self._draws_remaining} left.")

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
            self.update_sidebar("Returned to main menu.")
        else:
            self._finish_draw_action("Finished drawing train cards.")

    # ---- destination tickets ----

    def _start_ticket_draw(self) -> None:
        if self.game.game_over:
            return
        if self._action_mode != "main":
            return
        tickets = self.game.draw_destination_tickets()
        if not tickets:
            messagebox.showinfo("Tickets", "No tickets left in the deck.")
            return
        self._pending_tickets = tickets
        player = self.game.current_player()
        chosen = ask_ticket_choice(self.root, player.name, tickets, min_keep=1)
        if not chosen:
            # Return all to deck without advancing turn
            self.game.destination_deck = tickets + self.game.destination_deck
            self._pending_tickets = []
            return
        self.game.keep_destination_tickets(player, chosen, tickets, advance_turn=True)
        self._pending_tickets = []
        self.update_sidebar("Tickets chosen.")

    def _deal_initial_tickets(self) -> None:
        """Give each player their starting tickets before the game begins."""
        for player in self.game.get_players():
            drawn = self.game.draw_destination_tickets(3)
            if not drawn:
                break
            chosen = ask_ticket_choice(self.root, player.name, drawn, min_keep=2)
            # keep_destination_tickets without advancing the turn counter
            self.game.keep_destination_tickets(
                player, chosen if chosen else drawn[:2], drawn, advance_turn=False
            )

    # ---- route claiming ----

    def _on_route_click(self, route) -> None:
        if self.game.game_over:
            return
        if self._action_mode != "main":
            messagebox.showinfo("Turn", "Finish your current action first.")
            return

        chosen_color = None
        if route.color is None:
            player = self.game.current_player()
            playable_colors = self.game.available_colors_for_gray_route(player, route.length)
            chosen_color = ask_gray_route_color(
                self.root,
                player.name,
                playable_colors,
            )
            if not chosen_color:
                return

        success, message = self.game.claim_route(route, chosen_color)
        if not success:
            messagebox.showinfo("Route", message)
            return

        self.map_view.draw()
        self.update_sidebar(message)

    # ---- game over ----

    def _on_game_end(self, route_lengths: dict) -> None:
        lines = ["Game Over!\n"]
        sorted_players = (
            self.game.final_standings
            if self.game.final_standings
            else sorted(self.game.get_players(), key=lambda p: p.score, reverse=True)
        )
        for p in sorted_players:
            lines.append(
                f"{p.name}: {p.score} pts  "
                f"(tickets: {p.completed_tickets}, "
                f"longest: {route_lengths.get(p, 0)})"
            )
        if not sorted_players:
            lines.append("\nNo winner.")
        else:
            top = sorted_players[0]
            ties = [
                p
                for p in sorted_players
                if self.game._standings_key(p) == self.game._standings_key(top)
            ]
            if len(ties) == 1:
                lines.append(f"\nWinner: {top.name}!")
            else:
                lines.append("\nWinners (tie): " + ", ".join(p.name for p in ties))
        messagebox.showinfo("Game Over", "\n".join(lines))
