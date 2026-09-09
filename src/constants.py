# =============================================================
#  CC Tensei — constants.py
#  Todas as constantes e enums do jogo.
# =============================================================

from enum import Enum, auto

# --- Janela ---------------------------------------------------
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
GAME_TITLE    = "CC Tensei"
TARGET_FPS    = 60

# --- Mundo / Física ------------------------------------------
GRAVITY        = 1400       # px/s²
TILE           = 32         # tamanho do tile em px
GROUND_Y       = SCREEN_HEIGHT - TILE * 2
LEVEL_WIDTH    = TILE * 130  # largura total da fase

# --- Player --------------------------------------------------
PLAYER_SPEED        = 230       # px/s
PLAYER_JUMP_FORCE   = -620      # negativo = sobe
PLAYER_MAX_HP       = 100
PLAYER_W            = 28
PLAYER_H            = 40
PLAYER_SHOOT_DELAY  = 0.18      # s entre disparos
PLAYER_IFRAME_TIME  = 1.2       # s de invencibilidade após dano
PLAYER_CHARGE_TIME  = 0.55      # s para carregar tiro "1"

# --- Projéteis -----------------------------------------------
PROJ_ZERO_SPEED  = 720
PROJ_ZERO_DAMAGE = 10
PROJ_ZERO_W      = 14
PROJ_ZERO_H      = 8

PROJ_ONE_SPEED   = 380
PROJ_ONE_DAMAGE  = 28
PROJ_ONE_W       = 18
PROJ_ONE_H       = 12

MAX_PROJECTILES  = 64

# --- Inimigos ------------------------------------------------
VIRUS_HP     = 30;  VIRUS_SPEED     = 80;  VIRUS_DAMAGE     = 10
VIRUS_W      = 26;  VIRUS_H         = 26

VFAST_HP     = 20;  VFAST_SPEED     = 160; VFAST_DAMAGE     = 8
VFAST_W      = 24;  VFAST_H         = 24

VBIG_HP      = 90;  VBIG_SPEED      = 45;  VBIG_DAMAGE      = 22
VBIG_W       = 42;  VBIG_H          = 42

PATROL_RANGE = 130   # px de cada lado a partir da origem

# --- Boss ----------------------------------------------------
BOSS_W            = 84
BOSS_H            = 84
BOSS_MAX_HP       = 300
BOSS_PHASE2_HP    = 150        # HP ao entrar na fase 2
BOSS_BULLET_SPEED = 340
BOSS_SHOOT_DELAY  = 1.8
BOSS_DAMAGE       = 25
SHIELD_CYCLE      = 3.5        # s por ciclo
SHIELD_OPEN       = 1.2        # s com escudo aberto

# --- NPC -----------------------------------------------------
NPC_W            = 28
NPC_H            = 44
NPC_INTERACT_R   = 70          # px para ativar diálogo

# --- Quiz ----------------------------------------------------
QUESTIONS_PER_GATE = 2

# --- UI / HUD ------------------------------------------------
HUD_MARGIN   = 12
BAR_W        = 160
BAR_H        = 16

# --- Câmera --------------------------------------------------
CAM_LERP     = 8.0

# --- Cores (R, G, B) -----------------------------------------
SKY        = (100, 180, 240)
GROUND_COL = (101,  67,  33)
GRASS      = ( 80, 180,  60)
PLATFORM   = (130,  90,  45)
CLOUD      = (230, 240, 255)
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (150, 150, 150)
DARKGRAY   = ( 60,  60,  60)
LIGHTGRAY  = (200, 200, 200)
RED        = (220,  40,  40)
GREEN      = ( 40, 200,  60)
YELLOW     = (255, 220,  50)
BLUE       = ( 60, 120, 220)
PURPLE     = (180,  60, 240)
CYAN       = ( 40, 200, 200)
ORANGE     = (240, 140,  30)

PLAYER_COL   = ( 50, 110, 210)
VIRUS_COL    = (200,  40,  40)
VFAST_COL    = ( 40, 200, 160)
VBIG_COL     = (200,  20, 100)
BOSS_COL     = (220,  80,  20)
NPC_COL      = ( 40, 200, 140)
PROJ0_COL    = (255, 220,  50)
PROJ1_COL    = (255, 100, 200)
HP_GREEN     = ( 40, 200,  60)
HP_RED       = (200,  40,  40)
DIALOG_BG    = ( 10,  10,  30)
GATE_COL     = ( 50,  50, 200)
GATE_OPEN    = ( 50, 200,  50)
TERMINAL_COL = ( 20,  20,  60)
SHIELD_COL   = ( 80, 140, 255)


# =============================================================
#  Enums
# =============================================================

class GameState(Enum):
    MENU        = auto()
    PLAYING     = auto()
    PAUSED      = auto()
    DIALOG      = auto()   # NPC falando
    QUIZ        = auto()   # barreira do Boss
    BOSS_FIGHT  = auto()
    LEVEL_CLEAR = auto()
    GAME_OVER   = auto()
    VICTORY     = auto()


class OOPPillar(Enum):
    ENCAPSULAMENTO = 0
    HERANCA        = 1
    POLIMORFISMO   = 2
    ABSTRACAO      = 3


class EnemyType(Enum):
    VIRUS      = auto()
    VIRUS_FAST = auto()
    VIRUS_BIG  = auto()


class ProjType(Enum):
    ZERO = auto()   # rápido, dano menor
    ONE  = auto()   # lento/carregado, dano maior


class Direction(Enum):
    LEFT  = -1
    RIGHT =  1


class BossPhase(Enum):
    PHASE1 = auto()
    PHASE2 = auto()
    DEAD   = auto()


class QuizState(Enum):
    WAITING = auto()
    ACTIVE  = auto()
    PASSED  = auto()
    FAILED  = auto()
