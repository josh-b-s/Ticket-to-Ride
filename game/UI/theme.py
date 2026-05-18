"""theme.py — shared UI palette and font constants.

Based on the One Dark palette (#282C34 base) — dark but easy on the eyes.
"""

# ── Backgrounds ──────────────────────────────────────────────────────────────
BG_MAIN    = "#282C34"   # One Dark base — main window fill
BG_DARK    = "#21252B"   # slightly deeper — bottom bar, board frame
BG_PANEL   = "#2C313A"   # sidebar / panel surfaces
BG_SURFACE = "#333842"   # listbox / card inset surfaces
BG_ENTRY   = "#1E2227"   # entry field background

# ── Accent colours ───────────────────────────────────────────────────────────
ACCENT_RED  = "#E06C75"   # One Dark red — primary action
ACCENT_GOLD = "#E5C07B"   # One Dark yellow — headers / highlights
GOLD_DIM    = "#4B5263"   # muted border / divider color

# ── Foreground ───────────────────────────────────────────────────────────────
FG_PRIMARY = "#ABB2BF"   # One Dark foreground — main text
FG_MUTED   = "#7A8394"   # secondary / label text
FG_HINT    = "#5C6370"   # hint / detail text

# ── Button states ────────────────────────────────────────────────────────────
BTN_OFF   = "#3E4451"    # secondary / inactive button background
BTN_HOVER = "#BE5046"    # primary button hover (darker red)

# ── Fonts (Segoe UI — clean sans-serif) ──────────────────────────────────────
_SANS = "Segoe UI"

FONT_HERO   = (_SANS, 24, "bold")
FONT_CITY   = (_SANS, 11)
FONT_LABEL  = (_SANS, 9,  "bold")
FONT_ENTRY  = (_SANS, 10)
FONT_BTN    = (_SANS, 10, "bold")
FONT_BODY   = (_SANS, 10)
FONT_TITLE  = (_SANS, 10, "bold")
FONT_PLAYER = (_SANS, 12, "bold")
FONT_STATS  = (_SANS, 9)
FONT_SMALL  = (_SANS, 9)
FONT_BUTTON = (_SANS, 10, "bold")
FONT_HINT   = (_SANS, 8)

# ── Player token colours (plain-name → hex) ───────────────────────────────────
_PLAYER_COLORS: dict[str, str] = {
    "red":    "#E06C75",
    "yellow": "#E5C07B",
    "green":  "#98C379",
    "black":  "#ABB2BF",
    "blue":   "#61AFEF",
}

# ── Setup-screen slot definitions (colour_name, hex, display_label) ──────────
PLAYER_SLOTS: list[tuple[str, str, str]] = [
    ("red",    "#E06C75", "RED"),
    ("yellow", "#E5C07B", "YELLOW"),
    ("green",  "#98C379", "GREEN"),
    ("black",  "#ABB2BF", "BLACK"),
    ("blue",   "#61AFEF", "BLUE"),
]