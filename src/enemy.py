# =============================================================
#  CC Tensei — enemy.py
#  Hierarquia de inimigos (Vírus).
#  Demonstra Herança e Polimorfismo da POO:
#    Enemy (base) → Virus → VirusRapido / VirusGrande
# =============================================================

import pygame
import math
from constants import (
    EnemyType, Direction, GRAVITY, SCREEN_HEIGHT,
    VIRUS_HP, VIRUS_SPEED, VIRUS_DAMAGE, VIRUS_W, VIRUS_H,
    VFAST_HP, VFAST_SPEED, VFAST_DAMAGE, VFAST_W, VFAST_H,
    VBIG_HP,  VBIG_SPEED,  VBIG_DAMAGE,  VBIG_W,  VBIG_H,
    PATROL_RANGE,
    VIRUS_COL, VFAST_COL, VBIG_COL,
    BLACK, WHITE, YELLOW, HP_GREEN, DARKGRAY,
)


# =============================================================
#  Classe base — Enemy
# =============================================================
class Enemy:
    """
    Classe base (análoga à superclasse Inimigo do escopo POO).
    Define interface comum: update(), take_damage(), draw().
    """

    def __init__(self, x: float, y: float,
                 hp: int, speed: float, damage: int,
                 w: int, h: int, enemy_type: EnemyType):
        self.rect       = pygame.Rect(x, y, w, h)
        self._x         = float(x)
        self._y         = float(y)
        self._vx        = 0.0
        self._vy        = 0.0
        self.hp         = hp
        self.max_hp     = hp
        self.speed      = speed
        self.damage     = damage
        self.enemy_type = enemy_type
        self.direction  = Direction.LEFT
        self.origin_x   = float(x)
        self.on_ground  = False
        self.active     = True
        self._iframe    = 0.0

    # ----------------------------------------------------------
    def update(self, dt, platforms):  # type: ignore
        if not self.active:
            return
        if self._iframe > 0:
            self._iframe -= dt

        self._ai(dt)
        self._vy += GRAVITY * dt

        self._x += self._vx * dt
        self._y += self._vy * dt
        self.rect.x = int(self._x)
        self.rect.y = int(self._y)

        self._resolve_ground(platforms)

    def _ai(self, dt: float) -> None:
        """IA de patrulha — sobrescrita pelas subclasses."""
        left_edge  = self.origin_x - PATROL_RANGE
        right_edge = self.origin_x + PATROL_RANGE
        if self.direction == Direction.LEFT:
            self._vx = -self.speed
            if self._x <= left_edge:
                self.direction = Direction.RIGHT
        else:
            self._vx = self.speed
            if self._x >= right_edge:
                self.direction = Direction.LEFT

    def _resolve_ground(self, platforms):  # type: ignore
        self.on_ground = False
        for plat in platforms:
            if not self.rect.colliderect(plat):
                continue
            overlap_t = self.rect.bottom - plat.top
            overlap_b = plat.bottom      - self.rect.top
            if overlap_t < overlap_b and overlap_t < self.rect.height * 0.7:
                self._y = float(plat.top - self.rect.height)
                self._vy = 0.0
                self.on_ground = True
            else:
                self._y = float(plat.bottom)
                self._vy = 0.0
            self.rect.y = int(self._y)

        if self._y + self.rect.height >= SCREEN_HEIGHT:
            self._y      = float(SCREEN_HEIGHT - self.rect.height)
            self._vy     = 0.0
            self.on_ground = True
            self.rect.y  = int(self._y)

    # ----------------------------------------------------------
    def take_damage(self, amount: int) -> None:
        if not self.active or self._iframe > 0:
            return
        self.hp     -= amount
        self._iframe = 0.15
        if self.hp <= 0:
            self.hp     = 0
            self.active = False

    def check_player_collision(self, player) -> None:
        if self.active and player.active and self.rect.colliderect(player.rect):
            player.take_damage(self.damage)

    # ----------------------------------------------------------
    def draw(self, surface, offset):  # type: ignore
        """Sobrescrita por cada subclasse."""
        pass

    def _draw_hp_bar(self, surface, ox, oy):  # type: ignore
        bx = self.rect.x - ox
        by = self.rect.y - oy - 7
        bw = self.rect.width
        pygame.draw.rect(surface, DARKGRAY, (bx, by, bw, 4))
        filled = int(bw * (self.hp / self.max_hp))
        pygame.draw.rect(surface, HP_GREEN, (bx, by, filled, 4))


