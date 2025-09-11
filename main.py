import pygame
import sys
from board import create_board, spawn_tile, move, is_game_over, are_animations_running, cleanup_merged_tiles
from draw import draw_board
from settings import WINDOW_SIZE, HEADER_HEIGHT

def restart_game():
    board = create_board()
    tiles = []
    spawn_tile(board, tiles)
    spawn_tile(board, tiles)
    return board, tiles, 0

def run_game():
    pygame.init()
    pygame.mixer.init()

    # carregar música
    try:
        pygame.mixer.music.load("2048-song.mp3")
    except:
            print("⚠ Música não encontrada!")
    else:
        pygame.mixer.music.play(-1)

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + HEADER_HEIGHT))
    pygame.display.set_caption("2048 BCC - PyGame")
    font = pygame.font.SysFont("Arial", 20, bold=True)
    score_font = pygame.font.SysFont("Arial", 24, bold=True)

    board, tiles, score = restart_game()

    clock = pygame.time.Clock()
    game_over = False
    animations_done = True

    while True:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if animations_done:
                    if game_over:
                        if event.key == pygame.K_ESCAPE:
                            board, tiles, score = restart_game()
                            game_over = False
                    else:
                        direction = None
                        if event.key in [pygame.K_UP, pygame.K_w]: direction = "up"
                        elif event.key in [pygame.K_DOWN, pygame.K_s]: direction = "down"
                        elif event.key in [pygame.K_LEFT, pygame.K_a]: direction = "left"
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]: direction = "right"
                        elif event.key == pygame.K_ESCAPE: board, tiles, score = restart_game()
                        
                        if direction:
                            moved, points = move(board, tiles, direction)
                            if moved:
                                score += points
                                animations_done = False

        for tile in tiles:
            tile.update(dt)
        
        cleanup_merged_tiles(tiles)

        if not animations_done and not are_animations_running(tiles):
            spawn_tile(board, tiles)
            animations_done = True 

        if not game_over and is_game_over(board) and animations_done:
            game_over = True

        draw_board(screen, board, tiles, score, font, score_font, game_over=game_over)

if __name__ == "__main__":
    run_game()
