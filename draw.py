import pygame
from settings import TILE_SIZE, HEADER_HEIGHT, COLORS, MAX_FONT_SIZE, MIN_FONT_SIZE

font_cache = {}
surface_cache = {}

def draw_text_auto_fit(text, color, target_width, max_font=MAX_FONT_SIZE, min_font=MIN_FONT_SIZE):
    font_size = max_font
    
    while font_size >= min_font:
        if font_size not in font_cache:
            font_cache[font_size] = pygame.font.SysFont("Arial", font_size, bold=True)
        font = font_cache[font_size]

        text_width, _ = font.size(text)
        if text_width < target_width - 10:
            break
        font_size -= 1

    if font_size < min_font:
        font_size = min_font

    cache_key = (text, font_size, color)
    
    if cache_key not in surface_cache:
        font = font_cache[font_size]
        surface_cache[cache_key] = font.render(text, True, color)
    
    return surface_cache[cache_key]

def draw_grid(screen, board):
    for y in range(len(board)):
        for x in range(len(board[y])):
            rect = pygame.Rect(x * TILE_SIZE, HEADER_HEIGHT + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (50, 50, 50), rect)  
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)  

def draw_board(screen, board, tiles, score, font, score_font, game_over, music_on, icon_on, icon_off):
    screen.fill((30, 30, 30))

    score_text = score_font.render(f"Pontos: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    music_button_rect = None
    if icon_on and icon_off: # Só desenha se os ícones foram carregados
        width, height = screen.get_size()
        icon_to_draw = icon_on if music_on else icon_off
        padding = 10
        
        # Posiciona o ícone no canto superior direito
        music_button_rect = icon_to_draw.get_rect(
            topright=(width - padding, padding)
        )
        
        # Efeito de hover
        mouse_pos = pygame.mouse.get_pos()
        if music_button_rect.collidepoint(mouse_pos):
            icon_to_draw.set_alpha(200) 
        else:
            icon_to_draw.set_alpha(255)

        screen.blit(icon_to_draw, music_button_rect)
    

    draw_grid(screen, board)

    for tile in tiles:
        center_x = tile.x_draw * TILE_SIZE + TILE_SIZE / 2
        center_y = HEADER_HEIGHT + tile.y_draw * TILE_SIZE + TILE_SIZE / 2
        
        current_size = TILE_SIZE * tile.scale
        rect = pygame.Rect(0, 0, current_size, current_size)
        rect.center = (center_x, center_y)

        color = COLORS.get(tile.value, (200, 200, 200))
        pygame.draw.rect(screen, color, rect, border_radius=5)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=5)
        
        text_surface = draw_text_auto_fit(tile.value, (255, 255, 255), TILE_SIZE)

        alpha = max(0, min(255, 255 * tile.scale))
        text_surface.set_alpha(alpha)
        
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

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
    return music_button_rect
