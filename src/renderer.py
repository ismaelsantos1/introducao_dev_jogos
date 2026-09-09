# =============================================================
#  CC Tensei — renderer.py
#  Background paralaxe (céu + nuvens) e telas de estado.
# =============================================================

import pygame
import math
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, LEVEL_WIDTH,
    BLACK, WHITE, GRAY, LIGHTGRAY, DARKGRAY,
    RED, GREEN, YELLOW, CLOUD,
)


# =============================================================
#  Nuvens
# =============================================================
class CloudSystem:
    """8 nuvens em movimento com paralaxe 0.2x em relação à câmera."""

    _N = 8

    def __init__(self):
        random.seed(42)
        self._clouds = [
            {
                "x":     float(random.randint(0, LEVEL_WIDTH)),
                "y":     float(random.randint(40, 160)),
                "speed": float(random.randint(12, 32)),
            }
            for _ in range(self._N)
        ]

    def update(self, dt: float) -> None:
        for c in self._clouds:
            c["x"] -= c["speed"] * dt
            if c["x"] < -140:
                c["x"] = float(LEVEL_WIDTH)

    def draw(self, surface: pygame.Surface, cam_x: float) -> None:
        for c in self._clouds:
            # Aplica paralaxe: nuvens se movem a 20% da câmera
            sx = c["x"] - cam_x * 0.2
            # Wrap para tela
            while sx < -140:
                sx += LEVEL_WIDTH + 140
            while sx > SCREEN_WIDTH + 140:
                sx -= LEVEL_WIDTH + 140
            _draw_cloud(surface, int(sx), int(c["y"]))


def _draw_cloud(surface: pygame.Surface, x: int, y: int) -> None:
    w, h = 120, 40
    pygame.draw.rect(surface, CLOUD, (x,      y + 12, w,      h - 12))
    pygame.draw.rect(surface, CLOUD, (x + 10, y,      w - 20, h))
    pygame.draw.rect(surface, CLOUD, (x + 30, y - 10, 60,     h - 8))


# =============================================================
#  Fundo
# =============================================================
def draw_background(surface: pygame.Surface) -> None:
    """Gradiente de céu em 3 faixas."""
    h3 = SCREEN_HEIGHT // 3
    pygame.draw.rect(surface, (70,  140, 220), (0, 0,    SCREEN_WIDTH, h3))
    pygame.draw.rect(surface, (100, 180, 240), (0, h3,   SCREEN_WIDTH, h3))
    pygame.draw.rect(surface, (140, 210, 255), (0, h3*2, SCREEN_WIDTH, SCREEN_HEIGHT - h3*2))


