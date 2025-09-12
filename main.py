import pygame
import math
import sys
import os
from board import create_board, spawn_tile, move, is_game_over, are_animations_running, cleanup_merged_tiles
from draw import init_gl, draw_board_gl, update_viewport_on_resize
from settings import WINDOW_SIZE, HEADER_HEIGHT

SPAWN_DURATION = 1.5
MENU_FPS = 60

COLOR_TOP = (40, 0, 60)
COLOR_BOTTOM = (0, 0, 80)
TITLE_COLOR = (255, 215, 0)
SUBTITLE_COLOR = (200, 200, 255)
BUTTON_TEXT_NORMAL = (180, 180, 180)
BUTTON_TEXT_HOVER = (255, 255, 255)
BUTTON_BG_NORMAL = (120, 80, 0)
BUTTON_BG_HOVER = (150, 100, 0)
BUTTON_BORDER_NORMAL = (180, 120, 30)
BUTTON_BORDER_HOVER = (200, 150, 50)

HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

def create_gradient_surface(width, height):
    gradient = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(COLOR_TOP[0] * (1 - ratio) + COLOR_BOTTOM[0] * ratio)
        g = int(COLOR_TOP[1] * (1 - ratio) + COLOR_BOTTOM[1] * ratio)
        b = int(COLOR_TOP[2] * (1 - ratio) + COLOR_BOTTOM[2] * ratio)
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    return gradient

