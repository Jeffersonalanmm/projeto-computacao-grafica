import pygame
from settings import TILE_SIZE, HEADER_HEIGHT, COLORS, MAX_FONT_SIZE, MIN_FONT_SIZE

def draw_text_auto_fit(screen, text, rect, color, max_font=MAX_FONT_SIZE, min_font=MIN_FONT_SIZE):
    font_size = max_font
    font = pygame.font.SysFont("Arial", font_size, bold=True)
    text_surface = font.render(text, True, color)
    while (text_surface.get_width() > rect.width - 10 or text_surface.get_height() > rect.height - 10) and font_size > min_font:
        font_size -= 1
        font = pygame.font.SysFont("Arial", font_size, bold=True)
        text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_board(screen, board, score, font, score_font):
    screen.fill((30, 30, 30))

    
    score_text = score_font.render(f"Pontos: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    for i in range(len(board)):
        for j in range(len(board[i])):
            x = j * TILE_SIZE
            y = HEADER_HEIGHT + i * TILE_SIZE
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if board[i][j]:
                color = COLORS.get(board[i][j], (200, 200, 200))
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)
                draw_text_auto_fit(screen, board[i][j], rect, (255, 255, 255))
            else:
                pygame.draw.rect(screen, (80, 80, 80), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)

    pygame.display.flip()
