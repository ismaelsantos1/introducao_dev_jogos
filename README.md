# CC Tensei — O Estudante Reencarnado no Mundo Digital

Jogo educativo de plataforma 2D (run-and-gun) desenvolvido com **Python + pygame**
para a disciplina de **Introdução a Jogos** — UERN.

**Discente:** Juscelino K P Junior  
**Docente:** Raul Paradeda

---

## Sobre o jogo

Um estudante de Ciência da Computação é reencarnado em um mundo digital.
Para voltar para casa, ele precisa atravessar 4 regiões, aprender os pilares
da **Programação Orientada a Objetos** com professores-NPC e derrotar o
guardião (Boss) de cada fase.

| Fase | Pilar            | Boss             |
|------|------------------|------------------|
| 1    | Encapsulamento   | CPU-001          |
| 2    | Herança          | HEIR-X           |
| 3    | Polimorfismo     | POLY-MORPH       |
| 4    | Abstração        | CORE-ABS         |

---

## Como jogar

### Controles

| Tecla / Botão          | Ação                              |
|------------------------|-----------------------------------|
| `A` / `D`              | Mover esquerda / direita          |
| `W` ou `ESPAÇO`        | Pular                             |
| `CLIQUE ESQUERDO`      | Atirar "0" (rápido, dano menor)   |
| `CLIQUE DIREITO`       | Segurar → soltar para atirar "1"  |
| `E` ou `S`             | Interagir com NPC / terminal      |
| `ESC`                  | Pausar                            |
| `1` `2` `3` `4`        | Responder quiz                    |

### Fluxo de fase

1. Explore a fase, derrote vírus e **hackeie os terminais** (`E`) para
   aprender o conteúdo do pilar.
2. Fale com o **Professor-NPC** para ouvir a explicação completa.
3. Ao chegar à **porta do Boss**, responda o quiz corretamente para entrar.
4. Derrote o Boss no estilo run-and-gun.

> **CPU-001 (Fase 1):** o escudo só abre em janelas de tempo — apenas
> nesses momentos o Boss pode ser atingido (mecânica de Encapsulamento).

---

## Instalação e execução

```bash
# 1. Crie e ative um ambiente virtual (recomendado)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o jogo
python src/main.py
```

Requer **Python 3.10+** e **pygame 2.6+**.

---

## Estrutura do projeto

```
introducao_dev_jogos/
├── src/
│   ├── main.py          # ponto de entrada
│   ├── game.py          # GerenciadorJogo — máquina de estados
│   ├── constants.py     # constantes e enums
│   ├── player.py        # protagonista
│   ├── projectile.py    # projéteis binários "0" e "1"
│   ├── enemy.py         # hierarquia: Enemy → Virus / VirusRapido / VirusGrande
│   ├── boss.py          # CPU-001 com mecânica de escudo
│   ├── npc.py           # professores com diálogo educativo
│   ├── quiz.py          # barreira de perguntas antes do Boss
│   ├── level.py         # layout e lógica da fase
│   └── renderer.py      # fundo, paralaxe, telas de menu/gameover
├── assets/
│   ├── sprites/         # sprites futuros
│   └── sounds/          # sons futuros
├── requirements.txt
└── README.md
```

---

## Pilares da POO no código

| Pilar            | Onde aparece no código                                      |
|------------------|-------------------------------------------------------------|
| **Encapsulamento**| `Player._iframe`, `Boss.shielded` (property), atributos privados com `_` |
| **Herança**      | `Enemy` → `Virus` → `VirusRapido` / `VirusGrande`           |
| **Polimorfismo** | `enemy.draw()` / `enemy._ai()` sobrescritos em cada subclasse |
| **Abstração**    | `create_enemy()` (Factory Method) abstrai qual inimigo criar |
