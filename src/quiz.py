# =============================================================
#  CC Tensei — quiz.py
#  Barreira de acesso à sala do Boss.
#  Múltipla escolha, banco de perguntas por pilar.
# =============================================================

import pygame
import random
from dataclasses import dataclass
from constants import (
    OOPPillar, QuizState, QUESTIONS_PER_GATE,
    BLACK, WHITE, YELLOW, GREEN, RED, GRAY, DARKGRAY, LIGHTGRAY,
    SCREEN_WIDTH, SCREEN_HEIGHT,
)


# =============================================================
#  Modelo de dados
# =============================================================
@dataclass
class Question:
    text:          str
    options:       list      # sempre 4 opções
    correct_index: int       # 0-3
    pillar:        OOPPillar


# =============================================================
#  Banco de perguntas
# =============================================================
_BANK = {
    OOPPillar.ENCAPSULAMENTO: [
        Question(
            "O que e Encapsulamento?",
            ["Esconder estado interno e expor operacoes necessarias.",
             "Fazer todas as variaveis serem publicas.",
             "Copiar atributos de outra classe.",
             "Criar metodos com o mesmo nome."],
            0, OOPPillar.ENCAPSULAMENTO,
        ),
        Question(
            "Qual modificador deixa um atributo inacessivel fora da classe?",
            ["private", "public", "static", "global"],
            0, OOPPillar.ENCAPSULAMENTO,
        ),
        Question(
            "Forma correta de acessar 'saldo' privado de ContaBancaria:",
            ["conta.get_saldo()", "conta.saldo", "print(saldo)", "saldo()"],
            0, OOPPillar.ENCAPSULAMENTO,
        ),
        Question(
            "O que e um getter?",
            ["Metodo publico que retorna um atributo privado.",
             "Um construtor especial.",
             "Substitui o atributo privado.",
             "Usado para deletar objetos."],
            0, OOPPillar.ENCAPSULAMENTO,
        ),
        Question(
            "Principal beneficio do Encapsulamento:",
            ["Controle de acesso e protecao dos dados internos.",
             "Herdar metodos de outras classes.",
             "Criar multiplas instancias.",
             "Definir interfaces abstratas."],
            0, OOPPillar.ENCAPSULAMENTO,
        ),
        Question(
            "O que e um setter?",
            ["Metodo publico que modifica atributo privado com validacao.",
             "Metodo que imprime o objeto.",
             "Construtor sem parametros.",
             "Metodo estatico global."],
            0, OOPPillar.ENCAPSULAMENTO,
        ),
    ],
    OOPPillar.HERANCA: [
        Question(
            "O que e Heranca em POO?",
            ["Uma classe reutiliza atributos e metodos de outra.",
             "Uma classe copia fisicamente o codigo de outra.",
             "Duas classes compartilham o mesmo nome.",
             "Uma funcao chama outra funcao."],
            0, OOPPillar.HERANCA,
        ),
        Question(
            "A classe da qual se herda e chamada de:",
            ["Classe mae (ou base)", "Classe filha", "Interface", "Modulo"],
            0, OOPPillar.HERANCA,
        ),
        Question(
            "Exemplo correto de heranca:",
            ["Cachorro herda de Animal e adiciona latir().",
             "Cachorro copia todo o codigo de Animal.",
             "Animal herda de Cachorro.",
             "Cachorro e Animal sao a mesma classe."],
            0, OOPPillar.HERANCA,
        ),
        Question(
            "Em Python, como declarar que Filho herda de Pai?",
            ["class Filho(Pai):", "class Filho = Pai:",
             "class Filho -> Pai:", "inherit Filho from Pai:"],
            0, OOPPillar.HERANCA,
        ),
        Question(
            "Principal vantagem da heranca:",
            ["Reutilizacao de codigo e reducao de repeticao.",
             "Aumentar o numero de classes.",
             "Tornar todos os metodos privados.",
             "Eliminar construtores."],
            0, OOPPillar.HERANCA,
        ),
    ],
    OOPPillar.POLIMORFISMO: [
        Question(
            "O que e Polimorfismo?",
            ["O mesmo metodo tem comportamentos diferentes por objeto.",
             "Dois metodos com nomes diferentes fazem a mesma coisa.",
             "Uma classe tem dois construtores.",
             "Um objeto muda de tipo em tempo de execucao."],
            0, OOPPillar.POLIMORFISMO,
        ),
        Question(
            "Exemplo correto de polimorfismo:",
            ["Cachorro.falar()->'Au!'  Gato.falar()->'Miau!'",
             "Cachorro e Gato tem o mesmo comportamento.",
             "falar() e definido apenas em Cachorro.",
             "Gato nao pode chamar falar()."],
            0, OOPPillar.POLIMORFISMO,
        ),
        Question(
            "Como implementar polimorfismo de subtipos em Python?",
            ["Sobrescrever (override) o metodo na classe filha.",
             "Renomear o metodo na classe filha.",
             "Copiar o metodo da mae sem alteracao.",
             "Tornar o metodo privado."],
            0, OOPPillar.POLIMORFISMO,
        ),
        Question(
            "Beneficio do polimorfismo:",
            ["Tratar objetos de subclasses de forma uniforme.",
             "Obrigar todas as classes a ter o mesmo numero de metodos.",
             "Eliminar a necessidade de heranca.",
             "Criar copias identicas de objetos."],
            0, OOPPillar.POLIMORFISMO,
        ),
    ],
    OOPPillar.ABSTRACAO: [
        Question(
            "O que e Abstracao em POO?",
            ["Mostrar apenas o essencial e ocultar a complexidade.",
             "Copiar o comportamento de outra classe.",
             "Tornar todos os atributos publicos.",
             "Criar metodos com multiplos parametros."],
            0, OOPPillar.ABSTRACAO,
        ),
        Question(
            "O que e uma classe abstrata?",
            ["Define um contrato mas nao pode ser instanciada.",
             "Uma classe sem atributos.",
             "Uma classe com todos os metodos publicos.",
             "Uma classe que herda de si mesma."],
            0, OOPPillar.ABSTRACAO,
        ),
        Question(
            "Exemplo correto de abstracao:",
            ["Forma abstrata com area(); Circulo e Quadrado implementam.",
             "Forma herda de Circulo e Quadrado.",
             "area() e definido apenas em Forma.",
             "Circulo e Quadrado nao precisam de area()."],
            0, OOPPillar.ABSTRACAO,
        ),
        Question(
            "Em Python, como criar uma classe abstrata?",
            ["Herdar de ABC e usar @abstractmethod.",
             "Usar a palavra abstract antes do class.",
             "Deixar todos os metodos vazios.",
             "Usar @staticmethod em todos os metodos."],
            0, OOPPillar.ABSTRACAO,
        ),
        Question(
            "Principal objetivo da abstracao:",
            ["Separar a interface da implementacao.",
             "Aumentar o numero de parametros.",
             "Eliminar o uso de heranca.",
             "Tornar todos os objetos globais."],
            0, OOPPillar.ABSTRACAO,
        ),
    ],
}