# =============================================================
#  Virus — patrulha simples
# =============================================================
class Virus(Enemy):
    """Vírus Simples: blob vermelho com símbolo BUG."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, VIRUS_HP, VIRUS_SPEED, VIRUS_DAMAGE,
                         VIRUS_W, VIRUS_H, EnemyType.VIRUS)

    def draw(self, surface: pygame.Surface, offset: tuple) -> None:
        if not self.active:
            return
        if self._iframe > 0 and int(self._iframe * 12) % 2 == 0:
            return
        ox, oy = offset
        x = self.rect.x - ox
        y = self.rect.y - oy
        w, h = VIRUS_W, VIRUS_H

        pygame.draw.rect(surface, DARKGRAY, (x, y, w, h))
        pygame.draw.rect(surface, VIRUS_COL, (x + 1, y + 1, w - 2, h - 2))

        # Olhos
        pygame.draw.rect(surface, WHITE, (x + 4, y + 6, 5, 5))
        pygame.draw.rect(surface, WHITE, (x + w - 9, y + 6, 5, 5))
        px = 2 if self.direction == Direction.RIGHT else 1
        pygame.draw.rect(surface, BLACK, (x + 4 + px, y + 7, 3, 3))
        pygame.draw.rect(surface, BLACK, (x + w - 9 + px, y + 7, 3, 3))

        # Boca serrilhada
        for k in range(4):
            ty = y + h - 9 if k % 2 == 0 else y + h - 6
            pygame.draw.rect(surface, WHITE, (x + 4 + k * 4, ty, 3, 3))

        self._draw_hp_bar(surface, ox, oy)


# =============================================================
#  VirusRapido — veloz com salto periódico
# =============================================================
class VirusRapido(Enemy):
    """Vírus Rápido: mais veloz, salta periodicamente."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, VFAST_HP, VFAST_SPEED, VFAST_DAMAGE,
                         VFAST_W, VFAST_H, EnemyType.VIRUS_FAST)
        self._jump_timer = 0.0

    def _ai(self, dt: float) -> None:
        super()._ai(dt)
        self._jump_timer += dt
        if self._jump_timer >= 2.0 and self.on_ground:
            self._vy          = -420.0
            self.on_ground    = False
            self._jump_timer  = 0.0

    def draw(self, surface: pygame.Surface, offset: tuple) -> None:
        if not self.active:
            return
        if self._iframe > 0 and int(self._iframe * 12) % 2 == 0:
            return
        ox, oy = offset
        x = self.rect.x - ox
        y = self.rect.y - oy
        w, h = VFAST_W, VFAST_H

        # Corpo losango (2 retângulos)
        pygame.draw.rect(surface, DARKGRAY,  (x + w // 4, y, w // 2, h))
        pygame.draw.rect(surface, VFAST_COL, (x + w // 4 + 1, y + 1, w // 2 - 2, h - 2))

        # Olho central
        pygame.draw.rect(surface, WHITE, (x + w // 2 - 4, y + h // 2 - 4, 8, 8))
        pygame.draw.rect(surface, BLACK, (x + w // 2 - 2, y + h // 2 - 2, 4, 4))

        # Raios laterais
        pygame.draw.rect(surface, YELLOW, (x, y + h // 2 - 2, w // 4, 3))
        pygame.draw.rect(surface, YELLOW, (x + 3 * w // 4, y + h // 2 - 2, w // 4, 3))

        self._draw_hp_bar(surface, ox, oy)


# =============================================================
#  VirusGrande — tanque de 4 olhos
# =============================================================
class VirusGrande(Enemy):
    """Vírus Grande: mais lento, muito HP, dano alto."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, VBIG_HP, VBIG_SPEED, VBIG_DAMAGE,
                         VBIG_W, VBIG_H, EnemyType.VIRUS_BIG)

    def draw(self, surface: pygame.Surface, offset: tuple) -> None:
        if not self.active:
            return
        if self._iframe > 0 and int(self._iframe * 12) % 2 == 0:
            return
        ox, oy = offset
        x = self.rect.x - ox
        y = self.rect.y - oy
        w, h = VBIG_W, VBIG_H

        pygame.draw.rect(surface, BLACK,    (x, y, w, h))
        pygame.draw.rect(surface, (200, 20, 100), (x + 2, y + 2, w - 4, h - 4))

        # 4 olhos
        eyes = [
            (x + 6,      y + 8),
            (x + w - 14, y + 8),
            (x + 6,      y + h // 2),
            (x + w - 14, y + h // 2),
        ]
        for ex, ey in eyes:
            pygame.draw.rect(surface, YELLOW, (ex, ey, 8, 8))
            pygame.draw.rect(surface, BLACK,  (ex + 2, ey + 2, 4, 4))

        # Boca
        pygame.draw.rect(surface, BLACK, (x + 6, y + h - 14, w - 12, 6))
        for k in range(3):
            pygame.draw.rect(surface, WHITE, (x + 8 + k * 8, y + h - 14, 4, 3))

        self._draw_hp_bar(surface, ox, oy)


# =============================================================
#  Fábrica (Factory Method — padrão POO)
# =============================================================
def create_enemy(enemy_type: EnemyType, x: float, y: float) -> Enemy:
    """Instancia o inimigo correto a partir do tipo."""
    if enemy_type == EnemyType.VIRUS:
        return Virus(x, y)
    elif enemy_type == EnemyType.VIRUS_FAST:
        return VirusRapido(x, y)
    elif enemy_type == EnemyType.VIRUS_BIG:
        return VirusGrande(x, y)
    raise ValueError(f"Tipo de inimigo desconhecido: {enemy_type}")
