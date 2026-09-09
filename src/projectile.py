# =============================================================
#  CC Tensei — projectile.py
#  Projéteis binários "0" (rápido/fraco) e "1" (lento/forte).
#  Demonstra polimorfismo: mesma interface, dados distintos.
# =============================================================

import pygame
from constants import (
    ProjType, Direction,
    PROJ_ZERO_SPEED, PROJ_ZERO_DAMAGE, PROJ_ZERO_W, PROJ_ZERO_H,
    PROJ_ONE_SPEED,  PROJ_ONE_DAMAGE,  PROJ_ONE_W,  PROJ_ONE_H,
    PROJ0_COL, PROJ1_COL, BLACK, WHITE, LEVEL_WIDTH, SCREEN_HEIGHT,
)

# Tabela de dados por tipo (polimorfismo via dict — análogo à vtable)
_PROJ_DATA = {
    ProjType.ZERO: dict(speed=PROJ_ZERO_SPEED, damage=PROJ_ZERO_DAMAGE,
                        w=PROJ_ZERO_W, h=PROJ_ZERO_H, color=PROJ0_COL),
    ProjType.ONE:  dict(speed=PROJ_ONE_SPEED,  damage=PROJ_ONE_DAMAGE,
                        w=PROJ_ONE_W,  h=PROJ_ONE_H,  color=PROJ1_COL),
}


class Projectile:
    """
    Projétil binário disparado pelo player ou pelo boss.

    Atributos públicos
    ------------------
    active      : bool
    from_player : bool
    damage      : int
    rect        : pygame.Rect  (hitbox e posição)
    """

    def __init__(self, x: float, y: float,
                 direction: Direction, proj_type: ProjType,
                 from_player: bool = True):
        data = _PROJ_DATA[proj_type]
        self.proj_type   = proj_type
        self.from_player = from_player
        self.active      = True
        self.damage      = data["damage"]
        self._color      = data["color"]
        self._w          = data["w"]
        self._h          = data["h"]
        self._vx         = data["speed"] * direction.value
        self._vy         = 0.0
        # rect centralizado na posição de spawn
        self.rect = pygame.Rect(x - self._w // 2, y - self._h // 2,
                                self._w, self._h)
        self._x = float(self.rect.x)

    # ----------------------------------------------------------
    def update(self, dt: float) -> None:
        if not self.active:
            return
        self._x += self._vx * dt
        self.rect.x = int(self._x)

        # Desativa ao sair dos limites do nível
        if (self.rect.right < -64 or self.rect.left > LEVEL_WIDTH + 64
                or self.rect.bottom < -64 or self.rect.top > SCREEN_HEIGHT + 64):
            self.active = False

    def deactivate(self) -> None:
        self.active = False

    # ----------------------------------------------------------
    def draw(self, surface: pygame.Surface, offset: tuple) -> None:
        if not self.active:
            return
        rx = self.rect.x - offset[0]
        ry = self.rect.y - offset[1]
        draw_rect = pygame.Rect(rx, ry, self._w, self._h)

        if self.proj_type == ProjType.ZERO:
            # "0" — oval amarela com borda preta
            pygame.draw.rect(surface, BLACK, draw_rect, border_radius=4)
            inner = draw_rect.inflate(-2, -2)
            pygame.draw.rect(surface, self._color, inner, border_radius=3)
        else:
            # "1" — retângulo magenta com brilho central
            pygame.draw.rect(surface, BLACK, draw_rect, border_radius=2)
            inner = draw_rect.inflate(-2, -2)
            pygame.draw.rect(surface, self._color, inner, border_radius=1)
            # brilho
            shine = pygame.Rect(inner.centerx - 2, inner.y + 1, 4, inner.height - 2)
            pygame.draw.rect(surface, (255, 210, 245), shine)
