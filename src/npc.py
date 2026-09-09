# =============================================================
#  CC Tensei — npc.py
#  Professores da fase: ensinam os pilares da POO via diálogo.
# =============================================================

import pygame
import math
from constants import (
    OOPPillar, NPC_W, NPC_H, NPC_INTERACT_R,
    BLACK, WHITE, YELLOW, DARKGRAY, LIGHTGRAY, GRAY,
    NPC_COL, DIALOG_BG, SCREEN_WIDTH, SCREEN_HEIGHT,
)

# =============================================================
#  Conteúdo educativo
# =============================================================
_DIALOGS = {
    OOPPillar.ENCAPSULAMENTO: [
        "Ola, estudante! Eu sou o Prof. Capse.",
        "Encapsulamento e um dos pilares da POO.",
        "A ideia e PROTEGER os dados internos de um objeto.",
        "Imagine uma capsula: o que esta dentro nao",
        "pode ser acessado diretamente de fora.",
        "Usamos 'private' para esconder atributos",
        "e 'public' para expor apenas o necessario.",
        "Exemplo: ContaBancaria tem saldo privado.",
        "Voce nao acessa 'conta.saldo' diretamente.",
        "Use 'conta.get_saldo()' — um getter!",
        "Lembre: encapsulamento = protecao + controle.",
        "[Pressione E para continuar]",
    ],
    OOPPillar.HERANCA: [
        "Ola! Sou o Prof. Heri.",
        "Heranca permite que uma classe REUTILIZE codigo.",
        "Uma classe filha herda atributos e metodos da mae.",
        "Exemplo: 'Animal' tem metodo mover().",
        "'Cachorro' herda de Animal e adiciona latir().",
        "Cachorro nao precisa reimplementar mover().",
        "Em Python: class Cachorro(Animal): ...",
        "Isso evita repeticao — principio DRY.",
        "Lembre: heranca = reuso + hierarquia.",
        "[Pressione E para continuar]",
    ],
    OOPPillar.POLIMORFISMO: [
        "Oi! Sou a Prof. Poly.",
        "Polimorfismo significa 'muitas formas'.",
        "O mesmo metodo pode se comportar diferente",
        "dependendo do objeto que o chama.",
        "Exemplo: Animal tem metodo falar().",
        "Cachorro.falar() retorna 'Au!'",
        "Gato.falar()     retorna 'Miau!'",
        "Mesmo nome — comportamentos distintos!",
        "Em Python usamos sobrescrita de metodos (override).",
        "Lembre: polimorfismo = mesma interface, formas distintas.",
        "[Pressione E para continuar]",
    ],
    OOPPillar.ABSTRACAO: [
        "Bem-vindo! Sou o Prof. Abs.",
        "Abstracao e sobre mostrar apenas o ESSENCIAL.",
        "Ocultar a complexidade interna de um sistema.",
        "Ao usar um controle remoto, nao precisa saber",
        "como a TV funciona por dentro.",
        "Em POO, classes abstratas definem contratos.",
        "Exemplo: classe abstrata 'Forma' com area().",
        "'Circulo' e 'Quadrado' implementam area() distintos.",
        "Quem usa 'Forma' nao sabe qual e qual.",
        "Lembre: abstracao = esconder detalhes, expor interface.",
        "[Pressione E para continuar]",
    ],
}

_NAMES = {
    OOPPillar.ENCAPSULAMENTO: "Prof. Capse",
    OOPPillar.HERANCA:        "Prof. Heri",
    OOPPillar.POLIMORFISMO:   "Prof. Poly",
    OOPPillar.ABSTRACAO:      "Prof. Abs",
}

_SYMBOLS = {
    OOPPillar.ENCAPSULAMENTO: "{}",
    OOPPillar.HERANCA:        "->",
    OOPPillar.POLIMORFISMO:   "()",
    OOPPillar.ABSTRACAO:      "<>",
}


