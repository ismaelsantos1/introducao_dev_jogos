# =============================================================
#  CC Tensei — level.py
#  4 fases, cada uma dedicada a um pilar da POO.
#  Level(index) carrega automaticamente o layout correto.
# =============================================================

import pygame
import math
from constants import (
    OOPPillar, EnemyType,
    TILE, GROUND_Y, LEVEL_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH,
    PLAYER_W, PLAYER_H, NPC_INTERACT_R,
    BOSS_W, BOSS_H,
    GROUND_COL, GRASS, BLACK, WHITE, YELLOW,
    RED, GRAY,
    GATE_COL, GATE_OPEN, TERMINAL_COL,
)
from enemy import create_enemy, Enemy
from boss  import Boss
from npc   import NPC
from quiz  import Quiz


# =============================================================
#  Tabela de pilares por índice de fase
# =============================================================
_PILLARS = [
    OOPPillar.ENCAPSULAMENTO,
    OOPPillar.HERANCA,
    OOPPillar.POLIMORFISMO,
    OOPPillar.ABSTRACAO,
]


# =============================================================
#  Layouts de plataformas (compartilhados entre fases)
#  Cada fase usa o mesmo esqueleto, mudando apenas o visual
#  temático via cor de grama (definida por OOPPillar).
# =============================================================
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

# Cor da grama por fase (reforça a identidade visual)
_GRASS_COLOR = [
    ( 80, 180,  60),   # Fase 1 — verde padrão  (Encapsulamento)
    ( 60, 140, 200),   # Fase 2 — azul           (Herança)
    (200, 100,  40),   # Fase 3 — laranja        (Polimorfismo)
    (160,  50, 200),   # Fase 4 — roxo           (Abstração)
]


