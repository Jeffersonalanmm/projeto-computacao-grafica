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

        self.scale = 0.0
        self.animation_speed = 6.0
        self.merged_this_turn = False
        self.to_remove= False
        
    def update(self, dt):
        self.x_draw += (self.x - self.x_draw) * min(1, dt * self.speed)
        self.y_draw += (self.y - self.y_draw) * min(1, dt * self.speed)

        target_scale = 1.0
        if self.scale < target_scale:
            self.scale += (target_scale - self.scale) * self.animation_speed * dt

def create_board():
    return [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def spawn_tile(board, tiles):
    empty = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if not board[i][j]]
    if empty:
        i, j = random.choice(empty)
        value = random.choice(BASIC_POOL)
        board[i][j] = value
        tiles.append(Tile(j, i, value))

# def merge_line(line):
#     new_line = [c for c in line if c is not None]
#     i = 0
#     result = []
#     score_gained = 0
#     while i < len(new_line):
#         if i + 1 < len(new_line) and (new_line[i], new_line[i+1]) in MERGE_RULES:
#             merged, points = MERGE_RULES[(new_line[i], new_line[i+1])]
#             result.append(merged)
#             score_gained += points
#             i += 2
#         else:
#             result.append(new_line[i])
#             i += 1
#     while len(result) < BOARD_SIZE:
#         result.append(None)
#     return result, score_gained

def move(board, tiles, direction):
    moved = False
    total_score = 0

    for tile in tiles:
        tile.merged_this_turn = False

    dx, dy = 0, 0
    if direction == "left":
        dx = -1
        x_range = range(1, BOARD_SIZE)
        y_range = range(BOARD_SIZE)
    elif direction == "right":
        dx = 1
        x_range = range(BOARD_SIZE - 2, -1, -1)
        y_range = range(BOARD_SIZE)
    elif direction == "up":
        dy = -1
        x_range = range(BOARD_SIZE)
        y_range = range(1, BOARD_SIZE)
    elif direction == "down":
        dy = 1
        x_range = range(BOARD_SIZE)
        y_range = range(BOARD_SIZE - 2, -1, -1)

    for y_start in y_range:
        for x_start in x_range:
            if board[y_start][x_start] is not None:
                x, y = x_start, y_start
                
                current_tile = next((t for t in tiles if t.x == x and t.y == y and not t.to_remove), None)
                if not current_tile: continue

                last_empty_x, last_empty_y = x, y
                while 0 <= last_empty_x + dx < BOARD_SIZE and 0 <= last_empty_y + dy < BOARD_SIZE and \
                      board[last_empty_y + dy][last_empty_x + dx] is None:
                    last_empty_y += dy
                    last_empty_x += dx
                
                merge_target_x, merge_target_y = last_empty_x + dx, last_empty_y + dy
                
                can_merge = False
                if 0 <= merge_target_x < BOARD_SIZE and 0 <= merge_target_y < BOARD_SIZE:
                    target_value = board[merge_target_y][merge_target_x]
                    if target_value is not None:
                        target_tile = next((t for t in tiles if t.x == merge_target_x and t.y == merge_target_y), None)
                        if target_tile and not target_tile.merged_this_turn and (current_tile.value, target_tile.value) in MERGE_RULES:
                            can_merge = True

                if can_merge:
                    moved = True
                    board[y][x] = None
                    merged_value, points = MERGE_RULES[(current_tile.value, target_tile.value)]
                    board[target_tile.y][target_tile.x] = merged_value
                    total_score += points

                    current_tile.to_remove = True
                    current_tile.x, current_tile.y = target_tile.x, target_tile.y
                    target_tile.value = merged_value
                    target_tile.merged_this_turn = True

                elif last_empty_x != x or last_empty_y != y:
                    moved = True
                    board[last_empty_y][last_empty_x] = board[y][x]
                    board[y][x] = None
                    current_tile.x, current_tile.y = last_empty_x, last_empty_y

    if moved:
        tiles[:] = [t for t in tiles if not t.to_remove]
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

def are_animations_running(tiles):
    """Verifica se alguma peça ainda está em animação (deslizando ou nascendo)."""
    for tile in tiles:
        # Verifica se a peça ainda está deslizando para sua posição
        if abs(tile.x - tile.x_draw) > 0.01 or abs(tile.y - tile.y_draw) > 0.01:
            return True
        # Verifica se a peça ainda está em sua animação de "nascer"
        if tile.scale < 0.95:
            return True
    return False
