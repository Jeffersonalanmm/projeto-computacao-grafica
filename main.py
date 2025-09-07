import pygame
import sys
from board import create_board, spawn_tile, move, is_game_over
from draw import draw_board
from settings import WINDOW_SIZE, HEADER_HEIGHT

def restart_game():
    board = create_board()
    spawn_tile(board)
    spawn_tile(board)
    return board, 0

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + HEADER_HEIGHT))
    pygame.display.set_caption("2048 CC - PyGame")
    font = pygame.font.SysFont("Arial", 20, bold=True)
    score_font = pygame.font.SysFont("Arial", 24, bold=True)

    board, score = restart_game()

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    moved, points = move(board, "up")
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    moved, points = move(board, "down")
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    moved, points = move(board, "left")
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    moved, points = move(board, "right")
                elif event.key == pygame.K_ESCAPE:
                    board, score = restart_game()
                    continue
                else:
                    moved = False
                    points = 0

                if moved:
                    score += points

        draw_board(screen, board, score, font, score_font)

        if is_game_over(board):
            print("Game Over!")
            pygame.time.wait(2000)
            board, score = restart_game()

        clock.tick(60)

if __name__ == "__main__":
    run_game()
