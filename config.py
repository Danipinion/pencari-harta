import os, sys


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works in dev and in PyInstaller exe."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# --- Theme
APPEARANCE_MODE = "dark"
DEFAULT_COLOR_THEME = "dark-blue"
FONT_PAPAN = ("Consolas", 42, "bold")
FONT_UI = ("Segoe UI", 14, "bold")
FONT_STATS = ("Consolas", 16)

# --- Warna papan
COLOR_WALL = "#2c3e50"
COLOR_PATH = "#7f8c8d"
COLOR_PLAYER = "#e74c3c"
COLOR_TREASURE = "#f1c40f"
COLOR_BOMB = "#9b59b6"
COLOR_HINT = "#3498db"
COLOR_WIN = "#2ecc71"

# --- Papan
PAPAN_LEBAR, PAPAN_TINGGI = 10, 10
TILE_DINDING, TILE_JALUR, TILE_BOM = 0, 1, 2
JARAK_MINIMAL_HARTA = 5
JARAK_MAKSIMAL_HARTA = 7
JUMLAH_BOM = 5

# --- Pemain
ARAH_ATAS, ARAH_KANAN, ARAH_BAWAH, ARAH_KIRI = "atas", "kanan", "bawah", "kiri"
ARAH_LIST = [ARAH_ATAS, ARAH_KANAN, ARAH_BAWAH, ARAH_KIRI]
PLAYER_IMAGE_FILES = {
    ARAH_ATAS: resource_path("assets/images/char-back.png"),
    ARAH_KANAN: resource_path("assets/images/char-left.png"),
    ARAH_BAWAH: resource_path("assets/images/char-front.png"),
    ARAH_KIRI: resource_path("assets/images/char-right.png"),
}
TREASURE_IMAGE_FILE = resource_path("assets/images/chest-close.png")
BOMB_IMAGE_FILE = resource_path("assets/images/bomb.png")
WIN_IMAGE_FILE = resource_path("assets/images/chest-open.png")

# --- Sfx
SOUND_FILES = {
    "move": resource_path("assets/sfx/move.mp3"),
    "bump": resource_path("assets/sfx/bump.mp3"),
    "win": resource_path("assets/sfx/win.mp3"),
    "lose": resource_path("assets/sfx/lose.mp3"),
    "click": resource_path("assets/sfx/click.mp3"),
}
