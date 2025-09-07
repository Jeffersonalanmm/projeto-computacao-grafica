import random
from settings import BOARD_SIZE, BASIC_POOL, MERGE_RULES

class Tile:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.x_draw = float(x)
        self.y_draw = float(y)
        self.speed = 10 

    def update(self, dt):
        self.x_draw += (self.x - self.x_draw) * min(1, dt * self.speed)
        self.y_draw += (self.y - self.y_draw) * min(1, dt * self.speed)

def create_board():
    return [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def spawn_tile(board, tiles):
    empty = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if not board[i][j]]
    if empty:
        i, j = random.choice(empty)
        value = random.choice(BASIC_POOL)
        board[i][j] = value
        tiles.append(Tile(j, i, value))

def merge_line(line):
    new_line = [c for c in line if c is not None]
    i = 0
    result = []
    score_gained = 0
    while i < len(new_line):
        if i + 1 < len(new_line) and (new_line[i], new_line[i+1]) in MERGE_RULES:
            merged, points = MERGE_RULES[(new_line[i], new_line[i+1])]
            result.append(merged)
            score_gained += points
            i += 2
        else:
            result.append(new_line[i])
            i += 1
    while len(result) < BOARD_SIZE:
        result.append(None)
    return result, score_gained

def move(board, tiles, direction):
    moved = False
    total_score = 0

    for i in range(BOARD_SIZE):
        if direction == "left":
            line = board[i]
            merged, score = merge_line(line)
            if merged != line:
                moved = True
            board[i] = merged
            total_score += score
        elif direction == "right":
            line = board[i][::-1]
            merged, score = merge_line(line)
            merged = merged[::-1]
            if merged != board[i]:
                moved = True
            board[i] = merged
            total_score += score
        elif direction == "up":
            line = [board[r][i] for r in range(BOARD_SIZE)]
            merged, score = merge_line(line)
            if merged != line:
                moved = True
            for r in range(BOARD_SIZE):
                board[r][i] = merged[r]
            total_score += score
        elif direction == "down":
            line = [board[r][i] for r in range(BOARD_SIZE)][::-1]
            merged, score = merge_line(line)
            merged = merged[::-1]
            if merged != [board[r][i] for r in range(BOARD_SIZE)]:
                moved = True
            for r in range(BOARD_SIZE):
                board[r][i] = merged[r]
            total_score += score

    if moved:
        tiles.clear()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c]:
                    tiles.append(Tile(c, r, board[r][c]))
        spawn_tile(board, tiles)

    return moved, total_score

def is_game_over(board):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] is None:
                return False
            for di, dj in [(0, 1), (1, 0)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                    if (board[i][j], board[ni][nj]) in MERGE_RULES or (board[ni][nj], board[i][j]) in MERGE_RULES:
                        return False
    return True
