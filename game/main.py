import tkinter as tk

from game.UI.setup_screen import SetupScreen
from game.classes.game import Game


def main() -> None:
    root = tk.Tk()
    root.title("Ticket to Ride Prototype")
    root.geometry("1100x750")

    game = Game()
    root.current_screen = SetupScreen(root, game)

    root.mainloop()


if __name__ == "__main__":
    main()
