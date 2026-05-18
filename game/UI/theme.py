"""theme.py — shared palette and font constants for all UI screens."""

# ── Backgrounds ──────────────────────────────────────────────────────────────
BG_MAIN    = "#160d08"   # espresso — window fill / main background
BG_DARK    = "#0f0804"   # deep dark — bottom bar, board frame
BG_PANEL   = "#221409"   # sidebar panel
BG_SURFACE = "#1a0f06"   # listbox / card surfaces
BG_ENTRY   = "#0f0804"   # entry field background

# ── Accent colours ───────────────────────────────────────────────────────────
ACCENT_RED  = "#9e2020"   # TTR signal red
ACCENT_GOLD = "#c49a3c"   # railway gold
GOLD_DIM    = "#5a3e10"   # dimmed gold for dividers / borders

# ── Foreground ───────────────────────────────────────────────────────────────
FG_PRIMARY = "#f0e6d0"   # warm cream
FG_MUTED   = "#7a5c3a"   # secondary / label text
FG_HINT    = "#a07850"   # inline hint / detail text

# ── Button states ────────────────────────────────────────────────────────────
BTN_OFF   = "#2a1a0a"    # inactive / secondary button background
BTN_HOVER = "#7a1818"    # primary button hover

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_HERO   = ("Georgia", 28, "bold")
FONT_CITY   = ("Georgia", 12)
FONT_LABEL  = ("Georgia", 10, "bold")
FONT_ENTRY  = ("Georgia", 11)
FONT_BTN    = ("Georgia", 11, "bold")
FONT_BODY   = ("Georgia", 10)
FONT_TITLE  = ("Georgia", 11, "bold")
FONT_PLAYER = ("Georgia", 12, "bold")
FONT_STATS  = ("Georgia", 9)
FONT_SMALL  = ("Georgia", 9)
FONT_BUTTON = ("Georgia", 10, "bold")
FONT_HINT   = ("Georgia", 8)

# ── Player token colours (plain-name → hex) ───────────────────────────────────
_PLAYER_COLORS: dict[str, str] = {
    "red":    "#c43030",
    "yellow": "#c49a3c",
    "green":  "#2e8c2e",
    "black":  "#aaaaaa",
    "blue":   "#2255d4",
}

# ── Setup-screen slot definitions (colour_name, hex, display_label) ──────────
PLAYER_SLOTS: list[tuple[str, str, str]] = [
    ("red",    "#c43030", "RED"),
    ("yellow", "#c49a3c", "YELLOW"),
    ("green",  "#2e8c2e", "GREEN"),
    ("black",  "#aaaaaa", "BLACK"),
    ("blue",   "#2255d4", "BLUE"),
]