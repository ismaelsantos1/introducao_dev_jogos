# =============================================================
#  CC Tensei — player.py
#  Protagonista: estudante de CC com teclado mecânico.
#  Movimentação clássica de plataforma + disparo binário.
# =============================================================

import pygame
from constants import (
    Direction, ProjType,
    PLAYER_W, PLAYER_H, PLAYER_MAX_HP,
    PLAYER_SPEED, PLAYER_JUMP_FORCE, GRAVITY,
    PLAYER_SHOOT_DELAY, PLAYER_IFRAME_TIME, PLAYER_CHARGE_TIME,
    SCREEN_HEIGHT, LEVEL_WIDTH,
    PLAYER_COL, BLACK, WHITE, HP_GREEN, HP_RED, YELLOW, PURPLE,
    BAR_W, BAR_H, HUD_MARGIN,
)
from projectile import Projectile


class Player:
    """
    Jogador controlado pelo teclado/mouse.

    Controles
    ---------
    A / D          : mover esquerda / direita
    W ou ESPAÇO    : pular
    CLIQUE ESQ     : atirar "0" (rápido)
    CLIQUE DIR     : segurar para carregar; soltar para atirar "1"
    E / S          : interagir com NPC / terminal
    """

    def __init__(self, x: float, y: float):
        self.rect    = pygame.Rect(x, y, PLAYER_W, PLAYER_H)
        self._x      = float(x)
        self._y      = float(y)
        self._vx     = 0.0
        self._vy     = 0.0

        self.hp              = PLAYER_MAX_HP
        self.max_hp          = PLAYER_MAX_HP
        self.direction       = Direction.RIGHT
        self.on_ground       = False
        self.active          = True

        self._shoot_cd       = 0.0
        self._iframe         = 0.0
        self._charging       = False
        self._charge_timer   = 0.0
        self.terminals_hacked = 0

        # lista externa de projéteis — preenchida por shoot()
        self.bullets = []     # type: list

    # ==========================================================
    #  Update
    # ==========================================================
    def update(self, dt, platforms):  # type: ignore
        if not self.active:
            return

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        # --- Timers ---
        if self._shoot_cd > 0:
            self._shoot_cd -= dt
        if self._iframe > 0:
            self._iframe -= dt

        # --- Horizontal ---
        self._vx = 0.0
        if keys[pygame.K_a]:
            self._vx = -PLAYER_SPEED
            self.direction = Direction.LEFT
        if keys[pygame.K_d]:
            self._vx = PLAYER_SPEED
            self.direction = Direction.RIGHT

        # --- Pulo ---
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self._vy     = PLAYER_JUMP_FORCE
            self.on_ground = False

        # --- Carga do tiro "1" ---
        if mouse[2]:                       # botão direito pressionado
            self._charging = True
            self._charge_timer += dt
        else:
            if self._charging:             # acabou de soltar
                self._try_shoot_one()
            self._charging     = False
            self._charge_timer = 0.0

        # --- Tiro "0" ---
        if mouse[0] and self._shoot_cd <= 0:
            self._spawn_bullet(ProjType.ZERO)
            self._shoot_cd = PLAYER_SHOOT_DELAY

        # --- Gravidade ---
        self._vy += GRAVITY * dt

        # --- Integração ---
        self._x += self._vx * dt
        self._y += self._vy * dt

        self.rect.x = int(self._x)
        self.rect.y = int(self._y)

        # --- Colisão com plataformas ---
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                self._resolve_collision(plat)

        # --- Limites do mundo ---
        if self._x < 0:
            self._x = 0.0
            self.rect.x = 0
        if self._x + PLAYER_W > LEVEL_WIDTH:
            self._x = float(LEVEL_WIDTH - PLAYER_W)
            self.rect.x = LEVEL_WIDTH - PLAYER_W
        if self._y + PLAYER_H >= SCREEN_HEIGHT:
            self._y      = float(SCREEN_HEIGHT - PLAYER_H)
            self._vy     = 0.0
            self.on_ground = True
            self.rect.y  = int(self._y)

        # Atualiza projéteis
        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.active]

    def _resolve_collision(self, plat: pygame.Rect) -> None:
        """AABB: empurra o player para fora do menor eixo."""
        overlap_l = (self.rect.right)  - plat.left
        overlap_r = plat.right         - self.rect.left
        overlap_t = (self.rect.bottom) - plat.top
        overlap_b = plat.bottom        - self.rect.top

        min_x = min(overlap_l, overlap_r)
        min_y = min(overlap_t, overlap_b)

        if min_x < min_y:
            if overlap_l < overlap_r:
                self._x -= overlap_l
                self._vx  = 0.0
            else:
                self._x += overlap_r
                self._vx  = 0.0
        else:
            if overlap_t < overlap_b:
                # cabeça no teto
                self._y -= overlap_t
                self._vy  = 0.0
            else:
                # pousa no chão
                self._y   = float(plat.top - PLAYER_H)
                self._vy  = 0.0
                self.on_ground = True

        self.rect.x = int(self._x)
        self.rect.y = int(self._y)

    # ==========================================================
    #  Disparo
    # ==========================================================
    def _spawn_bullet(self, proj_type: ProjType) -> None:
        if self.direction == Direction.RIGHT:
            bx = self.rect.right
        else:
            bx = self.rect.left
        by = self.rect.top + PLAYER_H * 0.45
        self.bullets.append(Projectile(bx, by, self.direction, proj_type, True))
        self._shoot_cd = PLAYER_SHOOT_DELAY

    def _try_shoot_one(self) -> None:
        if self._charge_timer >= PLAYER_CHARGE_TIME and self._shoot_cd <= 0:
            self._spawn_bullet(ProjType.ONE)
        self._charge_timer = 0.0

    # ==========================================================
    #  Dano
    # ==========================================================
    def take_damage(self, amount: int) -> None:
        if not self.active or self._iframe > 0:
            return
        self.hp -= amount
        self._iframe = PLAYER_IFRAME_TIME
        if self.hp <= 0:
            self.hp     = 0
            self.active = False

    # ==========================================================
    #  Draw
    # ==========================================================
    def draw(self, surface, offset):  # type: ignore
        if not self.active:
            return
        # Pisca durante iframes
        if self._iframe > 0 and int(self._iframe * 10) % 2 == 0:
            return

        ox, oy = offset
        x = self.rect.x - ox
        y = self.rect.y - oy

        # --- Corpo (casaco azul escuro) ---
        pygame.draw.rect(surface, (30, 60, 160),
                         (x, y + 14, PLAYER_W, PLAYER_H - 14))

        # --- Cabeça ---
        pygame.draw.rect(surface, (240, 200, 160),
                         (x + 4, y, PLAYER_W - 8, 14))

        # --- Cabelo ---
        pygame.draw.rect(surface, (80, 45, 20),
                         (x + 4, y, PLAYER_W - 8, 5))

        # --- Olho ---
        eye_x = x + 10 if self.direction == Direction.RIGHT else x + 4
        pygame.draw.rect(surface, (20, 20, 80), (eye_x, y + 7, 4, 3))

        # --- Teclado mecânico (arma) ---
        kb_x = x + PLAYER_W - 2 if self.direction == Direction.RIGHT else x - 10
        pygame.draw.rect(surface, (140, 140, 160), (kb_x, y + 18, 12, 7))
        for k in range(3):
            pygame.draw.rect(surface, (210, 210, 230),
                             (kb_x + 1 + k * 4, y + 20, 3, 3))

        # --- Pernas ---
        pygame.draw.rect(surface, (20, 40, 120),
                         (x + 4, y + PLAYER_H - 12, 8, 12))
        pygame.draw.rect(surface, (20, 40, 120),
                         (x + 16, y + PLAYER_H - 12, 8, 12))

        # --- Aura de carga do tiro "1" ---
        if self._charging and self._charge_timer > 0:
            ratio  = min(self._charge_timer / PLAYER_CHARGE_TIME, 1.0)
            radius = int(6 + ratio * 12)
            alpha  = int(80 + ratio * 160)
            aura_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (200, 80, 255, alpha),
                               (radius, radius), radius)
            cx = x + PLAYER_W // 2 - radius
            cy = y + PLAYER_H // 2 - radius
            surface.blit(aura_surf, (cx, cy))

        # --- Projéteis ---
        for b in self.bullets:
            b.draw(surface, offset)

    def draw_hud(self, surface, font_sm):  # type: ignore
        # Barra de HP
        bx, by = HUD_MARGIN, HUD_MARGIN
        pygame.draw.rect(surface, BLACK,   (bx - 1, by - 1, BAR_W + 2, BAR_H + 2))
        pygame.draw.rect(surface, HP_RED,  (bx, by, BAR_W, BAR_H))
        filled = int(BAR_W * (self.hp / self.max_hp))
        pygame.draw.rect(surface, HP_GREEN, (bx, by, filled, BAR_H))
        surface.blit(font_sm.render("HP", True, WHITE), (bx + BAR_W + 6, by))

        # Barra de carga
        if self._charging:
            ratio  = min(self._charge_timer / PLAYER_CHARGE_TIME, 1.0)
            cy     = by + BAR_H + 6
            pygame.draw.rect(surface, BLACK, (bx - 1, cy - 1, BAR_W + 2, BAR_H + 2))
            c_filled = int(BAR_W * ratio)
            pygame.draw.rect(surface, (200, 80, 255), (bx, cy, c_filled, BAR_H))
            label = "[1] PRONTO!" if ratio >= 1.0 else "Carregando..."
            color = (200, 80, 255) if ratio >= 1.0 else (160, 60, 200)
            surface.blit(font_sm.render(label, True, color),
                         (bx, cy + BAR_H + 4))

        # Terminais hackeados
        txt = font_sm.render(f"Terminais: {self.terminals_hacked}", True, (200, 200, 200))
        surface.blit(txt, (HUD_MARGIN, by + 60))
