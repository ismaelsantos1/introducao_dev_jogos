# =============================================================
#  CC Tensei — game.py
#  GerenciadorJogo: máquina de estados e loop principal.
#
#  Estados:
#    MENU → PLAYING → DIALOG  (NPC falando)
#                   → QUIZ    (barreira do Boss)
#                   → BOSS_FIGHT
#                   → LEVEL_CLEAR → PLAYING / VICTORY
#    PLAYING        → PAUSED  → PLAYING
#    qualquer       → GAME_OVER → MENU
# =============================================================

import pygame
import sys
from constants import (
    GameState, OOPPillar, QuizState,
    SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS, LEVEL_WIDTH,
    CAM_LERP, PLAYER_W, PLAYER_H, TILE,
    BLACK, WHITE, GRAY, LIGHTGRAY, YELLOW,
)
from player   import Player
from level    import Level
from renderer import (
    CloudSystem, draw_background,
    draw_main_menu, draw_pause, draw_game_over,
    draw_level_clear, draw_victory,
)


# =============================================================
#  Fontes (criadas uma única vez após pygame.init)
# =============================================================
class Fonts:
    def __init__(self):
        self.title = pygame.font.SysFont("monospace", 52, bold=True)
        self.large = pygame.font.SysFont("monospace", 28)
        self.normal= pygame.font.SysFont("monospace", 20)
        self.small = pygame.font.SysFont("monospace", 15)


# =============================================================
#  Câmera simples (lerp horizontal)
# =============================================================
class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, player: Player, dt: float) -> None:
        target_x = player.rect.centerx - SCREEN_WIDTH  // 2
        target_y = player.rect.centery - SCREEN_HEIGHT // 2

        self.x += (target_x - self.x) * CAM_LERP * dt
        self.y += (target_y - self.y) * CAM_LERP * dt

        # Clamp horizontal
        self.x = max(0.0, min(self.x, float(LEVEL_WIDTH - SCREEN_WIDTH)))
        # Ancora vertical no chão
        self.y = max(0.0, min(self.y, 0.0))

    @property
    def offset(self):
        return int(self.x), int(self.y)


