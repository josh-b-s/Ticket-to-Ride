# Ticket to Ride – Sprint 3
**Author:** Josh Brian Saputra
**Unit:** FIT3077 Software Engineering: Architecture and Design
**Team:** DevOops

---

## Sprint 3 Extensions
- **Ferries** (required): special routes requiring Locomotive cards, with three-colour substitution support
- **Dynamic Configuration** (pick-from-list): file-based map loading with auto-generated destination tickets via Dijkstra shortest paths
- **Detailed Illegal Move Feedback** (self-defined): precise contextual error messages explaining exactly why a move was rejected

---

## How to Run

### Option 1 – Executable (Windows x86-64)
1. Navigate to the `game/` folder
2. Double-click `TicketToRide.exe`

The `maps/` folder is included alongside the executable. No installation required.

### Option 2 – Run from Source (Windows / macOS / Linux)

**Requirements:** Python 3.10 or higher, Pillow

1. Install Pillow:
```
pip install Pillow
```

2. Navigate to the **project root** (the folder containing the `game/` directory):
```
cd project1
```

3. Run:
```
python game\main.py
```

### Option 3 – Build Executable from Source

1. Install PyInstaller:
```
pip install pyinstaller
```

2. From the **project root**, create a `run.py` file containing:
```python
from game.main import main

if __name__ == "__main__":
    main()
```

3. Build:
```
pyinstaller --onefile --windowed --name "TicketToRide" run.py
```

4. Copy the `game\maps\` folder into `dist\`:
```
xcopy /E /I game\maps dist\maps
```

5. The executable is at `dist\TicketToRide.exe`

---

## Platform
Tested on **Windows 10/11 (x86-64)**

---

## Adding a New Map
Create a new folder inside `game/maps/` containing two files:
- `board.json`: defines cities (with x/y coordinates) and routes (with colour, length, and optional ferry_locos)
- `map.png`: background image displayed on the game board

The map will appear automatically on the setup screen. Destination tickets are generated from the board data with no code changes required.

---

## Repository Structure
```
project1/
├── game/
│   ├── main.py                  # Entry point
│   ├── TicketToRide.exe         # Windows executable (x86-64)
│   │
│   ├── classes/
│   │   ├── board.py             # Map loading from board.json + ticket generation
│   │   ├── destination_deck.py  # Destination ticket draw pile
│   │   ├── destination_ticket.py# Destination ticket dataclass
│   │   ├── game.py              # Game facade
│   │   ├── player.py            # Player state
│   │   ├── route.py             # Route data + ferry card arithmetic
│   │   ├── train_card.py        # Train card
│   │   └── train_deck.py        # Card deck management
│   │
│   ├── services/
│   │   ├── card_service.py      # Train card draw and selection logic
│   │   ├── move_validator.py    # Route claim validation + detailed error messages
│   │   ├── route_service.py     # Route claim transactions
│   │   ├── scoring_service.py   # End-game scoring and longest route
│   │   ├── ticket_service.py    # Destination ticket draw and keep logic
│   │   └── turn_manager.py      # Turn advancement
│   │
│   ├── UI/
│   │   ├── bottom_bar.py        # Active player hand and ticket display
│   │   ├── dialogs.py           # Reusable modal dialogs
│   │   ├── game_screen.py       # Main game screen layout
│   │   ├── map_view.py          # Board rendering with ferry markers
│   │   ├── setup_screen.py      # Map selection and player setup
│   │   ├── sidebar.py           # Player roster and action buttons
│   │   └── theme.py             # Shared colour and font constants
│   │
│   └── maps/
│       ├── London/
│       │   ├── board.json       # London map data
│       │   └── map.png          # London map image
│       └── Melbourne/
│           ├── board.json       # Melbourne map data
│           └── map.png          # Melbourne map image
```