# =============================================================
#  Classe Quiz
# =============================================================
class Quiz:
    """
    Barreira de acesso à sala do Boss.
    Sorteia QUESTIONS_PER_GATE perguntas do banco do pilar.
    O jogador precisa acertar TODAS para passar.
    """

    def __init__(self, pillar: OOPPillar):
        self.pillar    = pillar
        self.state     = QuizState.WAITING
        self._pool = []       # type: list
        self._active = []     # type: list
        self._cur_idx        = 0
        self._correct        = 0
        self._selected       = -1
        self._feedback_timer = 0.0
        self._last_correct   = False
        self._load()

    def _load(self):
        self._pool = list(_BANK[self.pillar])

    def start(self) -> None:
        sample = random.sample(self._pool,
                               min(QUESTIONS_PER_GATE, len(self._pool)))
        self._active         = sample
        self._cur_idx        = 0
        self._correct        = 0
        self._selected       = -1
        self._feedback_timer = 0.0
        self.state           = QuizState.ACTIVE

    def reset(self) -> None:
        self._load()
        self.start()

    # ----------------------------------------------------------
    @property
    def current_question(self):
        if self._cur_idx < len(self._active):
            return self._active[self._cur_idx]
        return None

    # ----------------------------------------------------------
    def handle_event(self, event):  # type: ignore
        if self.state != QuizState.ACTIVE:
            return
        if self._feedback_timer > 0:
            return

        pressed = -1

        if event.type == pygame.KEYDOWN:
            key_map = {
                pygame.K_1: 0, pygame.K_KP1: 0,
                pygame.K_2: 1, pygame.K_KP2: 1,
                pygame.K_3: 2, pygame.K_KP3: 2,
                pygame.K_4: 3, pygame.K_KP4: 3,
            }
            pressed = key_map.get(event.key, -1)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i in range(4):
                box = self._option_rect(i)
                if box.collidepoint(mx, my):
                    pressed = i
                    break

        if pressed >= 0:
            self._select(pressed)

    def _select(self, idx: int) -> None:
        q = self.current_question
        if q is None:
            return
        self._selected       = idx
        self._last_correct   = (idx == q.correct_index)
        if self._last_correct:
            self._correct += 1
        self._feedback_timer = 1.4

    def update(self, dt):  # type: ignore
        if self.state != QuizState.ACTIVE:
            return self.state
        if self._feedback_timer > 0:
            self._feedback_timer -= dt
            if self._feedback_timer <= 0:
                self._advance()
        return self.state

    def _advance(self) -> None:
        self._cur_idx += 1
        self._selected = -1
        if self._cur_idx >= len(self._active):
            self.state = (QuizState.PASSED
                          if self._correct == len(self._active)
                          else QuizState.FAILED)

    # ----------------------------------------------------------
    @staticmethod
    def _option_rect(i: int) -> pygame.Rect:
        return pygame.Rect(SCREEN_WIDTH // 2 - 300, 260 + i * 82, 600, 66)

    # ----------------------------------------------------------
    def draw(self, surface, font_lg, font_nm, font_sm):  # type: ignore

        if self.state == QuizState.WAITING:
            return

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        pillar_names = {
            OOPPillar.ENCAPSULAMENTO: "Encapsulamento",
            OOPPillar.HERANCA:        "Heranca",
            OOPPillar.POLIMORFISMO:   "Polimorfismo",
            OOPPillar.ABSTRACAO:      "Abstracao",
        }
        title = f"== BARREIRA: {pillar_names[self.pillar]} =="
        tw = font_lg.render(title, True, YELLOW)
        surface.blit(tw, (SCREEN_WIDTH // 2 - tw.get_width() // 2, 28))

        if self.state == QuizState.PASSED:
            msg = font_lg.render("CORRETO! Porta desbloqueada!", True, GREEN)
            surface.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2,
                                SCREEN_HEIGHT // 2 - 20))
            hint = font_nm.render("[ENTER] Continuar", True, LIGHTGRAY)
            surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                 SCREEN_HEIGHT // 2 + 40))
            return

        if self.state == QuizState.FAILED:
            msg = font_lg.render("Resposta errada! Tente novamente.", True, RED)
            surface.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2,
                                SCREEN_HEIGHT // 2 - 30))
            sub = font_nm.render("Revisite os terminais para rever o conteudo.", True, LIGHTGRAY)
            surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2,
                                SCREEN_HEIGHT // 2 + 20))
            hint = font_sm.render("[ENTER] Tentar de novo", True, GRAY)
            surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                 SCREEN_HEIGHT // 2 + 56))
            return

        q = self.current_question
        if q is None:
            return

        # Progresso
        prog = font_nm.render(
            f"Pergunta {self._cur_idx + 1} de {len(self._active)}", True, LIGHTGRAY)
        surface.blit(prog, (SCREEN_WIDTH // 2 - prog.get_width() // 2, 82))

        # Caixa da pergunta
        q_box = pygame.Rect(SCREEN_WIDTH // 2 - 350, 108, 700, 100)
        pygame.draw.rect(surface, (20, 20, 50),    q_box, border_radius=6)
        pygame.draw.rect(surface, (100, 100, 200), q_box, 2, border_radius=6)
        qtxt = font_nm.render(q.text, True, WHITE)
        surface.blit(qtxt, (q_box.x + 12, q_box.y + 32))

        # Opções
        letters = ["1.", "2.", "3.", "4."]
        for i, opt in enumerate(q.options):
            box    = self._option_rect(i)
            bg     = (30, 30, 70)
            border = (80, 80, 160)
            tc     = WHITE

            if self._feedback_timer > 0:
                if i == self._selected:
                    bg     = (20, 120, 20) if self._last_correct else (140, 20, 20)
                    border = GREEN         if self._last_correct else RED
                elif i == q.correct_index and not self._last_correct:
                    bg, border = (20, 100, 20), GREEN

            elif self._selected < 0:
                mx, my = pygame.mouse.get_pos()
                if box.collidepoint(mx, my):
                    bg, border = (50, 50, 120), (140, 140, 255)

            pygame.draw.rect(surface, bg,     box, border_radius=5)
            pygame.draw.rect(surface, border, box, 2, border_radius=5)
            surface.blit(font_nm.render(f"{letters[i]} {opt}", True, tc),
                         (box.x + 14, box.y + 20))

        # Instrução
        inst = font_sm.render("Pressione 1-4 ou clique para responder", True, DARKGRAY)
        surface.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2,
                             SCREEN_HEIGHT - 36))