# =============================================================
#  Inimigos — os spawns ficam iguais; o que diferencia é a
#  dificuldade progressiva (mais VirusBig e VirusFast nas
#  fases avançadas).
# =============================================================
_ENEMY_SPAWNS = [
    # Fase 1 — Encapsulamento (mais fácil)
    [
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
    ],
    # Fase 2 — Herança (moderado)
    [
        (300,  GROUND_Y - 26, EnemyType.VIRUS),
        (550,  GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (800,  GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (1050, GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (1300, GROUND_Y - 26, EnemyType.VIRUS),
        (1550, GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (1800, GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (2050, GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (2300, GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (2550, GROUND_Y - 26, EnemyType.VIRUS),
        (2750, GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (2920, GROUND_Y - 42, EnemyType.VIRUS_BIG),
    ],
    # Fase 3 — Polimorfismo (difícil)
    [
        (250,  GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (480,  GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (720,  GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (970,  GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (1180, GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (1420, GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (1650, GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (1900, GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (2150, GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (2400, GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (2650, GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (2900, GROUND_Y - 42, EnemyType.VIRUS_BIG),
    ],
    # Fase 4 — Abstração (muito difícil)
    [
        (200,  GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (420,  GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (640,  GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (860,  GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (1080, GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (1300, GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (1520, GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (1740, GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (1960, GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (2180, GROUND_Y - 26, EnemyType.VIRUS_FAST),
        (2600, GROUND_Y - 42, EnemyType.VIRUS_BIG),
        (2880, GROUND_Y - 26, EnemyType.VIRUS_FAST),
    ],
]


# =============================================================
#  Terminais — dicas específicas de cada pilar
# =============================================================
_TERMINALS = [
    # Fase 1 — Encapsulamento
    [
        (480,  GROUND_Y - 32,
         "'private' oculta dados. Use get_saldo() para acessar."),
        (1100, GROUND_Y - 32,
         "Getters/setters controlam leitura e escrita de atributos."),
        (2520, GROUND_Y - 224,
         "Encapsulamento = protecao + controle de acesso."),
    ],
    # Fase 2 — Herança
    [
        (480,  GROUND_Y - 32,
         "class Cachorro(Animal): herda tudo de Animal."),
        (1100, GROUND_Y - 32,
         "super().__init__() chama o construtor da classe mae."),
        (2520, GROUND_Y - 224,
         "Heranca = reuso de codigo + hierarquia de classes."),
    ],
    # Fase 3 — Polimorfismo
    [
        (480,  GROUND_Y - 32,
         "Sobrescrever draw() em cada subclasse = polimorfismo."),
        (1100, GROUND_Y - 32,
         "Mesmo metodo, comportamentos distintos por objeto."),
        (2520, GROUND_Y - 224,
         "Duck typing: se tem o metodo, pode ser chamado."),
    ],
    # Fase 4 — Abstração
    [
        (480,  GROUND_Y - 32,
         "Classe abstrata define contrato; nao pode ser instanciada."),
        (1100, GROUND_Y - 32,
         "from abc import ABC, abstractmethod."),
        (2520, GROUND_Y - 224,
         "Abstracao = expor interface, ocultar implementacao."),
    ],
]


# =============================================================
#  Posições fixas (iguais em todas as fases)
# =============================================================
_PLAYER_START = (60,  GROUND_Y - PLAYER_H)
_BOSS_ROOM_X  = 2980
_BOSS_SPAWN   = (3100, GROUND_Y - BOSS_H)
_NPC_POS      = (940,  GROUND_Y - 44 - 128)


# =============================================================
#  Classe Terminal
# =============================================================
class Terminal:
    SIZE = 32

    def __init__(self, x, y, hint):
        self.rect   = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.hint   = hint
        self.hacked = False
        self.active = True

    def near_player(self, player):
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return math.hypot(dx, dy) <= NPC_INTERACT_R

    def draw(self, surface, offset, font_sm):
        if not self.active:
            return
        ox, oy = offset
        x = self.rect.x - ox
        y = self.rect.y - oy
        s = self.SIZE

        pygame.draw.rect(surface, BLACK, (x, y, s, s))
        body = (20, 180, 80) if self.hacked else TERMINAL_COL
        pygame.draw.rect(surface, body, (x + 2, y + 2, s - 4, s - 4))

        scr = (0, 255, 100) if self.hacked else (0, 180, 60)
        pygame.draw.rect(surface, scr, (x + 4, y + 4, 24, 14))

        label = ">OK" if self.hacked else ">_"
        surface.blit(font_sm.render(label, True, WHITE), (x + 5, y + 5))

        if not self.hacked:
            pulse = abs(math.sin(pygame.time.get_ticks() / 330)) * 3
            surface.blit(font_sm.render("[E]", True, YELLOW),
                         (x - 2, int(y - 16 - pulse)))

        if self.hacked:
            pygame.draw.rect(surface, (0, 30, 10),
                             (x - 60, y - 38, 180, 26))
            surface.blit(font_sm.render(self.hint[:40], True, (100, 255, 140)),
                         (x - 56, y - 35))


# =============================================================
#  Classe Level — genérica, parametrizada por index (0-3)
# =============================================================
class Level:
    """
    Fase do jogo.  Recebe um índice 0-3 e carrega automaticamente
    o pilar, os inimigos, terminais, NPC e quiz correspondentes.

    index 0 → Encapsulamento
    index 1 → Herança
    index 2 → Polimorfismo
    index 3 → Abstração
    """

    def __init__(self, index=0):
        if index < 0 or index > 3:
            index = 0

        self.index         = index
        self.pillar        = _PILLARS[index]
        self.boss_defeated = False
        self.quiz_passed   = False

        # Plataformas
        self.platforms = [pygame.Rect(x, y, w, h) for x, y, w, h in _PLATFORMS]

        # Inimigos do índice correto
        self.enemies = [
            create_enemy(t, x, y) for x, y, t in _ENEMY_SPAWNS[index]
        ]

        # NPC com o pilar correto
        self.npcs = [NPC(*_NPC_POS, self.pillar)]

        # Terminais com dicas do pilar correto
        self.terminals = [
            Terminal(x, y, hint) for x, y, hint in _TERMINALS[index]
        ]

        # Boss
        self.boss = Boss(*_BOSS_SPAWN)
        self.boss.arena_min_x = _BOSS_SPAWN[0] - 280.0
        self.boss.arena_max_x = _BOSS_SPAWN[0] + 280.0

        # Quiz com o pilar correto
        self.quiz = Quiz(self.pillar)

        self.player_start   = _PLAYER_START
        self.boss_door_rect = pygame.Rect(_BOSS_ROOM_X, 0, 64, SCREEN_HEIGHT)

    # ----------------------------------------------------------
    def reset(self):
        """Reinicia inimigos, terminais e quiz ao morrer."""
        self.enemies = [
            create_enemy(t, x, y) for x, y, t in _ENEMY_SPAWNS[self.index]
        ]
        for t in self.terminals:
            t.hacked = False
        if not self.boss_defeated:
            self.boss = Boss(*_BOSS_SPAWN)
            self.boss.arena_min_x = _BOSS_SPAWN[0] - 280.0
            self.boss.arena_max_x = _BOSS_SPAWN[0] + 280.0
        self.quiz = Quiz(self.pillar)
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

    def player_at_boss_door(self, player):
        return self.boss_door_rect.colliderect(player.rect)

    def is_complete(self):
        return self.boss_defeated

    # ----------------------------------------------------------
    def draw(self, surface, offset, font_sm):
        ox, oy = offset
        grass_color = _GRASS_COLOR[self.index]

        # Plataformas
        for plat in self.platforms:
            rx = plat.x - ox
            ry = plat.y - oy
            pygame.draw.rect(surface, GROUND_COL, (rx, ry, plat.w, plat.h))
            pygame.draw.rect(surface, grass_color, (rx, ry, plat.w, TILE // 2))
            for seg in range(0, plat.w, TILE):
                pygame.draw.line(surface, (80, 50, 20),
                                 (rx + seg, ry + TILE),
                                 (rx + seg, ry + plat.h), 1)
            pygame.draw.rect(surface, (50, 30, 10),
                             (rx, ry, plat.w, plat.h), 2)

        # Terminais
        for t in self.terminals:
            t.draw(surface, offset, font_sm)

        # Porta do Boss
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
