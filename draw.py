import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from settings import TILE_SIZE, HEADER_HEIGHT, COLORS, COLOR_TOP, COLOR_BOTTOM
import math

_text_texture_cache = {}

_draw_cache = {
    'last_size': None,
    'bg_tex': None,        # (tex_id, w, h)
    'score_font': None,
    'title_font': None,
}

def init_gl(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)

def calculate_responsive_sizes(width, height):
    # Esplhar a lógica de dimensionamento do menu para que o board
    min_side = min(width, height)
    return {
        'title_font_size': max(24, min_side // 10),
        'subtitle_font_size': max(12, min_side // 28),
        'option_font_size': max(6, min_side // 24),
        'spacing': max(10, height // 24),
        'title_y': max(int(height * 0.02), height // 12),
        'button_width': max(120, width // 3),
        'button_height': max(36, height // 14)
    }

def update_viewport_on_resize(w, h):
    pygame.display.set_mode((w, h), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
    init_gl(w, h)

def surface_to_texture(surface):
    data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_size()
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, data)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id, width, height

def get_text_texture(text, font, color):
    key = (text, font.get_linesize(), color)
    if key in _text_texture_cache:
        return _text_texture_cache[key]
    surface = font.render(text, True, color)
    tex_id, w, h = surface_to_texture(surface)
    _text_texture_cache[key] = (tex_id, w, h, surface)
    return _text_texture_cache[key]

def draw_filled_rect(x, y, w, h, color):
    r, g, b = [c/255.0 for c in color]
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

def draw_rect_border(x, y, w, h, thickness, color):
    r, g, b = [c/255.0 for c in color]
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + thickness)
    glVertex2f(x, y + thickness)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(x, y + h - thickness)
    glVertex2f(x + w, y + h - thickness)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + thickness, y)
    glVertex2f(x + thickness, y + h)
    glVertex2f(x, y + h)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(x + w - thickness, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x + w - thickness, y + h)
    glEnd()

def draw_textured_quad(x, y, w, h, tex_id):
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor4f(1,1,1,1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(x, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 0); glVertex2f(x, y + h)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)

def draw_board_gl(board, tiles, score, high_score, font, score_font, game_over, music_on, icon_on, icon_off, icon_restart):
    width, height = pygame.display.get_surface().get_size()
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClear(GL_COLOR_BUFFER_BIT)

    current_size = (width, height)
    if _draw_cache['last_size'] != current_size:
        grad_h = min(256, max(2, height))
        grad_small = pygame.Surface((1, grad_h)).convert_alpha()
        for y in range(grad_h):
            ratio = y / (grad_h - 1)
            r = int(COLOR_TOP[0] * (1 - ratio) + COLOR_BOTTOM[0] * ratio)
            g = int(COLOR_TOP[1] * (1 - ratio) + COLOR_BOTTOM[1] * ratio)
            b = int(COLOR_TOP[2] * (1 - ratio) + COLOR_BOTTOM[2] * ratio)
            grad_small.set_at((0, y), (r, g, b, 255))
        grad_surf = pygame.transform.smoothscale(grad_small, (width, height))

        if _draw_cache['bg_tex']:
            try:
                glDeleteTextures([_draw_cache['bg_tex'][0]])
            except Exception:
                pass
        bg_tex_id, bw, bh = surface_to_texture(grad_surf)
        _draw_cache['bg_tex'] = (bg_tex_id, bw, bh)

    sizes = calculate_responsive_sizes(width, height)
    board_size = len(board)
    header_height = int(height * 0.12)
    max_board_width = int(width * 0.9)
    max_board_height = int((height - header_height) * 0.85)
    est_tile = min(max_board_width // max(1, board_size), max_board_height // max(1, board_size))

    score_font_size = max(14, min(48, est_tile // 3, sizes['title_font_size']))
    title_font_size = score_font_size
    _draw_cache['score_font'] = pygame.font.SysFont("Arial", score_font_size, bold=True)
    _draw_cache['title_font'] = pygame.font.SysFont("Arial", title_font_size, bold=True)
    _draw_cache['last_size'] = current_size

    # BG - cached
    if _draw_cache.get('bg_tex'):
        bg_tex_id, bw, bh = _draw_cache['bg_tex']
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, bg_tex_id)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(0, 0)
        glTexCoord2f(1, 1); glVertex2f(width, 0)
        glTexCoord2f(1, 0); glVertex2f(width, height)
        glTexCoord2f(0, 0); glVertex2f(0, height)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)

    board_size = len(board)
    header_height = int(height * 0.12)
    max_board_width = int(width * 0.9)
    max_board_height = int((height - header_height) * 0.85)
    tile_size = min(max_board_width // board_size, max_board_height // board_size)
    board_pixel_width = tile_size * board_size
    board_pixel_height = tile_size * board_size
    offset_x = (width - board_pixel_width) // 2
    offset_y = header_height + ((height - header_height) - board_pixel_height) // 2

    local_score_font = score_font if score_font is not None else _draw_cache['score_font']
    local_title_font = font if font is not None else _draw_cache['title_font']

    # Titulo
    sizes_local = calculate_responsive_sizes(width, height)
    # top padding
    top_margin = max(20, int(height * 0.05))
    title_color = (255, 180, 60)
    title_surface_text = "BCC2048"
    if font is not None:
        title_font_to_use = font
    else:
        base_font = _draw_cache.get('title_font')
        if base_font:
            base_linesize = base_font.get_linesize()
            title_font_size = max(24, int(base_linesize * 1.5))
        else:
            title_font_size = max(24, int(sizes_local['title_font_size'] * 1.5))
        title_font_to_use = pygame.font.SysFont("Arial", title_font_size, bold=True)

    tex_title_id, twt, tht, surft = get_text_texture(title_surface_text, title_font_to_use, title_color)
    title_x = offset_x
    title_y = top_margin
    draw_textured_quad(title_x, title_y, twt, tht, tex_title_id)

    score_text = f"Pontos: {score}"
    tex_id, tw, th, surf = get_text_texture(score_text, local_score_font, (255,255,255))
    score_x = offset_x
    score_y = title_y + tht + max(6, int(height * 0.01))
    draw_textured_quad(score_x, score_y, tw, th, tex_id)

    high_text = f"Recorde: {high_score}"
    tex_id2, tw2, th2, surf2 = get_text_texture(high_text, local_score_font, (255,215,0))
    draw_textured_quad(score_x + tw + 20, score_y, tw2, th2, tex_id2)

    music_button_rect = None
    restart_button_rect = None
    if icon_on is not None and icon_off is not None and icon_restart is not None:
        padding = 10
        icon_to_draw = icon_on if music_on else icon_off

        def surf_to_cached_tex(surf):
            key = ("ICON", id(surf), surf.get_size())
            if key in _text_texture_cache:
                return _text_texture_cache[key][0], _text_texture_cache[key][1], _text_texture_cache[key][2]
            tex_id, w, h = surface_to_texture(surf)
            _text_texture_cache[key] = (tex_id, w, h, surf)
            return tex_id, w, h

        tex_music_id, mw, mh = surf_to_cached_tex(icon_to_draw)
        music_button_rect = pygame.Rect(width - padding - mw, padding, mw, mh)

        tex_restart_id, rw, rh = surf_to_cached_tex(icon_restart)
        restart_button_rect = pygame.Rect(music_button_rect.left - padding - rw, padding, rw, rh)

        draw_textured_quad(music_button_rect.x, music_button_rect.y, music_button_rect.width, music_button_rect.height, tex_music_id)
        draw_textured_quad(restart_button_rect.x, restart_button_rect.y, restart_button_rect.width, restart_button_rect.height, tex_restart_id)

    for y in range(board_size):
        for x in range(board_size):
            rect_x = offset_x + x * tile_size
            rect_y = offset_y + y * tile_size
            draw_filled_rect(rect_x, rect_y, tile_size, tile_size, (50,50,50))
            draw_rect_border(rect_x, rect_y, tile_size, tile_size, 2, (0,0,0))

    for tile in tiles:
        center_x = offset_x + tile.x_draw * tile_size + tile_size / 2.0
        center_y = offset_y + tile.y_draw * tile_size + tile_size / 2.0
        w = h = tile_size * tile.scale
        x = center_x - w / 2.0
        y = center_y - h / 2.0

        color = COLORS.get(tile.value, (200,200,200))
        draw_filled_rect(x, y, w, h, color)
        draw_rect_border(x, y, w, h, 2, (0,0,0))

        text_surf = pygame.font.SysFont("Arial", max(12, int(tile_size*0.25)), bold=True)
        tex_id, tw, th, surf = get_text_texture(tile.value, text_surf, (255,255,255))
        scale = min((w - 8)/tw, (h - 8)/th, 1.0)
        draw_textured_quad(center_x - tw*scale/2.0, center_y - th*scale/2.0, tw*scale, th*scale, tex_id)

    if game_over:
        glEnable(GL_BLEND)
        glColor4f(0,0,0,0.7)
        glBegin(GL_QUADS)
        glVertex2f(0,0)
        glVertex2f(width,0)
        glVertex2f(width,height)
        glVertex2f(0,height)
        glEnd()
        glColor4f(1,0,0,1)
        big_font = pygame.font.SysFont("Arial", 48, bold=True)
        tex_id, tw, th, surf = get_text_texture("GAME OVER", big_font, (255,0,0))
        draw_textured_quad((width-tw)/2, (height-th)/2-20, tw, th, tex_id)
        small_font = pygame.font.SysFont("Arial", 24, bold=True)
        tex_id2, tw2, th2, surf2 = get_text_texture("Pressione ESC para reiniciar", small_font, (255,255,255))
        draw_textured_quad((width-tw2)/2, (height-th2)/2+30, tw2, th2, tex_id2)

    return music_button_rect, restart_button_rect
