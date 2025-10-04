# Agente-Labirinto-IA
Agente Inteligente no Labirinto

Projeto acadêmico para a disciplina de Inteligência Artificial.
O objetivo é implementar um agente que percorra um labirinto, coletando todas as comidas (o) e chegando à saída (S), sem conhecer o mapa previamente.

Estrutura do Projeto
.
├── agente.py        # Classe Agente, responsável por sensores, atuadores e política de movimento (BFS + memória)
├── ambiente.py      # Classe Ambiente, que carrega e gerencia o labirinto
├── main.py          # Arquivo principal da simulação
├── mapas/
│   ├── maze.txt          # Mapa simples fornecido
│   ├── maze_valido.txt   # Mapa maior e solucionável
│   └── maze_grande.txt   # Outro mapa de teste
└── README.md

Regras do Problema

O agente recebe percepções através de um sensor 3×3:

X = parede

_ = corredor

o = comida

E = entrada

S = saída

A posição [2][2] do sensor indica a direção atual do agente (N, S, L, O).

O agente possui atuadores:

setDirection(dir) → muda a direção.

move() → anda na direção apontada, se não houver parede.

Pontuação:

Cada comida coletada = +10 pontos

Cada passo = −1 ponto

Condição de término:

Todas as comidas foram coletadas e o agente está em uma célula de saída S.

Como Executar

Certifique-se de estar com Python 3.x instalado.

Clone/baixe o projeto e entre na pasta raiz.

Execute:

python main.py

Configuração de Mapas

Os mapas são arquivos .txt na pasta mapas/.

Cada mapa deve ser um retângulo formado pelos símbolos válidos (X, _, E, S, o).

Exemplo (mapas/maze.txt):

XXXXXXXXXXXXX
XE__________X
X_XXXXX_XXX_X
X_____X_____X
XXXX_XX_XXXXX
X_o_____o___X
X_X_XXXXX_X_X
X___X___X___X
XXX_X_o_X_XXX
X_______X___X
X_XXXXXXX_X_X
X_________o_X
X_XXXXX_XXX_X
X______S____X
XXXXXXXXXXXXX


Para usar outro mapa, edite no main.py:

caminho_mapa = Path("mapas") / "maze_valido.txt"

Funcionamento do Agente

O agente não conhece o mapa a priori.

Ele cria uma memória interna durante a exploração.

Estratégia:

Se conhece comida → planeja caminho via BFS até a mais próxima.

Se não há comida conhecida → busca uma fronteira de exploração (célula conhecida vizinha de espaço desconhecido).

Quando todas as comidas foram coletadas → busca a saída mais próxima.

Fallback: explora vizinhos desconhecidos ou menos visitados, evitando travar em sobe-desce.

Ajuste da Velocidade

No loop do main.py existe um time.sleep:

time.sleep(0.2)


Aumente/diminua o valor para deixar a simulação mais lenta ou rápida.
Exemplo: 0.5 = meio segundo por passo, 0.05 = rápido (~20 passos/s).
