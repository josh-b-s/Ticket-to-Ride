# Ticket to Ride – London Prototype
**Team:** DevOops
**Unit:** FIT3077 Software Engineering: Architecture and Design

---

## How to Run

### Option 1 – Executable (Windows x86-64)
1. Navigate to the `game/` folder
2. Double-click `main.exe`

No installation required.

### Option 2 – Run from Source (Windows / macOS / Linux)
**Requirements:** Python 3.10 or higher

1. Navigate to the `game/` folder
2. Run:
```
python main.py
```

No third-party libraries are required. `tkinter` is included with the standard Python installer.

---

## Platform
Tested on **Windows 10/11 (x86-64)**

---

## Repository Structure
```
/game/
    main.py               # Entry point
    main.exe              # Windows executable (x86-64)
    game.py               # Core game logic
    board.py              # Map cities and routes
    player.py             # Player state
    route.py              # Route data
    train_card.py         # Train card
    train_deck.py         # Card deck management
    destination_ticket.py # Destination ticket
    game_screen.py        # Main game UI
    map_view.py           # Board rendering
    setup_screen.py       # Player setup UI
    dialogs.py            # Reusable dialogs
```
