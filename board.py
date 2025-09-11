import random
from settings import BOARD_SIZE, BASIC_POOL, MERGE_RULES

class Tile:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.x_draw = float(x)
        self.y_draw = float(y)
        self.speed = 20

        self.scale = 0.0
        self.animation_speed = 12

        # Atributos que controlam a junção das peças
        self.merged_this_turn = False
        self.to_remove = False
        self.pending_value = None
        self.merge_target = None

    def update(self, dt):
        if self.merge_target:
            self.x_draw += (self.merge_target.x_draw - self.x_draw) * min(1, dt * self.speed)
            self.y_draw += (self.merge_target.y_draw - self.y_draw) * min(1, dt * self.speed)

            if abs(self.x_draw - self.merge_target.x_draw) < 0.1 and abs(self.y_draw - self.merge_target.y_draw) < 0.1:
                if self.merge_target.pending_value:
                    self.merge_target.value = self.merge_target.pending_value
                    self.merge_target.pending_value = None
                
                self.merge_target.scale = 0.6 
                self.to_remove = True 
                self.merge_target = None
        else:
            self.x_draw += (self.x - self.x_draw) * min(1, dt * self.speed)
            self.y_draw += (self.y - self.y_draw) * min(1, dt * self.speed)
        
        target_scale = 1.0
        if abs(self.scale - target_scale) > 0.01:
            self.scale += (target_scale - self.scale) * self.animation_speed * dt
        elif self.scale != 1.0:
            self.scale = 1.0

def create_board():
    return [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def spawn_tile(board, tiles):
    empty = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if not board[i][j]]
    if empty:
        i, j = random.choice(empty)
        value = random.choice(BASIC_POOL)
        board[i][j] = value
        tiles.append(Tile(j, i, value))

def move(board, tiles, direction):
    moved = False
    total_score = 0

    for tile in tiles:
        tile.merged_this_turn = False

    if direction == "left":
        sort_key, reverse, dx, dy = (lambda t: t.x), False, -1, 0
    elif direction == "right":
        sort_key, reverse, dx, dy = (lambda t: t.x), True, 1, 0
    elif direction == "up":
        sort_key, reverse, dx, dy = (lambda t: t.y), False, 0, -1
    elif direction == "down":
        sort_key, reverse, dx, dy = (lambda t: t.y), True, 0, 1

    sorted_tiles = sorted(tiles, key=sort_key, reverse=reverse)

    for current_tile in sorted_tiles:
        x_start, y_start = current_tile.x, current_tile.y
        x, y = x_start, y_start

        # Encontra a posição final do tile, pulando espaços vazios
        while 0 <= x + dx < BOARD_SIZE and 0 <= y + dy < BOARD_SIZE and board[y + dy][x + dx] is None:
            x += dx
            y += dy

        # Agora, a lógica de fusão
        # Verifica se o próximo bloco é um alvo de fusão válido
        if 0 <= x + dx < BOARD_SIZE and 0 <= y + dy < BOARD_SIZE:
            # Obtém a peça alvo que está imediatamente ao lado da posição de parada
            target_value = board[y + dy][x + dx]
            
            # Checa se a fusão é possível e se a peça alvo ainda não foi fundida neste turno
            if (current_tile.value, target_value) in MERGE_RULES:
                target_tile = next((t for t in tiles if t.x == x + dx and t.y == y + dy), None)
                
                if target_tile and not target_tile.merged_this_turn:
                    merged_value, points = MERGE_RULES[(current_tile.value, target_value)]
                    total_score += points
                    
                    current_tile.merge_target = target_tile
                    target_tile.pending_value = merged_value
                    target_tile.merged_this_turn = True
                    board[y_start][x_start] = None
                    moved = True
                    continue  # Continua para o próximo tile para evitar o movimento simples abaixo
        
        # Se não houve fusão, move a peça para a posição final
        if x != x_start or y != y_start:
            current_tile.x, current_tile.y = x, y
            board[y][x] = current_tile.value
            board[y_start][x_start] = None
            moved = True

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

def cleanup_merged_tiles(tiles):
    """Remove as peças que terminaram sua animação de junção."""
    tiles[:] = [t for t in tiles if not t.to_remove]


def are_animations_running(tiles):
    """Verifica se alguma animação ainda está acontecendo."""
    for tile in tiles:
        if tile.merge_target: return True
        if abs(tile.x - tile.x_draw) > 0.01 or abs(tile.y - tile.y_draw) > 0.01: return True
        if abs(tile.scale - 1.0) > 0.01: return True
    return False