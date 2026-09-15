# CC Tensei — Os 4 Pilares da POO no Código

> Disciplina: Introdução a Jogos — UERN  
> Discente: Juscelino K P Junior  
> Docente: Raul Paradeda

---

## Sumário

1. [Encapsulamento](#1-encapsulamento)
2. [Herança](#2-herança)
3. [Polimorfismo](#3-polimorfismo)
4. [Abstração](#4-abstração)
5. [Resumo](#5-resumo)

---

## 1. Encapsulamento

> *"Proteger o estado interno de um objeto, expondo apenas o necessário."*

Esse é o pilar mais visível no projeto, aplicado em três camadas.

### 1.1 Atributos privados com `_`

Em Python, o prefixo `_` indica que o atributo é de uso interno da classe.
No `Player` (`src/player.py`) toda a física é privada:

```python
# src/player.py — Player.__init__
self._x        = float(x)    # posição real (float de precisão)
self._y        = float(y)
self._vx       = 0.0          # velocidade horizontal
self._vy       = 0.0          # velocidade vertical
self._iframe   = 0.0          # timer de invencibilidade
self._shoot_cd = 0.0          # cooldown entre disparos
```

Ninguém de fora toca nesses valores diretamente.
O mesmo padrão está em `Enemy`, `Boss` e `NPC`.
O atributo `self.rect` (o `pygame.Rect`) é **público** porque é o que o mundo
externo precisa para colisão — o resto fica encapsulado.

### 1.2 `@property` — getter controlado

No `Boss` (`src/boss.py`), o estado do escudo não é um booleano exposto
diretamente. É uma **propriedade** que calcula o resultado com base em dois
atributos internos:

```python
# src/boss.py — Boss
@property
def shielded(self) -> bool:
    if self.phase == BossPhase.PHASE2:
        return False          # na fase 2, escudo não existe mais
    return not self._shield_open
```

Quem chama `boss.shielded` lê um valor simples.
A lógica de "em qual fase estou? o timer abriu o escudo?" fica
completamente oculta. A propriedade é usada diretamente no sistema de
colisão:

```python
# src/boss.py — Boss.check_player_bullets
def check_player_bullets(self, bullets):
    if not self.active or self.shielded:   # <-- property, não atributo direto
        return
```

O `NPC` (`src/npc.py`) aplica a mesma ideia para expor a linha de diálogo
atual e o progresso sem revelar a lista interna `_lines` nem o índice `_cur`:

```python
# src/npc.py — NPC
@property
def current_line(self) -> str:
    return self._lines[self._cur]

@property
def progress(self):
    return self._cur + 1, len(self._lines)
```

### 1.3 Métodos que controlam acesso (setter com lógica)

O disparo do player nunca acontece diretamente — passa pelo método
`_spawn_bullet`, que encapsula a criação do projétil e o reset do cooldown:

```python
# src/player.py — Player._spawn_bullet
def _spawn_bullet(self, proj_type):
    bx = self.rect.right if self.direction == Direction.RIGHT else self.rect.left
    by = self.rect.top + PLAYER_H * 0.45
    self.bullets.append(Projectile(bx, by, self.direction, proj_type, True))
    self._shoot_cd = PLAYER_SHOOT_DELAY   # controla cooldown internamente
```

O método `take_damage` encapsula toda a lógica de invencibilidade e morte:

```python
# src/player.py — Player.take_damage
def take_damage(self, amount):
    if not self.active or self._iframe > 0:
        return                         # ignora dano se invencível
    self.hp -= amount
    self._iframe = PLAYER_IFRAME_TIME  # ativa iframes
    if self.hp <= 0:
        self.hp     = 0
        self.active = False
```

Qualquer inimigo chama `player.take_damage(10)` — uma linha.
Toda a complexidade de iframes, morte e clamp de HP fica encapsulada.

---

## 2. Herança

> *"Uma classe reutiliza atributos e métodos de outra, estendendo ou especializando o comportamento."*

A hierarquia de inimigos é o exemplo mais direto do projeto:

```
Enemy  (classe base)
├── Virus
├── VirusRapido
└── VirusGrande
```

### 2.1 A classe base define o contrato comum

`Enemy` (`src/enemy.py`) inicializa tudo que qualquer inimigo vai precisar:
posição, velocidade, HP, speed, damage, direção, iframes.
Os métodos `update()`, `take_damage()`, `check_player_collision()` e
`_resolve_ground()` são implementados **uma única vez** e herdados pelas
três subclasses sem nenhuma repetição.

### 2.2 Subclasses constroem apenas o que é diferente

`Virus` passa apenas seus valores únicos para a base via `super()`:

```python
# src/enemy.py — Virus
class Virus(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, VIRUS_HP, VIRUS_SPEED, VIRUS_DAMAGE,
                         VIRUS_W, VIRUS_H, EnemyType.VIRUS)
```

`VirusRapido` faz o mesmo e acrescenta **só** o timer de salto, que é
exclusivo dele:

```python
# src/enemy.py — VirusRapido
class VirusRapido(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, VFAST_HP, VFAST_SPEED, VFAST_DAMAGE,
                         VFAST_W, VFAST_H, EnemyType.VIRUS_FAST)
        self._jump_timer = 0.0   # único atributo novo
```

Toda a física (gravidade, colisão com plataformas, animação de piscar ao
tomar dano) vem de graça pela herança.

### 2.3 Herança com extensão — `super()` reutiliza e a subclasse adiciona

`VirusRapido` sobrescreve `_ai()` mas chama `super()._ai(dt)` primeiro,
reutilizando a patrulha da base e adicionando o salto por cima:

```python
# src/enemy.py — VirusRapido._ai
def _ai(self, dt):
    super()._ai(dt)            # patrulha herdada da base (sem repetição)
    self._jump_timer += dt
    if self._jump_timer >= 2.0 and self.on_ground:
        self._vy         = -420.0   # salto exclusivo do VirusRapido
        self._jump_timer = 0.0
```

---

## 3. Polimorfismo

> *"A mesma operação com comportamentos diferentes dependendo do objeto."*

O polimorfismo aparece em três formas no projeto.

### 3.1 Sobrescrita de `draw()` — mesmo nome, visuais completamente distintos

A classe base `Enemy` declara `draw()` como método vazio:

```python
# src/enemy.py — Enemy
def draw(self, surface, offset):
    """Sobrescrita por cada subclasse."""
    pass
```

Cada subclasse implementa seu próprio visual. O loop de renderização em
`game.py` chama exatamente a mesma linha para qualquer inimigo:

```python
# src/game.py — Game._draw
for e in lvl.enemies:
    e.draw(self.screen, offset)    # Python resolve qual draw() chamar
```

O resultado visual é completamente diferente por objeto:

| Classe | Visual |
|---|---|
| `Virus.draw()` | Blob vermelho com olhos e boca serrilhada |
| `VirusRapido.draw()` | Losango com olho central e raios amarelos |
| `VirusGrande.draw()` | Tanque quadrado com 4 olhos amarelos |

Mas todos terminam chamando `self._draw_hp_bar(surface, ox, oy)` —
método herdado da base, sem repetição.

### 3.2 Polimorfismo via tabela de dados em `Projectile`

Em vez de criar subclasses para os dois projéteis, `projectile.py` usa um
dicionário como tabela de configuração (análogo a uma *vtable*):

```python
# src/projectile.py
_PROJ_DATA = {
    ProjType.ZERO: dict(speed=720, damage=10, w=14, h=8,  color=PROJ0_COL),
    ProjType.ONE:  dict(speed=380, damage=28, w=18, h=12, color=PROJ1_COL),
}
```

O construtor lê os dados pelo tipo. O método `draw()` se comporta diferente
para cada tipo dentro da mesma classe:

```python
# src/projectile.py — Projectile.draw
if self.proj_type == ProjType.ZERO:
    # "0" — oval amarela com borda preta
    pygame.draw.rect(surface, BLACK, draw_rect, border_radius=4)
    pygame.draw.rect(surface, self._color, draw_rect.inflate(-2, -2), border_radius=3)
else:
    # "1" — retângulo magenta com brilho central
    pygame.draw.rect(surface, self._color, ...)
    shine = pygame.Rect(inner.centerx - 2, inner.y + 1, 4, inner.height - 2)
    pygame.draw.rect(surface, (255, 210, 245), shine)
```

Mesmo nome `draw()`, comportamento visual diferente por tipo.

### 3.3 Polimorfismo de comportamento no Boss por fase

O `Boss` muda de padrão de ataque dependendo da fase em que está, usando
o mesmo gatilho de tiro:

```python
# src/boss.py — Boss.update
if self.phase == BossPhase.PHASE1:
    self._attack_straight(player)   # 1 projétil reto em direção ao player
else:
    self._attack_spread(player)     # leque de 3 projéteis
```

Em `game.py`, o código simplesmente chama
`lvl.boss.update(dt, player, platforms)` — não sabe em qual fase o boss
está, não sabe qual ataque será disparado.
O comportamento polimórfico acontece internamente.

---

## 4. Abstração

> *"Representar o essencial, ocultar os detalhes desnecessários."*

### 4.1 Factory Method — `create_enemy()`

Em `enemy.py`, a função `create_enemy()` aplica o padrão **Factory Method**:
o chamador pede um inimigo por tipo, sem precisar saber qual classe concreta
será instanciada:

```python
# src/enemy.py — Factory Method
def create_enemy(enemy_type, x, y):
    if enemy_type == EnemyType.VIRUS:
        return Virus(x, y)
    elif enemy_type == EnemyType.VIRUS_FAST:
        return VirusRapido(x, y)
    elif enemy_type == EnemyType.VIRUS_BIG:
        return VirusGrande(x, y)
```

Em `level.py`, o layout da fase é uma lista de tuplas `(x, y, tipo)`:

```python
# src/level.py — Level.__init__
self.enemies = [
    create_enemy(t, x, y) for x, y, t in _ENEMY_SPAWNS
]
```

O `Level` não importa `Virus`, `VirusRapido` ou `VirusGrande` diretamente —
só `create_enemy`. A decisão de qual classe construir fica abstraída dentro
da fábrica.

### 4.2 Interface implícita (duck typing)

Todas as entidades do jogo seguem um contrato informal: têm `update()`,
`draw()`, `active` e `rect`. O loop principal em `game.py` trata player,
inimigos e boss com as mesmas chamadas, sem precisar conhecer os detalhes
internos de nenhum deles:

```python
# src/game.py — Game._update
p.update(dt, lvl.platforms)              # Player
for e in lvl.enemies:
    e.update(dt, lvl.platforms)          # qualquer Enemy (Virus, VirusRapido...)
lvl.boss.update(dt, p, lvl.platforms)    # Boss
```

### 4.3 Câmera — ocultação da complexidade de suavização

A propriedade `Camera.offset` em `game.py` expõe apenas uma tupla `(int, int)`
para todo o sistema de renderização. Toda a lógica de *lerp*, clamp de bordas
do mundo e conversão `float → int` fica dentro de `Camera.update()`,
completamente oculta de qualquer código de desenho:

```python
# src/game.py — Camera
@property
def offset(self):
    return int(self.x), int(self.y)   # interface simples para o mundo externo

def update(self, player, dt):
    # complexidade totalmente abstraída aqui dentro:
    target_x = player.rect.centerx - SCREEN_WIDTH // 2
    self.x  += (target_x - self.x) * CAM_LERP * dt
    self.x   = max(0.0, min(self.x, float(LEVEL_WIDTH - SCREEN_WIDTH)))
```

---

## 5. Resumo

| Pilar | Arquivo(s) principal(is) | Como aparece no código |
|---|---|---|
| **Encapsulamento** | `player.py`, `boss.py`, `npc.py` | Atributos `_x _y _iframe`, `@property shielded`, `take_damage()` |
| **Herança** | `enemy.py` | `Enemy → Virus / VirusRapido / VirusGrande`, `super().__init__()`, `super()._ai()` |
| **Polimorfismo** | `enemy.py`, `projectile.py`, `boss.py` | `draw()` sobrescrito por subclasse, tabela `_PROJ_DATA`, ataque por fase |
| **Abstração** | `enemy.py`, `game.py` | `create_enemy()` (Factory Method), duck typing, `Camera.offset` |

---

*Gerado automaticamente a partir do código-fonte do projeto CC Tensei.*
