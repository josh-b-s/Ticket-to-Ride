import tkinter as tk
from tkinter import messagebox, simpledialog

from map_view import MapView
from train_card import TrainCard


class GameScreen:
    def __init__(self, root, game):
        self.root = root
        self.game = game

        self.draw_mode = False
        self.draws_remaining = 0
        self.ticket_mode = False
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
        self.refresh_card_ui()
        self.handle_initial_tickets()

    def build_sidebar(self):
        tk.Label(self.side_frame, text="Players:").pack(anchor="w", pady=(15, 5))

        self.player_list = tk.Listbox(self.side_frame, height=10)
        self.player_list.pack(fill="x")

        tk.Label(
            self.side_frame,
            text="Click a route on the board to claim it.",
            fg="gray",
            wraplength=220
        ).pack(pady=12)

        self.info_label = tk.Label(self.side_frame, text="", wraplength=220, justify="left")
        self.info_label.pack(pady=6)

        tk.Label(self.side_frame, text="Draw Train Cards").pack(anchor="w", pady=(12, 4))

        self.offer_frame = tk.Frame(self.side_frame)
        self.offer_frame.pack(fill="x")

        self.draw_status_label = tk.Label(self.side_frame, text="")
        self.draw_status_label.pack(pady=(10, 6))

        self.start_draw_button = tk.Button(
            self.side_frame,
            text="Draw Train Cards",
            command=self.start_draw_action
        )
        self.start_draw_button.pack(fill="x", pady=2)

        self.draw_deck_button = tk.Button(
            self.side_frame,
            text="Draw From Deck",
            command=self.draw_from_deck
        )
        self.draw_deck_button.pack(fill="x", pady=2)

        self.draw_ticket_button = tk.Button(
            self.side_frame,
            text="Draw Destination Tickets",
            command=self.start_ticket_draw
        )
        self.draw_ticket_button.pack(fill="x", pady=2)

        self.finish_draw_button = tk.Button(
            self.side_frame,
            text="Finish Drawing",
            command=lambda: self.finish_draw_action("Finished drawing early.")
        )
        self.finish_draw_button.pack(fill="x", pady=2)

        tk.Label(self.side_frame, text="Face-up offer:").pack(anchor="w", pady=(12, 4))
        self.offer_frame = tk.Frame(self.side_frame)
        self.offer_frame.pack(fill="x")

        tk.Label(self.side_frame, text="Destination Tickets:").pack(anchor="w", pady=(12, 4))
        self.ticket_list = tk.Listbox(self.side_frame, height=6)
        self.ticket_list.pack(fill="x")

    def update_sidebar(self, message=""):
        self.player_list.delete(0, "end")
        for p in self.game.get_players():
            self.player_list.insert("end", str(p))

        self.info_label.config(text=message)
        self.refresh_card_ui()
        self.update_bottom_bar()

    def refresh_card_ui(self):
        current = self.game.current_player()

        if self.draw_mode:
            self.draw_status_label.config(
                text=f"Draw mode active: {self.draws_remaining} draw(s) left"
            )
        else:
            self.draw_status_label.config(text="")

        self.draw_deck_button.config(state="normal" if self.draw_mode else "disabled")
        self.start_draw_button.config(state="disabled" if self.draw_mode else "normal")
        self.finish_draw_button.config(
            state="normal" if self.draw_mode and self.draws_remaining == 1 else "disabled"
        )

        for widget in self.offer_frame.winfo_children():
            widget.destroy()

        face_up = self.game.train_deck.get_face_up()

        for i, card in enumerate(face_up):
            text = "Empty" if card is None else str(card)

            can_click = (
                    self.draw_mode
                    and card is not None
                    and not (card.is_locomotive() and self.draws_remaining < 2)
            )

            btn = tk.Button(
                self.offer_frame,
                text=text,
                width=20,
                height=2,
                command=lambda idx=i: self.draw_from_offer(idx),
                state="normal" if can_click else "disabled"
            )
            btn.pack(fill="x", pady=2)

        self.ticket_list.delete(0, "end")
        if current:
            for ticket in current.destination_tickets:
                self.ticket_list.insert("end", str(ticket))

    def start_draw_action(self):
        if self.draw_mode:
            return

        self.draw_mode = True
        self.draws_remaining = 2
        self.update_sidebar("Draw up to 2 train cards (you may stop after 1).")

    def draw_from_deck(self):
        if not self.draw_mode:
            return

        player = self.game.current_player()
        if player is None:
            return

        card = self.game.draw_train_card_from_deck(player)
        if card is None:
            messagebox.showinfo("Deck", "No card available.")
            return

        self.draws_remaining -= 1

        if self.draws_remaining <= 0:
            self.finish_draw_action(f"Drew {card}. Turn ends.")
            return

        self.update_sidebar(f"Drew {card}. {self.draws_remaining} draw(s) left.")

    def draw_from_offer(self, index):
        if not self.draw_mode:
            return

        player = self.game.current_player()
        if player is None:
            return

        card = self.game.train_deck.face_up[index]
        if card is None:
            messagebox.showinfo("Offer", "That slot is empty.")
            return

        if card.is_locomotive() and self.draws_remaining < 2:
            messagebox.showinfo(
                "Rule",
                "A face-up locomotive can only be taken as your first draw."
            )
            return

        drawn = self.game.draw_train_card_from_face_up(player, index)
        if drawn is None:
            messagebox.showinfo("Offer", "That card is no longer available.")
            return

        if drawn.is_locomotive():
            self.finish_draw_action(f"Drew {drawn}. Turn ends.")
            return

        self.draws_remaining -= 1

        if self.draws_remaining <= 0:
            self.finish_draw_action(f"Drew {drawn}. Turn ends.")
            return

        self.update_sidebar(f"Drew {drawn}. {self.draws_remaining} draw(s) left.")

    def finish_draw_action(self, message=""):
        self.draw_mode = False
        self.draws_remaining = 0
        self.game.next_player()
        self.update_sidebar(message)

    def on_route_click(self, route):
        if self.draw_mode or self.ticket_mode:
            messagebox.showinfo("Turn", "Finish current action first.")
            return

        chosen_color = None
        if route.color is None:
            chosen_color = simpledialog.askstring(
                "Gray route",
                "Choose a color for this gray route:\n"
                "red, blue, green, yellow, black, orange, pink, white"
            )
            if chosen_color is None:
                return

            chosen_color = chosen_color.strip().lower()
            if chosen_color not in TrainCard.COLORS:
                messagebox.showinfo("Error", "Invalid color choice.")
                return

        success, message = self.game.claim_route(route, chosen_color=chosen_color)

        if not success:
            messagebox.showinfo("Route", message)
            return

        self.map_view.draw()
        self.update_sidebar(message)

    def start_ticket_draw(self):
        if self.draw_mode or self.ticket_mode:
            return

        self.ticket_mode = True
        self.drawn_tickets = self.game.draw_destination_tickets()

        if not self.drawn_tickets:
            messagebox.showinfo("Tickets", "No tickets left.")
            self.ticket_mode = False
            return

        self.show_ticket_choice()

    def show_ticket_choice(self):
        win = tk.Toplevel(self.root)
        win.title("Choose Tickets (keep at least 1)")

        vars = []

        for ticket in self.drawn_tickets:
            var = tk.IntVar(value=1)  # default keep all
            chk = tk.Checkbutton(win, text=str(ticket), variable=var)
            chk.pack(anchor="w")
            vars.append((var, ticket))

        def confirm():
            chosen = [t for v, t in vars if v.get() == 1]

            player = self.game.current_player()
            success, msg = self.game.choose_destination_tickets(
                player, chosen, self.drawn_tickets
            )

            if not success:
                messagebox.showinfo("Error", msg)
                return

            self.ticket_mode = False
            self.drawn_tickets = []
            win.destroy()
            self.update_sidebar(msg)

        tk.Button(win, text="Confirm", command=confirm).pack(pady=10)

    def choose_destination_tickets(self, player, tickets, min_keep=2):
        win = tk.Toplevel(self.root)
        win.title(f"{player.name} - Choose Destination Tickets")

        tk.Label(win, text="Select tickets to KEEP (min 2):").pack(pady=10)

        vars_ = []
        for t in tickets:
            var = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(win, text=str(t), variable=var, anchor="w", justify="left")
            chk.pack(fill="x", padx=10, pady=2)
            vars_.append(var)

        result = []

        def confirm():
            selected = [t for t, v in zip(tickets, vars_) if v.get()]
            if len(selected) < min_keep:
                messagebox.showerror("Error", f"You must keep at least {min_keep} tickets.")
                return
            result.extend(selected)
            win.destroy()

        tk.Button(win, text="Confirm", command=confirm).pack(pady=10)

        win.grab_set()
        win.wait_window()

        return result

    def handle_initial_tickets(self):
        for player in self.game.get_players():
            drawn = self.game.draw_destination_tickets(3)
            kept = self.choose_destination_tickets(player, drawn, min_keep=2)

            player.destination_tickets.extend(kept)

            # return unkept cards to bottom of deck
            for t in drawn:
                if t not in kept:
                    self.game.destination_deck.insert(0, t)

    def build_bottom_bar(self):
        self.bottom_inner = tk.Frame(self.bottom_bar, bg="#222", padx=10, pady=10)
        self.bottom_inner.pack(fill="both", expand=True)

        # Player info
        self.bottom_player_label = tk.Label(
            self.bottom_inner, text="", fg="white", bg="#222",
            font=("Arial", 12, "bold")
        )
        self.bottom_player_label.pack(anchor="w")

        self.bottom_stats_label = tk.Label(
            self.bottom_inner, text="", fg="white", bg="#222"
        )
        self.bottom_stats_label.pack(anchor="w", pady=(0, 8))

        # Cards + tickets split
        self.bottom_content = tk.Frame(self.bottom_inner, bg="#222")
        self.bottom_content.pack(fill="both", expand=True)

        # Cards
        self.card_frame = tk.Frame(self.bottom_content, bg="#222")
        self.card_frame.pack(side="left", fill="both", expand=True)

        tk.Label(self.card_frame, text="Train Cards", fg="white", bg="#222").pack(anchor="w")

        self.card_list = tk.Listbox(self.card_frame, height=5)
        self.card_list.pack(fill="both", expand=True)

        # Tickets
        self.ticket_frame = tk.Frame(self.bottom_content, bg="#222")
        self.ticket_frame.pack(side="left", fill="both", expand=True)

        tk.Label(self.ticket_frame, text="Tickets", fg="white", bg="#222").pack(anchor="w")

        self.ticket_list_bottom = tk.Listbox(self.ticket_frame, height=5)
        self.ticket_list_bottom.pack(fill="both", expand=True)

    def update_bottom_bar(self):
        player = self.game.current_player()
        if not player:
            return

        self.bottom_player_label.config(text=f"{player.name}'s Turn")
        self.bottom_stats_label.config(
            text=f"Score: {player.score} | Trains: {player.trains}"
        )

        # cards
        self.card_list.delete(0, "end")
        for c in player.train_cards:
            self.card_list.insert("end", str(c))

        # tickets
        self.ticket_list_bottom.delete(0, "end")
        for t in player.destination_tickets:
            self.ticket_list_bottom.insert("end", str(t))