# =============================================================
#  Classe NPC
# =============================================================
class NPC:
    """
    Professor da fase.  Ensina um pilar da POO via caixa de diálogo.
    Após a última linha, `talked` fica True.
    """

    def __init__(self, x: float, y: float, pillar: OOPPillar):
        self.rect    = pygame.Rect(x, y, NPC_W, NPC_H)
        self.pillar  = pillar
        self.active  = True
        self.talked  = False
        self._lines  = _DIALOGS[pillar]
        self._cur    = 0

    # ----------------------------------------------------------
    @property
    def current_line(self) -> str:
        return self._lines[self._cur]

    @property
    def progress(self):
        return self._cur + 1, len(self._lines)

    @property
    def name(self):
        return _NAMES[self.pillar]

    def near_player(self, player):  # type: ignore
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return math.hypot(dx, dy) <= NPC_INTERACT_R

    def advance(self):
        """Avança linha; retorna False quando acabou."""
        self._cur += 1
        if self._cur >= len(self._lines):
            self._cur   = len(self._lines) - 1
            self.talked = True
            return False
        return True

    def reset(self):
        self._cur   = 0
        self.talked = False

    # ----------------------------------------------------------
    def draw(self, surface, offset):  # type: ignore
        if not self.active:
            return
        ox, oy = offset
        x = self.rect.x - ox
        y = self.rect.y - oy

        body_col = (40, 160, 100) if self.talked else NPC_COL

        pygame.draw.rect(surface, DARKGRAY, (x, y, NPC_W, NPC_H))
        pygame.draw.rect(surface, body_col,  (x + 1, y + 1, NPC_W - 2, NPC_H - 2))

        # Cabeça
        pygame.draw.rect(surface, BLACK,          (x + 4, y, NPC_W - 8, 14))
        pygame.draw.rect(surface, (60, 220, 160), (x + 5, y + 1, NPC_W - 10, 12))

        # Olhos LED
        eye_c = LIGHTGRAY if self.talked else WHITE
        pygame.draw.rect(surface, eye_c, (x + 6,           y + 4, 5, 5))
        pygame.draw.rect(surface, eye_c, (x + NPC_W - 11,  y + 4, 5, 5))

        # Chapéu de formatura
        pygame.draw.rect(surface, (20, 20, 60), (x + 3, y - 5, NPC_W - 6, 5))
        pygame.draw.rect(surface, YELLOW,       (x + NPC_W // 2 - 2, y - 9, 4, 4))

        # Símbolo do pilar
        try:
            font = pygame.font.SysFont("monospace", 10)
            sym  = font.render(_SYMBOLS[self.pillar], True, (200, 255, 200))
            surface.blit(sym, (x + 4, y + 16))
        except Exception:
            pass

        # Pernas
        pygame.draw.rect(surface, BLACK, (x + 4,           y + NPC_H - 10, 8, 10))
        pygame.draw.rect(surface, BLACK, (x + NPC_W - 12,  y + NPC_H - 10, 8, 10))

    def draw_indicator(self, surface, offset, player, font_sm):  # type: ignore
        """'!' pulsante quando o player está próximo e não falou ainda."""
        if not self.active or self.talked:
            return
        if not self.near_player(player):
            return
        ox, oy = offset
        x = self.rect.x - ox
        y = self.rect.y - oy
        pulse = abs(math.sin(pygame.time.get_ticks() / 250)) * 4
        surface.blit(font_sm.render("!", True, YELLOW),
                     (x + NPC_W // 2 - 4, y - 22 - pulse))
        surface.blit(font_sm.render("[E] Falar", True, WHITE),
                     (x - 8, y - 36 - pulse))

    def draw_dialog(self, surface, font_nm, font_sm):  # type: ignore
        """Caixa de diálogo fixa no rodapé da tela."""
        bx, by = 60, SCREEN_HEIGHT - 180
        bw, bh = SCREEN_WIDTH - 120, 160

        pygame.draw.rect(surface, WHITE,      (bx - 2, by - 2, bw + 4, bh + 4))
        pygame.draw.rect(surface, DIALOG_BG,  (bx, by, bw, bh))

        # Nome do NPC
        surface.blit(font_nm.render(self.name, True, NPC_COL), (bx + 10, by + 8))

        # Linha atual
        surface.blit(font_nm.render(self._lines[self._cur], True, WHITE),
                     (bx + 10, by + 36))

        # Progresso
        cur, total = self.progress
        surface.blit(font_sm.render(f"{cur}/{total}", True, GRAY),
                     (bx + bw - 50, by + bh - 22))

        # Instrução
        surface.blit(font_sm.render("[E] Continuar", True, LIGHTGRAY),
                     (bx + 10, by + bh - 22))
