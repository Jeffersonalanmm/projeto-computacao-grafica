import pygame
import sys
import random

# Configurações
WINDOW_SIZE = 600
BOARD_SIZE = 4
TILE_SIZE = WINDOW_SIZE // BOARD_SIZE
FONT_SIZE = 18

# Regras de fusão
MERGE_RULES = {
    ("Lógica Matemática", "Lógica Matemática"): "Matemática Discreta",
    ("Geometria Analítica", "Geometria Analítica"): "Álgebra Linear",
    ("Geometria Analítica", "Cálculo 1"): "Cálculo 2",
    ("Cálculo 1", "Geometria Analítica"): "Cálculo 2",
    ("Introdução à Programação", "Introdução à Programação"): "AED 1",
    ("AED 1", "Álgebra Linear"): "Computação Gráfica",
    ("Álgebra Linear", "AED 1"): "Computação Gráfica",
}

# Cores por disciplina
COLORS = {
    "Lógica Matemática": (70, 130, 180),
    "Matemática Discreta": (34, 139, 34),
    "Geometria Analítica": (255, 140, 0),
    "Álgebra Linear": (148, 0, 211),
    "Cálculo 1": (255, 215, 0),
    "Cálculo 2": (178, 34, 34),
    "Introdução à Programação": (0, 206, 209),
    "AED 1": (219, 112, 147),
    "Computação Gráfica": (105, 105, 105),
}

BASIC_POOL = ["Lógica Matemática", "Geometria Analítica", "Cálculo 1", "Introdução à Programação"]

# Inicializa Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("2048 CC - PyGame")
font = pygame.font.SysFont("Arial", FONT_SIZE, bold=True)

# Tabuleiro
board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def spawn_tile():
    empty = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if not board[i][j]]
    if empty:
        i, j = random.choice(empty)
        board[i][j] = random.choice(BASIC_POOL)

# Movimento e fusão
def move(direction):
    moved = False

    def merge_line(line):
        new_line = [c for c in line if c is not None]
        i = 0
        result = []
        while i < len(new_line):
            if i + 1 < len(new_line) and (new_line[i], new_line[i+1]) in MERGE_RULES:
                result.append(MERGE_RULES[(new_line[i], new_line[i+1])])
                i += 2
            else:
                result.append(new_line[i])
                i += 1
        while len(result) < BOARD_SIZE:
            result.append(None)
        return result

    for i in range(BOARD_SIZE):
        if direction == "left":
            line = board[i]
            merged = merge_line(line)
            if merged != line:
                moved = True
            board[i] = merged
        elif direction == "right":
            line = board[i][::-1]
            merged = merge_line(line)
            merged = merged[::-1]
            if merged != board[i]:
                moved = True
            board[i] = merged
        elif direction == "up":
            line = [board[r][i] for r in range(BOARD_SIZE)]
            merged = merge_line(line)
            if merged != line:
                moved = True
            for r in range(BOARD_SIZE):
                board[r][i] = merged[r]
        elif direction == "down":
            line = [board[r][i] for r in range(BOARD_SIZE)][::-1]
            merged = merge_line(line)
            merged = merged[::-1]
            if merged != [board[r][i] for r in range(BOARD_SIZE)]:
                moved = True
            for r in range(BOARD_SIZE):
                board[r][i] = merged[r]

    if moved:
        spawn_tile()

# Desenho do tabuleiro
def draw_board():
    screen.fill((30, 30, 30))
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            x, y = j * TILE_SIZE, i * TILE_SIZE
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if board[i][j]:
                color = COLORS.get(board[i][j], (200, 200, 200))
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)
                # Texto centralizado
                text = font.render(board[i][j], True, (255, 255, 255))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            else:
                pygame.draw.rect(screen, (80, 80, 80), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)
    pygame.display.flip()

# Inicializa com 2 blocos
spawn_tile()
spawn_tile()

# Loop principal
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move("up")
            elif event.key == pygame.K_DOWN:
                move("down")
            elif event.key == pygame.K_LEFT:
                move("left")
            elif event.key == pygame.K_RIGHT:
                move("right")

    draw_board()
    clock.tick(60)
