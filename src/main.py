# =============================================================
#  CC Tensei — main.py
#  Ponto de entrada do jogo.
#
#  Disciplina : Introducao a Jogos — UERN
#  Discente   : Juscelino K P Junior
#  Docente    : Raul Paradeda
# =============================================================

import sys
import os

# Garante que importações relativas funcionem ao rodar main.py diretamente
sys.path.insert(0, os.path.dirname(__file__))

import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE
from game import Game


def main() -> None:
    pygame.init()
    pygame.display.set_caption(GAME_TITLE)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    game = Game(screen)
    game.run()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