def calculate_responsive_sizes(width, height):
    min_side = min(width, height)
    return {
        'title_font_size': max(24, min_side // 10),
        'subtitle_font_size': max(12, min_side // 28),
        'option_font_size': max(6, min_side // 24),
        'spacing': max(10, height // 24),
        'title_y': height // 4,
        'button_width': max(120, width // 3),
        'button_height': max(36, height // 14)
    }

def create_fonts(sizes):
    return {
        'title': pygame.font.SysFont("Arial", sizes['title_font_size'], bold=True),
        'subtitle': pygame.font.SysFont("Arial", sizes['subtitle_font_size']),
        'option': pygame.font.SysFont("Arial", sizes['option_font_size'], bold=True)
    }

def calculate_spawn_effect(elapsed_time):
    if elapsed_time < SPAWN_DURATION:
        progress = elapsed_time / SPAWN_DURATION
        scale_factor = 1 - (1 - progress) ** 3
        return min(scale_factor, 1.0)
    return 1.0

def calculate_button_rect(base_rect, scale_factor, hovered, elapsed_time):
    scaled_width = int(base_rect.width * scale_factor)
    scaled_height = int(base_rect.height * scale_factor)
    scaled_x = base_rect.x + (base_rect.width - scaled_width) // 2
    scaled_y = base_rect.y + (base_rect.height - scaled_height) // 2
    button_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
    return button_rect

def draw_button(surface, button_rect, scale_factor, hovered, fonts, option_text):
    if scale_factor <= 0:
        return
    bg_color = BUTTON_BG_HOVER if hovered else BUTTON_BG_NORMAL
    border_color = BUTTON_BORDER_HOVER if hovered else BUTTON_BORDER_NORMAL
    text_color = BUTTON_TEXT_HOVER if hovered else BUTTON_TEXT_NORMAL
    bg_with_alpha = tuple(int(c * scale_factor) for c in bg_color)
    border_with_alpha = tuple(int(c * scale_factor) for c in border_color)
    text_alpha = int(255 * scale_factor)
    text_with_alpha = tuple(min(c, text_alpha) for c in text_color)
    pygame.draw.rect(surface, bg_with_alpha, button_rect, border_radius=10)
    pygame.draw.rect(surface, border_with_alpha, button_rect, 2, border_radius=10)
    option_surface = fonts['option'].render(option_text, True, text_with_alpha)
    option_rect = option_surface.get_rect(center=button_rect.center)
    surface.blit(option_surface, option_rect)

def show_menu(screen, music_on, icon_on, icon_off):
    TYPING_SPEED = 0.05
    CURSOR_BLINK_SPEED = 2
    SUBTITLE_TEXT = "Uma jornada pela grade curricular."
    SUBTITLE_COLOR_ORANGE = (255, 180, 60)
    def draw_typing_subtitle_local(surface, fonts, width, subtitle_y, elapsed_time):
        chars_to_show = int(elapsed_time / TYPING_SPEED)
        chars_to_show = min(chars_to_show, len(SUBTITLE_TEXT))
        current_text = SUBTITLE_TEXT[:chars_to_show]
        show_cursor = False
        if chars_to_show < len(SUBTITLE_TEXT):
            cursor_cycle = elapsed_time * CURSOR_BLINK_SPEED
            show_cursor = (cursor_cycle % 1) < 0.5
        display_text = current_text + ("|" if show_cursor else "")
        if display_text:
            subtitle_surface = fonts['subtitle'].render(display_text, True, SUBTITLE_COLOR_ORANGE)
            if chars_to_show > 0:
                char_progress = (elapsed_time / TYPING_SPEED) - (chars_to_show - 1)
                char_alpha = min(1.0, char_progress)
                alpha_value = int(255 * char_alpha)
                subtitle_surface.set_alpha(alpha_value)
            subtitle_rect = subtitle_surface.get_rect(center=(width // 2, subtitle_y))
            surface.blit(subtitle_surface, subtitle_rect)
    clock = pygame.time.Clock()
    option = "Jogar"
    running = True
    start_time = pygame.time.get_ticks()
    gradient_surface = None
    last_size = None
    fonts = None
    sizes = None
    while running:
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) / 1000.0
        width, height = screen.get_size()
        current_size = (width, height)
        if current_size != last_size:
            gradient_surface = create_gradient_surface(width, height)
            sizes = calculate_responsive_sizes(width, height)
            fonts = create_fonts(sizes)
            last_size = current_size
        screen.blit(gradient_surface, (0, 0))
        pulse_scale = 1 + 0.03 * math.sin(elapsed_time * 2)
        title_surface = fonts['title'].render("BCC2048", True, TITLE_COLOR)
        title_size = (int(title_surface.get_width() * pulse_scale), int(title_surface.get_height() * pulse_scale))
        title_surface = pygame.transform.smoothscale(title_surface, title_size)
        title_height = title_surface.get_height()
        subtitle_surface = fonts['subtitle'].render("Uma jornada pela grade curricular.", True, (255, 180, 60))
        subtitle_height = subtitle_surface.get_height()
        button_height = sizes['button_height']
        spacing = sizes['spacing']
        total_block_height = title_height + spacing + subtitle_height + spacing * 2 + button_height
        top_y = (height - total_block_height) // 2
        title_rect = title_surface.get_rect(center=(width // 2, top_y + title_height // 2))
        screen.blit(title_surface, title_rect)
        subtitle_y = title_rect.bottom + spacing + subtitle_height // 2
        draw_typing_subtitle_local(screen, fonts, width, subtitle_y, elapsed_time)
        button_x = (width - sizes['button_width']) // 2
        button_y = subtitle_y + subtitle_height // 2 + spacing * 2
        base_button_rect = pygame.Rect(button_x, button_y, sizes['button_width'], sizes['button_height'])
        mouse_pos = pygame.mouse.get_pos()
        scale_factor = calculate_spawn_effect(elapsed_time)
        hovered = base_button_rect.collidepoint(mouse_pos) and scale_factor >= 1.0
        button_rect = calculate_button_rect(base_button_rect, scale_factor, hovered, elapsed_time)
        draw_button(screen, button_rect, scale_factor, hovered, fonts, option)
        if icon_on:
            music_button_rect = icon_on.get_rect(topright=(width - 15, 15))
            screen.blit(icon_on if music_on else icon_off, music_button_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE] and scale_factor >= 1.0:
                    return music_on
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if scale_factor >= 1.0 and button_rect.collidepoint(event.pos):
                    return music_on
                if icon_on and music_button_rect.collidepoint(event.pos):
                    music_on = not music_on
        clock.tick(MENU_FPS)

def restart_game():
    board = create_board()
    tiles = []
    spawn_tile(board, tiles)
    spawn_tile(board, tiles)
    return board, tiles, 0

def run_game():
    pygame.init()
    pygame.mixer.init()
    info = pygame.display.Info()
    screen_width = int(info.current_w * 0.7)
    screen_height = int(info.current_h * 0.75)
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("BCC2048")
    try:
        icon_size = (30, 30)
        icon_on_img = pygame.image.load("icons/music_on.png").convert_alpha()
        icon_off_img = pygame.image.load("icons/music_off.png").convert_alpha()
        restart_icon = pygame.image.load("icons/restart.png").convert_alpha()
        icon_on = pygame.transform.scale(icon_on_img, icon_size)
        icon_off = pygame.transform.scale(icon_off_img, icon_size)
        icon_restart = pygame.transform.scale(restart_icon, icon_size)
        icons_loaded = True
    except Exception:
        icons_loaded = False
        icon_on = icon_off = icon_restart = None
    music_on = True
    try:
        pygame.mixer.music.load("2048-song.mp3")
        if music_on:
            pygame.mixer.music.play(-1)
    except Exception:
        music_on = False
    if icons_loaded:
        music_on = show_menu(screen, music_on, icon_on, icon_off)
    else:
        show_menu(screen, music_on, None, None)
    flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
    current_w, current_h = screen.get_size()
    screen = pygame.display.set_mode((current_w, current_h), flags)
    pygame.display.set_caption("2048BCC")
    init_gl(*screen.get_size())
    font = pygame.font.SysFont("Arial", 20, bold=True)
    score_font = pygame.font.SysFont("Arial", 24, bold=True)
    board, tiles, score = restart_game()
    high_score = load_high_score()
    clock = pygame.time.Clock()
    game_over = False
    animations_done = True
    music_button_rect = None
    restart_button_rect = None
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                update_viewport_on_resize(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if music_button_rect and music_button_rect.collidepoint(event.pos):
                    music_on = not music_on
                    if music_on:
                        try:
                            pygame.mixer.music.play(-1)
                        except Exception:
                            pass
                    else:
                        pygame.mixer.music.stop()
                if restart_button_rect and restart_button_rect.collidepoint(event.pos):
                    board, tiles, score = restart_game()
                    game_over = False
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
                        elif event.key == pygame.K_ESCAPE:
                            board, tiles, score = restart_game()
                        if direction:
                            moved, points = move(board, tiles, direction)
                            if moved:
                                score += points
                                if score > high_score:
                                    high_score = score
                                    save_high_score(high_score)
                                animations_done = False
        for tile in tiles:
            tile.update(dt)
        cleanup_merged_tiles(tiles)
        if not animations_done and not are_animations_running(tiles):
            spawn_tile(board, tiles)
            animations_done = True
        if not game_over and is_game_over(board, tiles) and animations_done:
            game_over = True
        music_button_rect, restart_button_rect = draw_board_gl(
            board, tiles, score, high_score, font, score_font, game_over,
            music_on, icon_on, icon_off, icon_restart
        )
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
