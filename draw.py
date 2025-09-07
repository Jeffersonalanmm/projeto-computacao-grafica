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

def draw_grid(screen, board):
    for y in range(len(board)):
        for x in range(len(board[y])):
            rect = pygame.Rect(x * TILE_SIZE, HEADER_HEIGHT + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (50, 50, 50), rect)  
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)  

def draw_board(screen, board, tiles, score, font, score_font, game_over=False):
    screen.fill((30, 30, 30))

    score_text = score_font.render(f"Pontos: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    draw_grid(screen, board)

    for tile in tiles:
        x = int(tile.x_draw * TILE_SIZE)
        y = int(HEADER_HEIGHT + tile.y_draw * TILE_SIZE)
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        color = COLORS.get(tile.value, (200, 200, 200))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        draw_text_auto_fit(screen, tile.value, rect, (255, 255, 255))

    if game_over:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        big_font = pygame.font.SysFont("Arial", 48, bold=True)
        text = big_font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
        screen.blit(text, text_rect)

        small_font = pygame.font.SysFont("Arial", 24, bold=True)
        text2 = small_font.render("Pressione ESC para reiniciar", True, (255, 255, 255))
        text2_rect = text2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 30))
        screen.blit(text2, text2_rect)

    pygame.display.flip()
