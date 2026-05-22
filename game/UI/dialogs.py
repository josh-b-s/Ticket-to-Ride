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
    Modal dialog asking the player which tickets to keep.

    Returns the kept tickets (len >= min_keep), or an empty list if the
    window was closed without confirming.
    """
    win = tk.Toplevel(root)
    win.title(f"{player_name} — Choose Destination Tickets (keep ≥ {min_keep})")
    win.resizable(False, False)
    win.result = []   # written by confirm(); read after wait_window

    tk.Label(win, text=f"Select tickets to KEEP (minimum {min_keep}):", pady=8).pack()

    vars_and_tickets = [(tk.BooleanVar(value=True), t) for t in tickets]
    for var, ticket in vars_and_tickets:
        tk.Checkbutton(win, text=str(ticket), variable=var).pack(anchor="w", padx=16)

    def confirm() -> None:
        chosen = [t for v, t in vars_and_tickets if v.get()]
        if len(chosen) < min_keep:
            messagebox.showerror(
                "Error", f"You must keep at least {min_keep} ticket(s).", parent=win
            )
            return
        win.result = chosen
        win.destroy()

    tk.Button(win, text="Confirm", command=confirm).pack(pady=10)
    win.grab_set()
    root.wait_window(win)
    return win.result


def ask_gray_route_color(
    root: tk.Tk, player_name: str, available_colors: list[str]
) -> str | None:
    """
    Ask the player to choose a colour for a gray route.

    Returns the selected colour in lowercase, or None if cancelled.
    """
    if not available_colors:
        messagebox.showinfo("Gray Route", "No valid colour available for this route.")
        return None

    win = tk.Toplevel(root)
    win.title(f"{player_name} — Choose Colour for Gray Route")
    win.resizable(False, False)
    win.result = None   # written by confirm(); read after wait_window

    tk.Label(win, text="Choose which colour cards to spend:", pady=8).pack(anchor="w", padx=12)

    selected = tk.StringVar(value=available_colors[0])
    for color in available_colors:
        tk.Radiobutton(win, text=color.title(), value=color,
                       variable=selected).pack(anchor="w", padx=20)

    def confirm() -> None:
        win.result = selected.get().strip().lower()
        win.destroy()

    btn_row = tk.Frame(win, pady=10)
    btn_row.pack(fill="x")
    tk.Button(btn_row, text="Confirm", command=confirm,        width=10).pack(side="left",  padx=12)
    tk.Button(btn_row, text="Cancel",  command=win.destroy,    width=10).pack(side="right", padx=12)

    win.grab_set()
    root.wait_window(win)
    return win.result
