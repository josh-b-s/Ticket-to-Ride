"""setup_screen.py - player entry and map selection."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageEnhance, ImageTk

from game.UI.game_screen import GameScreen
from game.UI.theme import (
    ACCENT_GOLD, ACCENT_RED, BG_ENTRY, BG_MAIN as BG, BG_PANEL,
    BG_SURFACE, BTN_HOVER, BTN_OFF, FG_MUTED, FG_PRIMARY, FONT_BTN,
    FONT_ENTRY, FONT_HERO, FONT_HINT, FONT_LABEL, FONT_BODY, GOLD_DIM,
    PLAYER_SLOTS,
)

_MAPS_DIR = Path(__file__).parent.parent.parent / "maps"

# Map card dimensions
_CARD_W = 180
_CARD_H = 110

# Image brightness when not selected (0.0 = black, 1.0 = original)
_IMG_DIM    = 0.15
_IMG_SELECT = 0.30

_BORDER_NORMAL   = GOLD_DIM
_BORDER_SELECTED = ACCENT_GOLD
_OVERLAY_NORMAL  = "#1a1d23cc"   # semi-transparent dark tint label colour
_LABEL_NORMAL    = FG_MUTED
_LABEL_SELECTED  = ACCENT_GOLD


def _find_maps() -> list[Path]:
    """Return sorted paths of valid map folders (must contain board.json + map.png)."""
    if not _MAPS_DIR.is_dir():
        return []
    return sorted(
        p for p in _MAPS_DIR.iterdir()
        if p.is_dir()
        and (p / "board.json").exists()
        and (p / "map.png").exists()
    )


def _make_card_image(
    map_path: Path, brightness: float
) -> ImageTk.PhotoImage | None:
    """Load map.png, resize to card size, and apply brightness."""
    png = map_path / "map.png"
    if not png.exists():
        return None
    try:
        img = Image.open(png).convert("RGB")
        img = img.resize((_CARD_W, _CARD_H), Image.Resampling.LANCZOS)
        img = ImageEnhance.Brightness(img).enhance(brightness)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class SetupScreen:
    def __init__(self, root: tk.Tk, game) -> None:
        self.root  = root
        self.game  = game
        self.root.configure(bg=BG)

        self._selected_map: Path | None = None

        # Canvas widgets keyed by map path (used for highlight updates)
        self._map_canvases: dict[Path, tk.Canvas] = {}
        self._map_name_ids: dict[Path, int]        = {}

        # PhotoImage references must be kept alive or GC will blank them
        self._img_dim:    dict[Path, ImageTk.PhotoImage | None] = {}
        self._img_bright: dict[Path, ImageTk.PhotoImage | None] = {}
        self._img_ids:    dict[Path, int]                        = {}

        self.frame = tk.Frame(self.root, bg=BG)
        self.frame.pack(fill="both", expand=True)

        self._build_ui()

    # --- Build ---

    def _build_ui(self) -> None:
        centre = tk.Frame(self.frame, bg=BG)
        centre.pack(expand=True)

        tk.Label(
            centre, text="TICKET TO RIDE",
            font=FONT_HERO, bg=BG, fg=ACCENT_GOLD,
        ).pack()

        tk.Frame(centre, height=1, bg=ACCENT_GOLD).pack(fill="x", pady=16)

        tk.Label(
            centre, text="SELECT A MAP",
            font=FONT_LABEL, bg=BG, fg=ACCENT_GOLD,
        ).pack(anchor="w", pady=(0, 8))

        self._build_map_picker(centre)

        tk.Frame(centre, height=1, bg=GOLD_DIM).pack(fill="x", pady=16)

        tk.Label(
            centre, text="ENTER PLAYERS  (2 – 5)",
            font=FONT_LABEL, bg=BG, fg=ACCENT_GOLD,
        ).pack(anchor="w", pady=(0, 8))

        self.entries: list[tuple[str, tk.Entry]] = []
        for color_name, hex_color, label in PLAYER_SLOTS:
            self._build_player_row(centre, color_name, hex_color, label)

        tk.Frame(centre, height=1, bg=ACCENT_GOLD).pack(fill="x", pady=16)
        self._build_buttons(centre)

    def _build_map_picker(self, parent: tk.Frame) -> None:
        maps = _find_maps()

        if not maps:
            tk.Label(
                parent,
                text=(
                    f"No maps found in {_MAPS_DIR}\n"
                    "Each map folder must contain board.json and map.png."
                ),
                font=FONT_HINT, bg=BG, fg=ACCENT_RED, justify="left",
            ).pack(anchor="w", pady=(0, 8))
            return

        row = tk.Frame(parent, bg=BG)
        row.pack(anchor="w")

        for map_path in maps:
            # Pre-render both brightness variants so toggling is instant
            self._img_dim[map_path]    = _make_card_image(map_path, _IMG_DIM)
            self._img_bright[map_path] = _make_card_image(map_path, _IMG_SELECT)
            self._build_map_card(row, map_path)

        self._select_map(maps[0])

    def _build_map_card(self, parent: tk.Frame, map_path: Path) -> None:
        """Build one map card using a Canvas so the image can be a background."""
        canvas = tk.Canvas(
            parent,
            width=_CARD_W, height=_CARD_H,
            bg=BG_PANEL,
            highlightthickness=1,
            highlightbackground=_BORDER_NORMAL,
            cursor="hand2",
        )
        canvas.pack(side="left", padx=(0, 10))

        # Background image (drawn first so text sits on top)
        img = self._img_dim[map_path]
        if img:
            img_id = canvas.create_image(0, 0, anchor="nw", image=img)
        else:
            img_id = None
        self._img_ids[map_path] = img_id

        # Map name label centred on the canvas
        name_id = canvas.create_text(
            _CARD_W // 2, _CARD_H // 2,
            text=map_path.name,
            fill=_LABEL_NORMAL,
            font=FONT_BODY,
        )
        self._map_name_ids[map_path] = name_id
        self._map_canvases[map_path] = canvas

        for event in ("<Button-1>", ):
            canvas.bind(event, lambda e, p=map_path: self._select_map(p))
        canvas.bind("<Enter>", lambda e, p=map_path: self._on_hover(p, True))
        canvas.bind("<Leave>", lambda e, p=map_path: self._on_hover(p, False))

    # --- Player row ---

    def _build_player_row(
        self, parent: tk.Frame,
        color_name: str, hex_color: str, label: str,
    ) -> None:
        row = tk.Frame(parent, bg=BG_PANEL, pady=10, padx=16)
        row.pack(fill="x", pady=3, expand=True)
        focus_bg = "#363B45"

        lbl = tk.Label(
            row, text="\u25c6  " + label,
            font=FONT_LABEL, width=9, anchor="w",
            bg=BG_PANEL, fg=hex_color,
        )
        lbl.pack(side="left")

        tk.Frame(row, width=1, bg=GOLD_DIM).pack(
            side="left", fill="y", padx=(10, 14)
        )

        entry = tk.Entry(
            row, font=FONT_ENTRY,
            bg=BG_ENTRY, fg=FG_PRIMARY,
            insertbackground=ACCENT_GOLD, relief="flat",
            highlightthickness=1,
            highlightcolor=ACCENT_GOLD,
            highlightbackground=GOLD_DIM,
        )
        entry.pack(side="left", ipady=3, expand=True, fill="x")
        entry.bind(
            "<FocusIn>",
            lambda e, r=row, l=lbl: (r.config(bg=focus_bg), l.config(bg=focus_bg)),
        )
        entry.bind(
            "<FocusOut>",
            lambda e, r=row, l=lbl: (r.config(bg=BG_PANEL), l.config(bg=BG_PANEL)),
        )
        self.entries.append((color_name, entry))

    # --- Buttons ---

    def _build_buttons(self, parent: tk.Frame) -> None:
        btn_row = tk.Frame(parent, bg=BG)
        btn_row.pack()

        start = tk.Button(
            btn_row, text="START GAME", font=FONT_BTN,
            bg=ACCENT_RED, fg="#ffffff",
            activebackground=BTN_HOVER, activeforeground="#ffffff",
            relief="flat", padx=30, pady=10,
            cursor="hand2", bd=0, highlightthickness=0,
            command=self._start_game,
        )
        start.pack(side="left", padx=(0, 10))
        start.bind("<Enter>", lambda e: start.config(bg=BTN_HOVER))
        start.bind("<Leave>", lambda e: start.config(bg=ACCENT_RED))

        clear = tk.Button(
            btn_row, text="CLEAR", font=FONT_BTN,
            bg=BTN_OFF, fg=FG_MUTED,
            activebackground=GOLD_DIM, activeforeground=FG_PRIMARY,
            relief="flat", padx=18, pady=10,
            cursor="hand2", bd=0, highlightthickness=0,
            command=self._clear_inputs,
        )
        clear.pack(side="left")
        clear.bind("<Enter>", lambda e: clear.config(fg=FG_PRIMARY))
        clear.bind("<Leave>", lambda e: clear.config(fg=FG_MUTED))

    # --- Map selection state ---

    def _select_map(self, path: Path) -> None:
        self._selected_map = path
        for p, canvas in self._map_canvases.items():
            selected = p == path
            self._apply_card_state(p, selected=selected, hovered=False)

    def _on_hover(self, path: Path, entering: bool) -> None:
        if path == self._selected_map:
            return
        self._apply_card_state(path, selected=False, hovered=entering)

    def _apply_card_state(
        self, path: Path, selected: bool, hovered: bool
    ) -> None:
        canvas  = self._map_canvases[path]
        name_id = self._map_name_ids[path]
        img_id  = self._img_ids.get(path)

        # Border
        canvas.config(
            highlightbackground=_BORDER_SELECTED if selected else _BORDER_NORMAL
        )

        # Label colour
        canvas.itemconfig(
            name_id,
            fill=_LABEL_SELECTED if selected else (FG_PRIMARY if hovered else _LABEL_NORMAL),
        )

        # Image brightness — swap PhotoImage reference on the canvas item
        if img_id is not None:
            img = (
                self._img_bright[path]
                if (selected or hovered)
                else self._img_dim[path]
            )
            if img:
                canvas.itemconfig(img_id, image=img)

    # --- Event handlers ---

    def _clear_inputs(self) -> None:
        for _, entry in self.entries:
            entry.delete(0, "end")

    def _start_game(self) -> None:
        if self._selected_map is None:
            messagebox.showerror("Error", "Please select a map first.")
            return

        self.game.reset_players()

        filled = [
            (color, entry.get().strip())
            for color, entry in self.entries
            if entry.get().strip()
        ]

        if len(filled) < 2:
            messagebox.showerror("Error", "Please enter at least 2 player names.")
            return

        names = [name for _, name in filled]
        if len(names) != len(set(names)):
            messagebox.showerror("Error", "Player names must be unique.")
            return

        for color_name, name in filled:
            player = self.game.add_player(name)
            if player is not None:
                player.color = color_name

        try:
            self.game.start(self._selected_map)
        except (ValueError, FileNotFoundError) as e:
            messagebox.showerror("Error", str(e))
            return

        self.frame.destroy()
        self.root.current_screen = GameScreen(self.root, self.game)