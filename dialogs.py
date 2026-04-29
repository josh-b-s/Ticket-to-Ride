"""Reusable modal dialogs for Ticket to Ride."""
import tkinter as tk
from tkinter import messagebox


def ask_ticket_choice(
        root: tk.Tk,
        player_name: str,
        tickets: list,
        min_keep: int = 1,
) -> list:
    """
    Show a modal dialog asking the player to choose tickets to keep.
    Returns the list of kept tickets (guaranteed len >= min_keep),
    or an empty list if the window was closed without confirming.
    """
    win = tk.Toplevel(root)
    win.title(f"{player_name} — Choose Destination Tickets (keep ≥ {min_keep})")
    win.resizable(False, False)

    tk.Label(win, text=f"Select tickets to KEEP (minimum {min_keep}):", pady=8).pack()

    vars_and_tickets = [(tk.BooleanVar(value=True), t) for t in tickets]
    for var, ticket in vars_and_tickets:
        tk.Checkbutton(win, text=str(ticket), variable=var).pack(anchor="w", padx=16)

    result: list = []

    def confirm() -> None:
        chosen = [t for v, t in vars_and_tickets if v.get()]
        if len(chosen) < min_keep:
            messagebox.showerror(
                "Error", f"You must keep at least {min_keep} ticket(s).", parent=win
            )
            return
        result.extend(chosen)
        win.destroy()

    tk.Button(win, text="Confirm", command=confirm).pack(pady=10)
    win.grab_set()
    root.wait_window(win)
    return result
