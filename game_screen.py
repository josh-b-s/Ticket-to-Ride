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

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.board_frame = tk.Frame(self.frame)
        self.board_frame.pack(side="left", fill="both", expand=True)

        self.side_frame = tk.Frame(self.frame, width=260, padx=10, pady=10)
        self.side_frame.pack(side="right", fill="y")
        self.side_frame.pack_propagate(False)

        self.map_view = MapView(
            self.board_frame,
            self.game,
            on_route_click=self.on_route_click
        )

        self.build_sidebar()
        self.update_sidebar()
        self.refresh_card_ui()

    def build_sidebar(self):
        tk.Label(
            self.side_frame,
            text="Game Screen",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 10))

        self.current_label = tk.Label(self.side_frame, text="")
        self.current_label.pack(pady=5)

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

        tk.Label(self.side_frame, text="Train cards:").pack(anchor="w", pady=(12, 4))
        self.hand_list = tk.Listbox(self.side_frame, height=8)
        self.hand_list.pack(fill="x")

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

        tk.Label(self.side_frame, text="Face-up offer:").pack(anchor="w", pady=(12, 4))
        self.offer_frame = tk.Frame(self.side_frame)
        self.offer_frame.pack(fill="x")

    def update_sidebar(self, message=""):
        current = self.game.current_player()
        self.current_label.config(
            text=f"Current player: {current.name if current else 'None'}"
        )

        self.player_list.delete(0, "end")
        for p in self.game.get_players():
            self.player_list.insert("end", str(p))

        self.info_label.config(text=message)
        self.refresh_card_ui()

    def refresh_card_ui(self):
        current = self.game.current_player()

        self.hand_list.delete(0, "end")
        if current:
            for card in current.train_cards:
                self.hand_list.insert("end", str(card))

        if self.draw_mode:
            self.draw_status_label.config(
                text=f"Draw mode active: {self.draws_remaining} draw(s) left"
            )
        else:
            self.draw_status_label.config(text="")

        self.draw_deck_button.config(state="normal" if self.draw_mode else "disabled")
        self.start_draw_button.config(state="disabled" if self.draw_mode else "normal")

        for widget in self.offer_frame.winfo_children():
            widget.destroy()

        face_up = self.game.train_deck.get_face_up()
        for i, card in enumerate(face_up):
            text = "Empty" if card is None else str(card)
            state = "disabled"

            if self.draw_mode and card is not None:
                if card.is_locomotive() and self.draws_remaining < 2:
                    state = "disabled"
                else:
                    state = "normal"

            btn = tk.Button(
                self.offer_frame,
                text=text,
                width=18,
                command=lambda idx=i: self.draw_from_offer(idx),
                state=state
            )
            btn.pack(fill="x", pady=1)

    def start_draw_action(self):
        if self.draw_mode:
            return

        self.draw_mode = True
        self.draws_remaining = 2
        self.update_sidebar("Choose up to 2 train cards.")

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
        if self.draw_mode:
            messagebox.showinfo("Turn", "Finish drawing train cards first.")
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