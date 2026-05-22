"""theme.py — shared UI palette and font constants (One Dark base #282C34)."""

#  Backgrounds 
BG_MAIN = "#282C34"  # main window fill
BG_DARK = "#21252B"  # bottom bar, board frame
BG_PANEL = "#2C313A"  # sidebar / panel surfaces
BG_SURFACE = "#333842"  # listbox / card inset surfaces
BG_ENTRY = "#1E2227"  # entry field background

#  Accent colours 
ACCENT_RED = "#E06C75"
ACCENT_GOLD = "#E5C07B"
GOLD_DIM = "#4B5263"  # muted border / divider

#  Foreground 
FG_PRIMARY = "#ABB2BF"
FG_MUTED = "#7A8394"
FG_HINT = "#5C6370"

#  Button states 
BTN_OFF = "#3E4451"
BTN_HOVER = "#BE5046"

#  Fonts 
_SANS = "Segoe UI"

FONT_HERO = (_SANS, 24, "bold")
FONT_CITY = (_SANS, 11)
FONT_LABEL = (_SANS, 9, "bold")
FONT_ENTRY = (_SANS, 10)
FONT_BTN = (_SANS, 10, "bold")
FONT_BODY = (_SANS, 10)
FONT_TITLE = (_SANS, 10, "bold")
FONT_PLAYER = (_SANS, 12, "bold")
FONT_STATS = (_SANS, 9)
FONT_SMALL = (_SANS, 9)
FONT_BUTTON = (_SANS, 10, "bold")
FONT_HINT = (_SANS, 8)

#  Player colours used in the sidebar / badges 
# Lighter One Dark palette tones — intentionally different from the darker
# map piece colours in map_view._TRAIN_PIECE_HEX.
_PLAYER_COLORS: dict[str, str] = {
    "red": "#E06C75",
    "yellow": "#E5C07B",
    "green": "#98C379",
    "black": "#ABB2BF",
    "blue": "#61AFEF",
}

#  Setup-screen slot definitions (colour_name, hex, display_label) 
PLAYER_SLOTS: list[tuple[str, str, str]] = [
    ("red", "#E06C75", "RED"),
    ("yellow", "#E5C07B", "YELLOW"),
    ("green", "#98C379", "GREEN"),
    ("black", "#ABB2BF", "BLACK"),
    ("blue", "#61AFEF", "BLUE"),
]