# =============================================================
#  Game
# =============================================================
class Game:
    """
    Gerencia o ciclo de jogo completo:
    inicialização → update → draw → limpeza.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen  = screen
        self.clock   = pygame.time.Clock()
        self.fonts   = Fonts()
        self.clouds  = CloudSystem()
        self.running = True

        self._state        = GameState.MENU
        self._level        = Level()
        self._player       = Player(*self._level.player_start)
        self._camera       = Camera()
        self._active_npc   = None   # NPC em diálogo
        self._clear_timer  = 0.0
        self._hint_text    = ""
        self._hint_timer   = 0.0
        self._current_lvl_idx = 0

    # ==========================================================
    #  Loop público
    # ==========================================================
    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            dt = min(dt, 0.05)   # cap para evitar saltos em lag

            self._handle_events()
            self._update(dt)
            self._draw()

    # ==========================================================
    #  Eventos
    # ==========================================================
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Fecha com Alt+F4 / botão X
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_ALT:
                    self.running = False
                    return

            self._dispatch_event(event)

    def _dispatch_event(self, event: pygame.event.Event) -> None:
        s = self._state

        if s == GameState.MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._start_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

        elif s == GameState.PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._state = GameState.PLAYING
                elif event.key == pygame.K_m:
                    self._state = GameState.MENU

        elif s == GameState.GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._restart()
                elif event.key == pygame.K_ESCAPE:
                    self._state = GameState.MENU

        elif s == GameState.VICTORY:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._state = GameState.MENU

        elif s == GameState.LEVEL_CLEAR:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._next_level()

        elif s == GameState.DIALOG:
            if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_e, pygame.K_s, pygame.K_RETURN, pygame.K_SPACE):
                if self._active_npc:
                    more = self._active_npc.advance()
                    if not more:
                        self._active_npc = None
                        self._state = GameState.PLAYING

        elif s == GameState.QUIZ:
            lvl = self._level
            lvl.quiz.handle_event(event)
            if lvl.quiz.state == QuizState.PASSED:
                if event.type == pygame.KEYDOWN and event.key in (
                        pygame.K_RETURN, pygame.K_SPACE):
                    lvl.quiz_passed = True
                    self._state = GameState.BOSS_FIGHT
            elif lvl.quiz.state == QuizState.FAILED:
                if event.type == pygame.KEYDOWN and event.key in (
                        pygame.K_RETURN, pygame.K_SPACE):
                    lvl.quiz.reset()
                    self._state = GameState.PLAYING

        elif s == GameState.PLAYING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._state = GameState.PAUSED

        elif s == GameState.BOSS_FIGHT:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._state = GameState.PAUSED

    # ==========================================================
    #  Update
    # ==========================================================
    def _update(self, dt: float) -> None:
        self.clouds.update(dt)

        s   = self._state
        lvl = self._level
        p   = self._player

        if s in (GameState.MENU, GameState.PAUSED,
                 GameState.GAME_OVER, GameState.VICTORY):
            return

        if s == GameState.LEVEL_CLEAR:
            self._clear_timer -= dt
            if self._clear_timer <= 0:
                self._next_level()
            return

        if s == GameState.DIALOG:
            return   # player congelado durante diálogo

        if s in (GameState.PLAYING, GameState.BOSS_FIGHT):
            # ---- Player ----
            p.update(dt, lvl.platforms)
            self._camera.update(p, dt)

            if not p.active:
                self._state = GameState.GAME_OVER
                return

            # ---- Dica de terminal ----
            if self._hint_timer > 0:
                self._hint_timer -= dt

            # ---- Lógica exclusiva de PLAYING ----
            if s == GameState.PLAYING:
                # Inimigos
                for e in lvl.enemies:
                    e.update(dt, lvl.platforms)
                    e.check_player_collision(p)
                    for b in p.bullets:
                        if b.active and b.from_player and e.active:
                            if e.rect.colliderect(b.rect):
                                e.take_damage(b.damage)
                                b.deactivate()

                # Terminais
                hint = lvl.check_terminal_interaction(p)
                if hint:
                    self._hint_text  = hint
                    self._hint_timer = 3.5

                # NPCs
                keys = pygame.key.get_pressed()
                for npc in lvl.npcs:
                    if npc.near_player(p) and (keys[pygame.K_e] or keys[pygame.K_s]):
                        npc.reset()
                        self._active_npc = npc
                        self._state = GameState.DIALOG
                        break

                # Porta do Boss
                if lvl.player_at_boss_door(p):
                    if not lvl.quiz_passed:
                        lvl.quiz.start()
                        self._state = GameState.QUIZ
                    else:
                        self._state = GameState.BOSS_FIGHT

            # ---- Lógica exclusiva de BOSS_FIGHT ----
            elif s == GameState.BOSS_FIGHT:
                lvl.boss.update(dt, p, lvl.platforms)
                lvl.boss.check_player_bullets(p.bullets)
                lvl.boss.check_player_collision(p)

                if not p.active:
                    self._state = GameState.GAME_OVER

                if not lvl.boss.active:
                    lvl.boss_defeated = True
                    self._clear_timer = 3.0
                    self._state = GameState.LEVEL_CLEAR

    # ==========================================================
    #  Draw
    # ==========================================================
    def _draw(self) -> None:
        s = self._state

        if s == GameState.MENU:
            draw_main_menu(self.screen, self.fonts.title,
                           self.fonts.large, self.fonts.small)
            pygame.display.flip()
            return

        if s == GameState.GAME_OVER:
            draw_game_over(self.screen, self.fonts.title,
                           self.fonts.normal, self.fonts.small)
            pygame.display.flip()
            return

        if s == GameState.VICTORY:
            draw_victory(self.screen, self.fonts.title,
                         self.fonts.large, self.fonts.normal)
            pygame.display.flip()
            return

        # ---- Fundo ----
        draw_background(self.screen)
        self.clouds.draw(self.screen, self._camera.x)

        lvl    = self._level
        p      = self._player
        offset = self._camera.offset

        # ---- Fase (plataformas, terminais, porta) ----
        lvl.draw(self.screen, offset, self.fonts.small)

        # ---- NPCs ----
        for npc in lvl.npcs:
            npc.draw(self.screen, offset)
            npc.draw_indicator(self.screen, offset, p, self.fonts.small)

        # ---- Inimigos ----
        for e in lvl.enemies:
            e.draw(self.screen, offset)

        # ---- Boss ----
        if s == GameState.BOSS_FIGHT or lvl.boss.active:
            lvl.boss.draw(self.screen, offset)

        # ---- Player ----
        p.draw(self.screen, offset)

        # ---- HUD ----
        p.draw_hud(self.screen, self.fonts.small)

        if s == GameState.BOSS_FIGHT:
            lvl.boss.draw_hud(self.screen, self.fonts.small)

        # Label da fase
        lbl_names = ["Encapsulamento", "Heranca", "Polimorfismo", "Abstracao"]
        lbl = self.fonts.small.render(
            f"Fase {self._current_lvl_idx + 1}: {lbl_names[self._current_lvl_idx]}",
            True, WHITE)
        self.screen.blit(lbl, (SCREEN_WIDTH - lbl.get_width() - 12, 12))

        # Dica de terminal
        if self._hint_timer > 0:
            alpha = min(self._hint_timer, 1.0)
            hint_surf = pygame.Surface((SCREEN_WIDTH - 80, 44), pygame.SRCALPHA)
            hint_surf.fill((0, 30, 10, int(alpha * 210)))
            htxt = self.fonts.small.render(self._hint_text[:72], True,
                                           (100, 255, 140))
            hint_surf.blit(htxt, (8, 12))
            self.screen.blit(hint_surf, (40, SCREEN_HEIGHT - 106))

        # Diálogo do NPC
        if s == GameState.DIALOG and self._active_npc:
            self._active_npc.draw_dialog(
                self.screen, self.fonts.normal, self.fonts.small)

        # Quiz
        if s == GameState.QUIZ:
            lvl.quiz.draw(self.screen, self.fonts.large,
                          self.fonts.normal, self.fonts.small)

        # Telas de sobreposição
        if s == GameState.PAUSED:
            draw_pause(self.screen, self.fonts.title, self.fonts.normal)

        if s == GameState.LEVEL_CLEAR:
            draw_level_clear(self.screen, self._current_lvl_idx,
                             self.fonts.title, self.fonts.large, self.fonts.normal)

        # FPS
        fps_txt = self.fonts.small.render(
            f"FPS: {int(self.clock.get_fps())}", True, GRAY)
        self.screen.blit(fps_txt, (SCREEN_WIDTH - fps_txt.get_width() - 12,
                                    SCREEN_HEIGHT - 22))

        pygame.display.flip()

    # ==========================================================
    #  Helpers de transição de estado
    # ==========================================================
    def _start_game(self) -> None:
        self._current_lvl_idx = 0
        self._level   = Level()
        self._player  = Player(*self._level.player_start)
        self._camera  = Camera()
        self._active_npc  = None
        self._hint_timer  = 0.0
        self._state = GameState.PLAYING

    def _restart(self) -> None:
        self._level.reset()
        self._player = Player(*self._level.player_start)
        self._camera = Camera()
        self._active_npc = None
        self._hint_timer = 0.0
        self._state = GameState.PLAYING

    def _next_level(self) -> None:
        self._current_lvl_idx += 1
        if self._current_lvl_idx >= 4:
            self._state = GameState.VICTORY
            return
        # Fases 2-4: reutiliza a mesma estrutura de nível
        # (num projeto completo, cada fase teria seu próprio Level)
        self._level  = Level()
        self._player = Player(*self._level.player_start)
        self._camera = Camera()
        self._active_npc = None
        self._state = GameState.PLAYING
