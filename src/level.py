# =============================================================
#  CC Tensei — level.py
#  Fase 1: Encapsulamento
#  Layout de plataformas, inimigos, NPC, terminais e boss room.
# =============================================================

import pygame
import math
from constants import (
    OOPPillar, EnemyType,
    TILE, GROUND_Y, LEVEL_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH,
    PLAYER_W, PLAYER_H, NPC_INTERACT_R,
    BOSS_W, BOSS_H,
    GROUND_COL, GRASS, PLATFORM, BLACK, WHITE, YELLOW,
    GREEN, RED, GRAY, DARKGRAY, LIGHTGRAY,
    GATE_COL, GATE_OPEN, TERMINAL_COL,
)
from enemy  import create_enemy, Enemy
from boss   import Boss
from npc    import NPC
from quiz   import Quiz


# =============================================================
#  Dados estáticos da Fase 1
# =============================================================

# (x, y, largura, altura)
_PLATFORMS = [
    # Chão principal
    (0,    GROUND_Y, 900,  TILE * 2),
    (920,  GROUND_Y, 600,  TILE * 2),
    (1540, GROUND_Y, 800,  TILE * 2),
    (2360, GROUND_Y, 1000, TILE * 2),
    # Plataformas flutuantes — bloco 1
    (200,  GROUND_Y - 96,  128, TILE),
    (400,  GROUND_Y - 160, 128, TILE),
    (600,  GROUND_Y - 96,  128, TILE),
    # Bloco 2 — zona NPC
    (920,  GROUND_Y - 128, 160, TILE),
    (1120, GROUND_Y - 80,  128, TILE),
    (1300, GROUND_Y - 160, 96,  TILE),
    # Bloco 3 — zona de combate
    (1600, GROUND_Y - 96,  160, TILE),
    (1820, GROUND_Y - 160, 128, TILE),
    (2000, GROUND_Y - 96,  96,  TILE),
    (2120, GROUND_Y - 128, 160, TILE),
    # Plataforma alta (terminal 3)
    (2500, GROUND_Y - 192, 128, TILE),
    (2700, GROUND_Y - 128, 128, TILE),
    # Ante-sala do Boss
    (3000, GROUND_Y - 64,  300, TILE),
]

# (x, y, tipo)
_ENEMY_SPAWNS = [
    (350,  GROUND_Y - 26, EnemyType.VIRUS),
    (700,  GROUND_Y - 26, EnemyType.VIRUS),
    (960,  GROUND_Y - 26, EnemyType.VIRUS_FAST),
    (1200, GROUND_Y - 26, EnemyType.VIRUS),
    (1640, GROUND_Y - 26, EnemyType.VIRUS_FAST),
    (1900, GROUND_Y - 42, EnemyType.VIRUS_BIG),
    (2100, GROUND_Y - 26, EnemyType.VIRUS),
    (2200, GROUND_Y - 26, EnemyType.VIRUS_FAST),
    (2450, GROUND_Y - 26, EnemyType.VIRUS),
    (2650, GROUND_Y - 42, EnemyType.VIRUS_BIG),
    (2850, GROUND_Y - 26, EnemyType.VIRUS),
    (2950, GROUND_Y - 26, EnemyType.VIRUS_FAST),
]

# (x, y, dica exibida ao hackear)
_TERMINALS = [
    (480,  GROUND_Y - 32,
     "'private' oculta dados. Use get_saldo() para acessar."),
    (1100, GROUND_Y - 32,
     "Getters/setters controlam leitura e escrita de atributos."),
    (2520, GROUND_Y - 224,
     "Encapsulamento = protecao + controle de acesso."),
]

_PLAYER_START  = (60,  GROUND_Y - PLAYER_H)
_BOSS_ROOM_X   = 2980          # x da porta do Boss
_BOSS_SPAWN    = (3100, GROUND_Y - BOSS_H)
_NPC_POS       = (940,  GROUND_Y - 44 - 128)


# =============================================================
#  Classe Terminal
# =============================================================
class Terminal:
    SIZE = 32

    def __init__(self, x: float, y: float, hint: str):
        self.rect   = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.hint   = hint
        self.hacked = False
        self.active = True

    def near_player(self, player) -> bool:
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return math.hypot(dx, dy) <= NPC_INTERACT_R

    def draw(self, surface: pygame.Surface, offset: tuple,
             font_sm: pygame.font.Font) -> None:
        if not self.active:
            return
        ox, oy = offset
        x = self.rect.x - ox
        y = self.rect.y - oy
        s = self.SIZE

        # Gabinete
        pygame.draw.rect(surface, BLACK, (x, y, s, s))
        body = (20, 180, 80) if self.hacked else TERMINAL_COL
        pygame.draw.rect(surface, body, (x + 2, y + 2, s - 4, s - 4))

        # Tela
        scr = (0, 255, 100) if self.hacked else (0, 180, 60)
        pygame.draw.rect(surface, scr, (x + 4, y + 4, 24, 14))

        label = ">OK" if self.hacked else ">_"
        lbl   = font_sm.render(label, True, WHITE)
        surface.blit(lbl, (x + 5, y + 5))

        # Ícone de interação
        if not self.hacked:
            pulse = abs(math.sin(pygame.time.get_ticks() / 330)) * 3
            hint_txt = font_sm.render("[E]", True, YELLOW)
            surface.blit(hint_txt, (x - 2, int(y - 16 - pulse)))

        # Dica após hackear
        if self.hacked:
            pygame.draw.rect(surface, (0, 30, 10),
                             (x - 60, y - 38, 180, 26))
            h = font_sm.render(self.hint[:40], True, (100, 255, 140))
            surface.blit(h, (x - 56, y - 35))


