WINDOW_SIZE = 600
BOARD_SIZE = 4
TILE_SIZE = WINDOW_SIZE // BOARD_SIZE
FONT_SIZE = 20
HEADER_HEIGHT = 60

# BG
COLOR_TOP = (40, 0, 60)
COLOR_BOTTOM = (0, 0, 80)

MERGE_RULES = {
    ("IP", "IP"): ("POO", 2),
    ("POO", "POO"): ("AED I", 4),
    ("AED I", "AED I"): ("AED II", 8),
    ("AED II", "AED II"): ("CG", 16),
    ("CG", "CG"): ("PLP", 32),
    ("PLP", "PLP"): ("PAA", 64),
    ("PAA", "PAA"): ("Compiladores", 128),
    ("Compiladores", "Compiladores"): ("IA", 256),
    ("IA", "IA"): ("RP", 512),
    ("RP", "RP"): ("Projetão", 1024),
    ("Projetão", "Projetão"): ("TCC", 2048),
}

COLORS = {
    "IP": (70, 130, 180),
    "POO": (34, 139, 34),
    "AED I": (255, 140, 0),
    "AED II": (148, 0, 211),
    "PLP": (255, 215, 0),
    "PAA": (178, 34, 34),
    "CG": (0, 206, 209),
    "IA": (219, 112, 147),
    "RP": (255, 105, 180),
    "Projetão": (105, 105, 105),
    "TCC": (123, 104, 238),
}

BASIC_POOL = [
    "IP", "POO"
]

MAX_FONT_SIZE = 24
MIN_FONT_SIZE = 10
