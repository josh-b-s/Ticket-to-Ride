import tkinter as tk
from tkinter import messagebox, simpledialog

from map_view import MapView
from train_card import TrainCard


class GameScreen:
    def __init__(self, root, game):
        self.root = root
        self.game = game

        self.action_mode = "main"  # main | draw | tickets
        self.draws_remaining = 0
        self.cards_drawn_this_turn = 0
        self.drawn_tickets = []

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.main_area = tk.Frame(self.frame)
        self.main_area.pack(fill="both", expand=True)

        self.board_frame = tk.Frame(self.main_area)
        self.board_frame.pack(side="left", fill="both", expand=True)

        self.side_frame = tk.Frame(self.main_area, width=260, padx=10, pady=10)
        self.side_frame.pack(side="right", fill="y")
        self.side_frame.pack_propagate(False)

        self.bottom_bar = tk.Frame(self.frame, height=140, bg="#222")
        self.bottom_bar.pack(side="bottom", fill="x")
        self.bottom_bar.pack_propagate(False)

        self.map_view = MapView(
            self.board_frame,
            self.game,
            on_route_click=self.on_route_click
        )

        self.build_sidebar()
        self.build_bottom_bar()
        self.update_sidebar()
        self.handle_initial_tickets()

    def build_sidebar(self):
        tk.Label(self.side_frame, text="Players:").pack(anchor="w", pady=(10, 5))

        self.player_list = tk.Listbox(self.side_frame, height=8)
        self.player_list.pack(fill="x")

        self.info_label = tk.Label(self.side_frame, text="", wraplength=220, justify="left")
        self.info_label.pack(pady=8)

        self.action_frame = tk.Frame(self.side_frame)
        self.action_frame.pack(fill="x", pady=10)

    def update_sidebar(self, message=""):
        self.player_list.delete(0, "end")
        for p in self.game.get_players():
            self.player_list.insert("end", str(p))

        self.info_label.config(text=message)
        self.render_actions()
        self.update_bottom_bar()

    def render_actions(self):
        for w in self.action_frame.winfo_children():
            w.destroy()

        if self.action_mode == "main":
            tk.Button(
                self.action_frame,
                text="Draw Train Cards",
                command=self.start_draw_action
            ).pack(fill="x", pady=2)

            tk.Button(
                self.action_frame,
                text="Draw Destination Tickets",
                command=self.start_ticket_draw
            ).pack(fill="x", pady=2)

        elif self.action_mode == "draw":
            tk.Label(
                self.action_frame,
                text=f"Draws remaining: {self.draws_remaining}"
            ).pack(pady=4)

            tk.Button(
                self.action_frame,
                text="Draw From Deck",
                command=self.draw_from_deck
            ).pack(fill="x", pady=2)

            self.update_finish_button()

            tk.Button(
                self.action_frame,
                text=self.cancel_or_finish_text,
                command=self.cancel_or_finish_draw
            ).pack(fill="x", pady=2)

            tk.Label(self.action_frame, text="Face-up cards:").pack(pady=(8, 2))

            face_up = self.game.train_deck.get_face_up()

            for i, card in enumerate(face_up):
                text = "Empty" if card is None else str(card)

                can_click = (
                        card is not None and
                        not (card.is_locomotive() and self.draws_remaining < 2)
                )

                tk.Button(
                    self.action_frame,
                    text=text,
                    command=lambda idx=i: self.draw_from_offer(idx),
                    state="normal" if can_click else "disabled"
                ).pack(fill="x", pady=1)

    def start_draw_action(self):
        self.action_mode = "draw"
        self.draws_remaining = 2
        self.cards_drawn_this_turn = 0
        self.update_sidebar("Draw up to 2 train cards.")

    def draw_from_deck(self):
        if self.action_mode != "draw":
            return

        player = self.game.current_player()
        card = self.game.draw_train_card_from_deck(player)

        if card is None:
            messagebox.showinfo("Deck", "No card available.")
            return

        self.cards_drawn_this_turn += 1
        self.draws_remaining -= 1

        if self.draws_remaining <= 0:
            self.finish_draw_action(f"Drew {card}. Turn ends.")
        else:
            self.update_sidebar(f"Drew {card}. {self.draws_remaining} left.")

    def draw_from_offer(self, index):
        if self.action_mode != "draw":
            return

        player = self.game.current_player()
        card = self.game.train_deck.face_up[index]

        if card is None:
            return

        if card.is_locomotive() and self.draws_remaining < 2:
            messagebox.showinfo("Rule", "Locomotive must be first draw.")
            return

        drawn = self.game.draw_train_card_from_face_up(player, index)

        if drawn is None:
            return

        self.cards_drawn_this_turn += 1

        if drawn.is_locomotive():
            self.finish_draw_action(f"Drew {drawn}. Turn ends.")
            return

        self.draws_remaining -= 1

        if self.draws_remaining <= 0:
            self.finish_draw_action(f"Drew {drawn}. Turn ends.")
        else:
            self.update_sidebar(f"Drew {drawn}. {self.draws_remaining} left.")

    def finish_draw_action(self, message=""):
        self.action_mode = "main"
        self.draws_remaining = 0
        self.cards_drawn_this_turn = 0
        self.game.next_player()
        self.update_sidebar(message)

    def cancel_draw(self):
        if self.cards_drawn_this_turn == 0:
            self.action_mode = "main"
            self.update_sidebar("Cancelled.")
        else:
            messagebox.showinfo("Rule", "You must take at least 1 card.")

    def on_route_click(self, route):
        if self.action_mode != "main":
            messagebox.showinfo("Turn", "Finish current action first.")
            return

        chosen_color = None
        if route.color is None:
            chosen_color = simpledialog.askstring(
                "Gray route",
                "Choose color: red, blue, green, yellow, black, orange, pink, white"
            )
            if not chosen_color:
                return

            chosen_color = chosen_color.strip().lower()
            if chosen_color not in TrainCard.COLORS:
                messagebox.showinfo("Error", "Invalid color.")
                return

        success, message = self.game.claim_route(route, chosen_color)

        if not success:
            messagebox.showinfo("Route", message)
            return

        self.map_view.draw()
        self.update_sidebar(message)

    def start_ticket_draw(self):
        if self.action_mode != "main":
            return

        self.drawn_tickets = self.game.draw_destination_tickets()

        if not self.drawn_tickets:
            messagebox.showinfo("Tickets", "No tickets left.")
            return

        self.show_ticket_choice()

    def show_ticket_choice(self):
        win = tk.Toplevel(self.root)
        win.title("Choose Tickets (keep at least 1)")

        vars = []

        for ticket in self.drawn_tickets:
            var = tk.IntVar(value=1)
            tk.Checkbutton(win, text=str(ticket), variable=var).pack(anchor="w")
            vars.append((var, ticket))

        def confirm():
            chosen = [t for v, t in vars if v.get() == 1]

            if len(chosen) < 1:
                messagebox.showinfo("Error", "Keep at least 1 ticket.")
                return

            player = self.game.current_player()
            self.game.choose_destination_tickets(player, chosen, self.drawn_tickets)

            win.destroy()
            self.update_sidebar("Tickets chosen.")

        tk.Button(win, text="Confirm", command=confirm).pack(pady=10)

    def handle_initial_tickets(self):
        for player in self.game.get_players():
            drawn = self.game.draw_destination_tickets(3)

            kept = self.choose_destination_tickets(player, drawn, min_keep=2)

            player.destination_tickets.extend(kept)

            for t in drawn:
                if t not in kept:
                    self.game.destination_deck.insert(0, t)

        self.update_sidebar("Initial tickets chosen.")

    def build_bottom_bar(self):
        self.bottom_inner = tk.Frame(self.bottom_bar, bg="#222", padx=10, pady=10)
        self.bottom_inner.pack(fill="both", expand=True)

        self.bottom_player_label = tk.Label(
            self.bottom_inner, text="", fg="white", bg="#222",
            font=("Arial", 12, "bold")
        )
        self.bottom_player_label.pack(anchor="w")

        self.bottom_stats_label = tk.Label(
            self.bottom_inner, text="", fg="white", bg="#222"
        )
        self.bottom_stats_label.pack(anchor="w", pady=(0, 8))

        self.bottom_content = tk.Frame(self.bottom_inner, bg="#222")
        self.bottom_content.pack(fill="both", expand=True)

        self.card_list = tk.Listbox(self.bottom_content, height=5)
        self.card_list.pack(side="left", fill="both", expand=True)

        self.ticket_list_bottom = tk.Listbox(self.bottom_content, height=5)
        self.ticket_list_bottom.pack(side="left", fill="both", expand=True)

    def update_bottom_bar(self):
        player = self.game.current_player()
        if not player:
            return

        self.bottom_player_label.config(text=f"{player.name}'s Turn")
        self.bottom_stats_label.config(
            text=f"Score: {player.score} | Trains: {player.trains}"
        )

        self.card_list.delete(0, "end")
        for c in player.train_cards:
            self.card_list.insert("end", str(c))

        self.ticket_list_bottom.delete(0, "end")
        for t in player.destination_tickets:
            self.ticket_list_bottom.insert("end", str(t))

    def choose_destination_tickets(self, player, tickets, min_keep=2):
        win = tk.Toplevel(self.root)
        win.title(f"{player.name} - Choose Destination Tickets")

        tk.Label(win, text=f"Select tickets to KEEP (min {min_keep}):").pack(pady=10)

        vars_ = []
        for t in tickets:
            var = tk.BooleanVar(value=True)
            tk.Checkbutton(win, text=str(t), variable=var).pack(anchor="w")
            vars_.append((var, t))

        result = []

        def confirm():
            selected = [t for v, t in vars_ if v.get()]

            if len(selected) < min_keep:
                messagebox.showerror("Error", f"You must keep at least {min_keep} tickets.")
                return

            result.clear()
            result.extend(selected)
            win.destroy()

        tk.Button(win, text="Confirm", command=confirm).pack(pady=10)

        win.grab_set()
        self.root.wait_window(win)

        return result

    def update_finish_button(self):
        if self.cards_drawn_this_turn == 0:
            self.cancel_or_finish_text = "Cancel (Back)"
        else:
            self.cancel_or_finish_text = "Finish Turn"

    def cancel_or_finish_draw(self):
        # CANCEL = go back to main menu, no turn change
        if self.cards_drawn_this_turn == 0:
            self.action_mode = "main"
            self.draws_remaining = 0
            self.update_sidebar("Returned to main menu.")
            return

        # FINISH = valid only if at least 1 card drawn
        self.finish_draw_action("Finished drawing train cards.")