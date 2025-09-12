import pygame
from settings import COLORS, MAX_FONT_SIZE, MIN_FONT_SIZE, COLOR_TOP, COLOR_BOTTOM

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
    width, height = screen.get_size()
    board_size = len(board)
    header_height = int(height * 0.12)
    max_board_width = int(width * 0.9)
    max_board_height = int((height - header_height) * 0.85)
    tile_size = min(max_board_width // board_size, max_board_height // board_size)
    board_pixel_width = tile_size * board_size
    board_pixel_height = tile_size * board_size
    offset_x = (width - board_pixel_width) // 2
    offset_y = header_height + ((height - header_height) - board_pixel_height) // 2

    for y in range(board_size):
        for x in range(board_size):
            rect = pygame.Rect(
                offset_x + x * tile_size,
                offset_y + y * tile_size,
                tile_size,
                tile_size
            )
            pygame.draw.rect(screen, (50, 50, 50), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)

def draw_board(screen, board, tiles, score, font, score_font, game_over, music_on, icon_on, icon_off, icon_restart):
    #Responsividade
    width, height = screen.get_size()
    #BG gradiente
    gradient = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / max(1, height)
        r = int(COLOR_TOP[0] * (1 - ratio) + COLOR_BOTTOM[0] * ratio)
        g = int(COLOR_TOP[1] * (1 - ratio) + COLOR_BOTTOM[1] * ratio)
        b = int(COLOR_TOP[2] * (1 - ratio) + COLOR_BOTTOM[2] * ratio)
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    screen.blit(gradient, (0, 0))

    width, height = screen.get_size()
    board_size = len(board)
    header_height = int(height * 0.12)
    max_board_width = int(width * 0.9)
    max_board_height = int((height - header_height) * 0.85)
    tile_size = min(max_board_width // board_size, max_board_height // board_size)
    board_pixel_width = tile_size * board_size
    board_pixel_height = tile_size * board_size
    offset_x = (width - board_pixel_width) // 2
    offset_y = header_height + ((height - header_height) - board_pixel_height) // 2

    if score_font is None:
        score_font_size = max(14, min(48, tile_size // 3))
        score_font = pygame.font.SysFont("Arial", score_font_size, bold=True)
    if font is None:
        font_size = max(12, min(36, tile_size // 4))
        font = pygame.font.SysFont("Arial", font_size, bold=True)

    # Titulo acima do score
    top_margin = max(10, int(height * 0.03))  # distância da parte superior
    title_color = (255, 180, 60)  # laranja
    title_surface = score_font.render("BCC2048", True, title_color)
    title_x = offset_x
    title_y = top_margin
    screen.blit(title_surface, (title_x, title_y))

    score_text = score_font.render(f"Pontos: {score}", True, (255, 255, 255))
    score_x = offset_x
    score_y = title_y + title_surface.get_height() + max(6, int(height * 0.01))
    screen.blit(score_text, (score_x, score_y))

    music_button_rect = None
    restart_button_rect = None
    if icon_on and icon_off and icon_restart: # Só desenha se os ícones foram carregados
        width, height = screen.get_size()
        icon_to_draw = icon_on if music_on else icon_off
        padding = 10
        
        # Posiciona o ícone no canto superior direito
        music_button_rect = icon_to_draw.get_rect(
            topright=(width - padding, padding)
        )

        restart_button_rect = icon_restart.get_rect(
            topright=(music_button_rect.left - padding, padding)
        )
        
        # Efeito de hover
        mouse_pos = pygame.mouse.get_pos()
        if music_button_rect.collidepoint(mouse_pos):
            icon_to_draw.set_alpha(200) 
        else:
            icon_to_draw.set_alpha(255)

        if restart_button_rect.collidepoint(mouse_pos): 
            icon_restart.set_alpha(200)
        else: 
            icon_restart.set_alpha(255)


        screen.blit(icon_to_draw, music_button_rect)
        screen.blit(icon_restart, restart_button_rect) 
    


    draw_grid(screen, board)

    # Tiles
    for tile in tiles:
        center_x = offset_x + tile.x_draw * tile_size + tile_size / 2
        center_y = offset_y + tile.y_draw * tile_size + tile_size / 2
        current_size = tile_size * tile.scale
        rect = pygame.Rect(0, 0, current_size, current_size)
        rect.center = (center_x, center_y)

        color = COLORS.get(tile.value, (200, 200, 200))
        pygame.draw.rect(screen, color, rect, border_radius=5)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=5)

        text_surface = draw_text_auto_fit(tile.value, (255, 255, 255), tile_size)
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
    return music_button_rect, restart_button_rect
