# --- Theme
APPEARANCE_MODE = "dark"
DEFAULT_COLOR_THEME = "dark-blue"
FONT_PAPAN = ("Consolas", 30, "bold")
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
ARAH_ATAS, ARAH_KANAN, ARAH_BAWAH, ARAH_KIRI = 'atas', 'kanan', 'bawah', 'kiri'
ARAH_LIST = [ARAH_ATAS, ARAH_KANAN, ARAH_BAWAH, ARAH_KIRI]
PLAYER_ICONS = {
    ARAH_ATAS: '👆🏻',
    ARAH_KANAN: '👉🏻',
    ARAH_BAWAH: '👇🏻',
    ARAH_KIRI: '👈🏻',
}
TREASURE_CHAR = "★"
BOMB_CHAR = "⚫"

# --- Sfx
SOUND_FILES = {
    'move': 'sfx/move.mp3',
    'bump': 'sfx/bump.mp3',
    'win': 'sfx/win.mp3',
    'lose': 'sfx/lose.mp3',
    'click': 'sfx/click.mp3'
}