# =============================================================
#  Classe Level
# =============================================================
class Level:
    """
    Fase 1 — Encapsulamento.
    Contém toda a geometria, entidades e estado da fase.
    """

    def __init__(self):
        self.pillar       = OOPPillar.ENCAPSULAMENTO
        self.index        = 0
        self.boss_defeated = False
        self.quiz_passed   = False

        # Plataformas como pygame.Rect
        self.platforms: list[pygame.Rect] = [
            pygame.Rect(x, y, w, h) for x, y, w, h in _PLATFORMS
        ]

        # Inimigos
        self.enemies: list[Enemy] = [
            create_enemy(t, x, y) for x, y, t in _ENEMY_SPAWNS
        ]

        # NPC
        self.npcs: list[NPC] = [
            NPC(*_NPC_POS, OOPPillar.ENCAPSULAMENTO)
        ]

        # Terminais
        self.terminals: list[Terminal] = [
            Terminal(x, y, hint) for x, y, hint in _TERMINALS
        ]

        # Boss
        self.boss = Boss(*_BOSS_SPAWN)
        self.boss.arena_min_x = _BOSS_SPAWN[0] - 280.0
        self.boss.arena_max_x = _BOSS_SPAWN[0] + 280.0

        # Quiz
        self.quiz = Quiz(OOPPillar.ENCAPSULAMENTO)

        # Posição inicial do player
        self.player_start = _PLAYER_START

        # Zona da porta do boss (retângulo estreito)
        self.boss_door_rect = pygame.Rect(_BOSS_ROOM_X, 0, 64, SCREEN_HEIGHT)

    # ----------------------------------------------------------
    def reset(self) -> None:
        """Reinicia inimigos, terminais e quiz ao morrer."""
        self.enemies = [create_enemy(t, x, y) for x, y, t in _ENEMY_SPAWNS]
        for t in self.terminals:
            t.hacked = False
        if not self.boss_defeated:
            self.boss = Boss(*_BOSS_SPAWN)
            self.boss.arena_min_x = _BOSS_SPAWN[0] - 280.0
            self.boss.arena_max_x = _BOSS_SPAWN[0] + 280.0
        self.quiz = Quiz(OOPPillar.ENCAPSULAMENTO)
        self.quiz_passed = False
        for npc in self.npcs:
            npc.reset()

    # ----------------------------------------------------------
    def check_terminal_interaction(self, player):
        """Processa hack; retorna a dica do terminal ou None."""
        keys = pygame.key.get_pressed()
        if not (keys[pygame.K_e] or keys[pygame.K_s]):
            return None
        for t in self.terminals:
            if t.active and not t.hacked and t.near_player(player):
                t.hacked = True
                player.terminals_hacked += 1
                return t.hint
        return None

    def player_at_boss_door(self, player) -> bool:
        return self.boss_door_rect.colliderect(player.rect)

    def is_complete(self) -> bool:
        return self.boss_defeated

    # ----------------------------------------------------------
    def draw(self, surface: pygame.Surface,
             offset: tuple, font_sm: pygame.font.Font) -> None:
        ox, oy = offset

        # ---- Plataformas ----
        for plat in self.platforms:
            rx = plat.x - ox
            ry = plat.y - oy
            # Terra
            pygame.draw.rect(surface, GROUND_COL, (rx, ry, plat.w, plat.h))
            # Grama no topo
            pygame.draw.rect(surface, GRASS, (rx, ry, plat.w, TILE // 2))
            # Linhas de segmento
            for seg in range(0, plat.w, TILE):
                pygame.draw.line(surface, (80, 50, 20, 80),
                                 (rx + seg, ry + TILE),
                                 (rx + seg, ry + plat.h), 1)
            # Borda
            pygame.draw.rect(surface, (50, 30, 10),
                             (rx, ry, plat.w, plat.h), 2)

        # ---- Terminais ----
        for t in self.terminals:
            t.draw(surface, offset, font_sm)

        # ---- Porta do Boss ----
        gx = _BOSS_ROOM_X - ox
        gy = SCREEN_HEIGHT - TILE * 6 - oy
        gw, gh = 60, TILE * 4
        color = GATE_OPEN if self.quiz_passed else GATE_COL
        pygame.draw.rect(surface, BLACK, (gx, gy, gw, gh))
        pygame.draw.rect(surface, color, (gx + 2, gy + 2, gw - 4, gh - 4))
        if not self.quiz_passed:
            pygame.draw.rect(surface, (200, 180, 20),
                             (gx + gw // 2 - 8, gy + gh // 2 - 8, 16, 16))
            surface.blit(font_sm.render("?", True, BLACK),
                         (gx + gw // 2 - 4, gy + gh // 2 - 7))
        else:
            surface.blit(font_sm.render(">>", True, WHITE),
                         (gx + 8, gy + gh // 2 - 8))
        surface.blit(font_sm.render("BOSS", True, RED),
                     (gx + 4, gy - 18))
