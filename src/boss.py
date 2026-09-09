# =============================================================
#  CC Tensei — boss.py
#  CPU-001: Boss da Fase 1 (Encapsulamento)
#
#  Mecânica temática: escudo de "encapsulamento" que só abre
#  em janelas específicas — só então recebe dano.
#  Duas fases de ataque: reta (fase 1) e leque (fase 2).
# =============================================================

import pygame
import math
from constants import (
    BossPhase, Direction, ProjType, GRAVITY, SCREEN_HEIGHT,
    BOSS_W, BOSS_H, BOSS_MAX_HP, BOSS_PHASE2_HP,
    BOSS_BULLET_SPEED, BOSS_SHOOT_DELAY, BOSS_DAMAGE,
    SHIELD_CYCLE, SHIELD_OPEN,
    BLACK, WHITE, YELLOW, HP_RED, DARKGRAY,
    BAR_W, BAR_H, SCREEN_WIDTH, HUD_MARGIN,
)
from projectile import Projectile


class Boss:
    """
    CPU-001 — guardião da Fase 1.

    Fases
    -----
    PHASE1: escudo ativo; abre por SHIELD_OPEN s a cada SHIELD_CYCLE s.
            Atira projétil reto em direção ao player.
    PHASE2: escudo cai; velocidade e cadência aumentam.
            Atira leque de 3 projéteis.
    DEAD  : animação de derrota.
    """

    _MOVE_SPEED_P1 = 90.0
    _MOVE_SPEED_P2 = 160.0

    def __init__(self, x: float, y: float):
        self.rect   = pygame.Rect(x, y, BOSS_W, BOSS_H)
        self._x     = float(x)
        self._y     = float(y)
        self._vx    = 0.0
        self._vy    = 0.0

        self.hp     = BOSS_MAX_HP
        self.max_hp = BOSS_MAX_HP
        self.phase  = BossPhase.PHASE1
        self.active = True
        self.on_ground = False
        self.direction = Direction.LEFT

        self._shoot_timer  = 0.0
        self._move_timer   = 0.0
        self._iframe       = 0.0
        self._shield_timer = 0.0
        self._shield_open  = False

        # limites da arena (definidos por Level ao inicializar)
        self.arena_min_x = x - 300.0
        self.arena_max_x = x + 300.0

        # projéteis próprios
        self.bullets = []     # type: list

    # ==========================================================
    #  Propriedade: escudo ativo?
    # ==========================================================
    @property
    def shielded(self) -> bool:
        if self.phase == BossPhase.PHASE2:
            return False
        return not self._shield_open

    # ==========================================================
    #  Update
    # ==========================================================
    def update(self, dt, player, platforms):  # type: ignore
        if not self.active or self.phase == BossPhase.DEAD:
            return

        if self._iframe > 0:
            self._iframe -= dt

        # ---- Transição para fase 2 ----
        if self.phase == BossPhase.PHASE1 and self.hp <= BOSS_PHASE2_HP:
            self.phase        = BossPhase.PHASE2
            self._shield_open = True

        # ---- Ciclo do escudo ----
        if self.phase == BossPhase.PHASE1:
            self._shield_timer += dt
            if self._shield_timer >= SHIELD_CYCLE:
                self._shield_timer = 0.0
                self._shield_open  = True
            elif self._shield_open and self._shield_timer >= SHIELD_OPEN:
                self._shield_open  = False

        # ---- Movimento (vai-e-vem) ----
        speed = (self._MOVE_SPEED_P2 if self.phase == BossPhase.PHASE2
                 else self._MOVE_SPEED_P1)
        self._move_timer += dt
        if self._move_timer >= 2.0:
            self.direction   = (Direction.RIGHT if self.direction == Direction.LEFT
                                else Direction.LEFT)
            self._move_timer = 0.0
        self._vx = speed * self.direction.value

        # Clamp arena
        if self._x < self.arena_min_x:
            self._x, self._vx = self.arena_min_x, 0.0
            self.direction = Direction.RIGHT
        if self._x + BOSS_W > self.arena_max_x:
            self._x, self._vx = self.arena_max_x - BOSS_W, 0.0
            self.direction = Direction.LEFT

        # ---- Gravidade ----
        self._vy += GRAVITY * dt

        # ---- Integração ----
        self._x += self._vx * dt
        self._y += self._vy * dt
        self.rect.x = int(self._x)
        self.rect.y = int(self._y)

        self._resolve_ground(platforms)

        # ---- Tiro ----
        shoot_delay = (BOSS_SHOOT_DELAY * 0.6 if self.phase == BossPhase.PHASE2
                       else BOSS_SHOOT_DELAY)
        self._shoot_timer += dt
        if self._shoot_timer >= shoot_delay and player.active and not self.shielded:
            self._shoot_timer = 0.0
            if self.phase == BossPhase.PHASE1:
                self._attack_straight(player)
            else:
                self._attack_spread(player)

        # ---- Atualiza projéteis ----
        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.active]

        # ---- Morte ----
        if self.hp <= 0:
            self.hp     = 0
            self.phase  = BossPhase.DEAD
            self.active = False

    def _resolve_ground(self, platforms):  # type: ignore
        self.on_ground = False
        for plat in platforms:
            if not self.rect.colliderect(plat):
                continue
            overlap_t = self.rect.bottom - plat.top
            overlap_b = plat.bottom      - self.rect.top
            if overlap_t < overlap_b and overlap_t < BOSS_H * 0.6:
                self._y = float(plat.top - BOSS_H)
                self._vy = 0.0
                self.on_ground = True
                self.rect.y = int(self._y)

        if self._y + BOSS_H >= SCREEN_HEIGHT:
            self._y       = float(SCREEN_HEIGHT - BOSS_H)
            self._vy      = 0.0
            self.on_ground = True
            self.rect.y   = int(self._y)

    # ==========================================================
    #  Ataques
    # ==========================================================
    def _spawn_bullet(self, vx: float, vy: float) -> None:
        cx = self._x + BOSS_W * 0.5
        cy = self._y + BOSS_H * 0.4
        b  = Projectile(cx, cy, Direction.RIGHT, ProjType.ZERO, from_player=False)
        b._vx = vx
        b._vy = vy
        b.damage = BOSS_DAMAGE
        self.bullets.append(b)

    def _attack_straight(self, player) -> None:
        dx = (player.rect.centerx) - (self.rect.centerx)
        dy = (player.rect.centery) - (self.rect.centery)
        dist = math.hypot(dx, dy) or 1.0
        self._spawn_bullet(dx / dist * BOSS_BULLET_SPEED,
                           dy / dist * BOSS_BULLET_SPEED)

    def _attack_spread(self, player) -> None:
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) or 1.0
        nx, ny = dx / dist, dy / dist
        for angle in (-0.35, 0.0, 0.35):
            ca, sa = math.cos(angle), math.sin(angle)
            self._spawn_bullet(
                (nx * ca - ny * sa) * BOSS_BULLET_SPEED,
                (nx * sa + ny * ca) * BOSS_BULLET_SPEED,
            )

    # ==========================================================
    #  Colisões
    # ==========================================================
    def check_player_bullets(self, bullets):  # type: ignore
        if not self.active or self.shielded:
            return
        for b in bullets:
            if b.active and b.from_player and self.rect.colliderect(b.rect):
                if self._iframe <= 0:
                    self.hp     -= b.damage
                    self._iframe = 0.08
                b.deactivate()

    def check_player_collision(self, player) -> None:
        if not self.active or not player.active:
            return
        if self.rect.colliderect(player.rect):
            player.take_damage(BOSS_DAMAGE)
        for b in self.bullets:
            if b.active and b.rect.colliderect(player.rect):
                player.take_damage(b.damage)
                b.deactivate()

    # ==========================================================
    #  Draw
    # ==========================================================
    def draw(self, surface, offset):  # type: ignore
        if not self.active:
            return
        ox, oy = offset
        x = self.rect.x - ox
        y = self.rect.y - oy
        w, h = BOSS_W, BOSS_H

        # ---- Escudo ----
        if self.phase == BossPhase.PHASE1 and not self._shield_open:
            shield_surf = pygame.Surface((w + 24, h + 24), pygame.SRCALPHA)
            pygame.draw.rect(shield_surf, (80, 140, 255, 140),
                             (0, 0, w + 24, h + 24), border_radius=8)
            pygame.draw.rect(shield_surf, (120, 180, 255, 80),
                             (2, 2, w + 20, h + 20), 3, border_radius=7)
            surface.blit(shield_surf, (x - 12, y - 12))

        # ---- Corpo metálico ----
        pygame.draw.rect(surface, BLACK,          (x,     y,     w,     h))
        pygame.draw.rect(surface, (80, 80, 100),  (x + 2, y + 2, w - 4, h - 4))
        pygame.draw.rect(surface, (40, 40, 60),   (x + 6, y + 6, w - 12, h - 12))

        # ---- Painel de LEDs (4×3) ----
        led_on  = (255, 80, 20)
        led_off = (60, 30, 10)
        total_leds = 12
        lit = int(self.hp / self.max_hp * total_leds)
        for row in range(3):
            for col in range(4):
                color = led_on if (row * 4 + col) < lit else led_off
                pygame.draw.rect(surface, color,
                                 (x + 10 + col * 14, y + 10 + row * 10, 10, 7))

        # ---- Olho central ----
        eye_color = ((200, 50, 255) if self.phase == BossPhase.PHASE2
                     else (255, 40, 40))
        cx = x + w // 2
        cy = y + h // 2 + 8
        pygame.draw.circle(surface, BLACK,      (cx, cy), 12)
        pygame.draw.circle(surface, eye_color,  (cx, cy), 10)
        pygame.draw.circle(surface, WHITE,      (cx, cy),  4)

        # ---- Scan lines (fase 2) ----
        if self.phase == BossPhase.PHASE2:
            scan = pygame.Surface((w, h), pygame.SRCALPHA)
            for row in range(0, h, 6):
                pygame.draw.line(scan, (255, 80, 0, 40), (0, row), (w, row))
            surface.blit(scan, (x, y))

        # ---- Label ----
        try:
            font = pygame.font.SysFont("monospace", 9)
            surface.blit(font.render("CPU-001", True, (200, 200, 255)),
                         (x + 2, y + h - 12))
        except Exception:
            pass

        # ---- Projéteis do boss ----
        for b in self.bullets:
            b.draw(surface, offset)

    def draw_hud(self, surface, font_sm):  # type: ignore
        if not self.active:
            return
        bw = 400
        bh = 20
        bx = (SCREEN_WIDTH - bw) // 2
        by = SCREEN_HEIGHT - 44

        pygame.draw.rect(surface, BLACK,  (bx - 1, by - 1, bw + 2, bh + 2))
        pygame.draw.rect(surface, HP_RED, (bx, by, bw, bh))
        filled = int(bw * (self.hp / self.max_hp))
        bar_color = ((200, 50, 255) if self.phase == BossPhase.PHASE2
                     else (255, 100, 20))
        pygame.draw.rect(surface, bar_color, (bx, by, filled, bh))

        label = "CPU-001  [ESCUDO ATIVO]" if self.shielded else "CPU-001"
        txt   = font_sm.render(label, True, WHITE)
        surface.blit(txt, (bx + bw // 2 - txt.get_width() // 2, by - 20))