# =============================================================
#  Telas de estado
# =============================================================
def draw_main_menu(surface: pygame.Surface,
                   font_title: pygame.font.Font,
                   font_lg: pygame.font.Font,
                   font_sm: pygame.font.Font) -> None:

    surface.fill((10, 10, 30))

    # Grade de circuito decorativa
    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(surface, (30, 60, 30), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.line(surface, (30, 60, 30), (0, y), (SCREEN_WIDTH, y))

    # Título
    title = font_title.render("CC TENSEI", True, (80, 180, 255))
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 130))

    sub = font_lg.render("O Estudante Reencarnado no Mundo Digital", True, (140, 220, 140))
    surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 205))

    pygame.draw.line(surface, (80, 80, 160),
                     (SCREEN_WIDTH // 2 - 200, 248),
                     (SCREEN_WIDTH // 2 + 200, 248), 2)

    # Itens pulsantes
    t = pygame.time.get_ticks() / 500
    pulse_y = int(math.fabs(math.sin(t)) * 18)

    items = [("[ENTER]  Iniciar Jogo", WHITE, -pulse_y),
             ("[ESC]    Sair",          GRAY,  0)]
    for i, (text, color, dy) in enumerate(items):
        txt = font_lg.render(text, True, color)
        surface.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2,
                            325 + i * 68 + dy))

    # Créditos
    cr1 = font_sm.render("Disciplina: Introducao a Jogos | UERN", True, (80, 80, 120))
    cr2 = font_sm.render("Discente: Juscelino K P Junior", True, (80, 80, 120))
    surface.blit(cr1, (18, SCREEN_HEIGHT - 26))
    surface.blit(cr2, (SCREEN_WIDTH - cr2.get_width() - 18, SCREEN_HEIGHT - 26))


def draw_pause(surface: pygame.Surface,
               font_title: pygame.font.Font,
               font_nm: pygame.font.Font) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    msg = font_title.render("PAUSADO", True, WHITE)
    surface.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2,
                        SCREEN_HEIGHT // 2 - 60))
    hint = font_nm.render("[ESC] Continuar   |   [M] Menu", True, LIGHTGRAY)
    surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                         SCREEN_HEIGHT // 2 + 20))


def draw_game_over(surface: pygame.Surface,
                   font_title: pygame.font.Font,
                   font_nm: pygame.font.Font,
                   font_sm: pygame.font.Font) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((30, 0, 0, 220))
    surface.blit(overlay, (0, 0))

    title = font_title.render("GAME OVER", True, RED)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2,
                          SCREEN_HEIGHT // 2 - 90))

    sub = font_nm.render("Voce foi derrotado pelos virus digitais.", True, LIGHTGRAY)
    surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2,
                        SCREEN_HEIGHT // 2))

    t     = pygame.time.get_ticks() / 500
    alpha = int((math.fabs(math.sin(t)) * 0.4 + 0.6) * 255)
    hint  = font_nm.render("[ENTER] Tentar Novamente   |   [ESC] Menu",
                            True, (255, 255, 255))
    hint.set_alpha(alpha)
    surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                         SCREEN_HEIGHT // 2 + 60))


def draw_level_clear(surface: pygame.Surface,
                     level_index: int,
                     font_title: pygame.font.Font,
                     font_lg: pygame.font.Font,
                     font_nm: pygame.font.Font) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 40, 0, 200))
    surface.blit(overlay, (0, 0))

    title = font_title.render("FASE CONCLUIDA!", True, GREEN)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 130))

    pillars = ["Encapsulamento Dominado!",
               "Heranca Dominada!",
               "Polimorfismo Dominado!",
               "Abstracao Dominada!"]
    if 0 <= level_index < 4:
        sub = font_lg.render(pillars[level_index], True, YELLOW)
        surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 225))

    hint = font_nm.render("[ENTER] Proxima Fase", True, WHITE)
    surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                         SCREEN_HEIGHT // 2 + 50))


def draw_victory(surface: pygame.Surface,
                 font_title: pygame.font.Font,
                 font_lg: pygame.font.Font,
                 font_nm: pygame.font.Font) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 40, 220))
    surface.blit(overlay, (0, 0))

    # Confete
    t = pygame.time.get_ticks()
    for i in range(40):
        px = (i * 97 + 50) % SCREEN_WIDTH
        py = int((t / 1000 * (50 + i % 30) + i * 17) % SCREEN_HEIGHT)
        col = ((i * 60) % 256, (i * 90) % 256, 200)
        pygame.draw.rect(surface, col, (px, py, 6, 6))

    title = font_title.render("VITORIA!", True, YELLOW)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 110))

    sub = font_lg.render("Voce dominou os 4 Pilares da POO!", True, WHITE)
    surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 210))

    for i, txt in enumerate(["✓ Encapsulamento", "✓ Heranca",
                              "✓ Polimorfismo",   "✓ Abstracao"]):
        line = font_nm.render(txt, True, GREEN)
        surface.blit(line, (SCREEN_WIDTH // 2 - line.get_width() // 2,
                             305 + i * 40))

    hint = font_nm.render("[ENTER] Menu Principal", True, LIGHTGRAY)
    surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                         SCREEN_HEIGHT - 76))
