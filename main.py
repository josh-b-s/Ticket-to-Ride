import tkinter as tk

from game import Game
from setup_screen import SetupScreen


def main():
    root = tk.Tk()
    root.title("Ticket to Ride Prototype")
    root.geometry("1100x750")

    game = Game()
    root.current_screen = SetupScreen(root, game)

    root.mainloop()


if __name__ == "__main__":
    main()