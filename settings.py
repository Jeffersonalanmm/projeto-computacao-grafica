WINDOW_SIZE = 600
BOARD_SIZE = 4
TILE_SIZE = WINDOW_SIZE // BOARD_SIZE
FONT_SIZE = 20
HEADER_HEIGHT = 60

MERGE_RULES = {
    ("Lógica Matemática", "Lógica Matemática"): ("Matemática Discreta", 10),
    ("Geometria Analítica", "Geometria Analítica"): ("Álgebra Linear", 10),
    ("Geometria Analítica", "Cálculo I"): ("Cálculo II", 20),
    ("Cálculo I", "Geometria Analítica"): ("Cálculo II", 20),
    ("Introdução à Programação I", "Introdução à Programação I"): ("Algoritmos e Estruturas de Dados I", 10),
    ("Algoritmos e Estruturas de Dados I", "Programação Orientada a Objetos"): ("Engenharia de Software I", 50),
    ("Álgebra Linear", "Algoritmos e Estruturas de Dados I"): ("Computação Gráfica", 50),
    
}

COLORS = {
    "Lógica Matemática": (70, 130, 180),
    "Matemática Discreta": (34, 139, 34),
    "Geometria Analítica": (255, 140, 0),
    "Álgebra Linear": (148, 0, 211),
    "Cálculo I": (255, 215, 0),
    "Cálculo II": (178, 34, 34),
    "Introdução à Programação I": (0, 206, 209),
    "Algoritmos e Estruturas de Dados I": (219, 112, 147),
    "Programação Orientada a Objetos": (255, 105, 180),
    "Engenharia de Software I": (105, 105, 105),
    "Computação Gráfica": (123, 104, 238),
}

BASIC_POOL = [
    "Lógica Matemática",
    "Geometria Analítica",
    "Cálculo I",
    "Introdução à Programação I",
]

MAX_FONT_SIZE = 24
MIN_FONT_SIZE = 10
