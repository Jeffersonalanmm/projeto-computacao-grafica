import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from settings import TILE_SIZE, HEADER_HEIGHT, COLORS
import math

_text_texture_cache = {}

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
    glClearColor(0.1176, 0.1176, 0.1176, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    board_size = len(board)
    header_height = int(height * 0.12)
    max_board_width = int(width * 0.9)
    max_board_height = int((height - header_height) * 0.85)
    tile_size = min(max_board_width // board_size, max_board_height // board_size)
    board_pixel_width = tile_size * board_size
    board_pixel_height = tile_size * board_size
    offset_x = (width - board_pixel_width) // 2
    offset_y = header_height + ((height - header_height) - board_pixel_height) // 2

    score_text = f"Pontos: {score}"
    tex_id, tw, th, surf = get_text_texture(score_text, score_font, (255,255,255))
    score_x = offset_x
    score_y = 10
    draw_textured_quad(score_x, score_y, tw, th, tex_id)

    high_text = f"Recorde: {high_score}"
    tex_id2, tw2, th2, surf2 = get_text_texture(high_text, score_font, (255,215,0))
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

