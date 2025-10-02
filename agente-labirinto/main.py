# main.py
# Simulação: carrega o ambiente, cria o agente e executa passos com
# uma política simples: prioriza comida adjacente; senão, segue “mão direita”.

import time
from pathlib import Path
from ambiente import Ambiente
from agente import Agente, DIRECOES  # usa o agente e o dicionário de direções

# giros relativos à direção atual (N,L,S,O)
GIRO_DIREITA = {'N': 'L', 'L': 'S', 'S': 'O', 'O': 'N'}
GIRO_ESQUERDA = {v: k for k, v in GIRO_DIREITA.items()}

def pode_andar(env: Ambiente, i: int, j: int, dir_: str) -> bool:
    """Retorna True se a célula à frente na direção dir_ não é parede."""
    di, dj = DIRECOES[dir_]
    ni, nj = i + di, j + dj
    return env.celula(ni, nj) != 'X'

def comida_adjacente(env: Ambiente, i: int, j: int) -> str | None:
    """Se houver comida em alguma direção adjacente, retorna a direção ('N','L','S','O')."""
    for d in ['N', 'L', 'S', 'O']:
        di, dj = DIRECOES[d]
        if env.celula(i + di, j + dj) == 'o':
            return d
    return None

def proximo_passo(ag: Agente):
    """
    Política de movimento do agente:
    1) Se há comida adjacente, vira para ela e anda.
    2) Regra da mão direita: tenta direita; se não, reto; se não, esquerda; senão 180°.
    """
    env = ag.env

    # 1) perseguir comida adjacente
    alvo = comida_adjacente(env, ag.i, ag.j)
    if alvo is not None:
        ag.setDirection(alvo)
        ag.move()
        return

    # 2) mão direita
    direita = GIRO_DIREITA[ag.dir]
    if pode_andar(env, ag.i, ag.j, direita):
        ag.setDirection(direita)
        ag.move()
        return

    if pode_andar(env, ag.i, ag.j, ag.dir):
        ag.move()
        return

    esquerda = GIRO_ESQUERDA[ag.dir]
    if pode_andar(env, ag.i, ag.j, esquerda):
        ag.setDirection(esquerda)
        ag.move()
        return

    # 180°
    oposta = GIRO_DIREITA[GIRO_DIREITA[ag.dir]]
    ag.setDirection(oposta)
    ag.move()

def render(env: Ambiente, ag: Agente):
    """Desenha o mapa com o agente (mostra a letra da direção na posição atual)."""
    linhas = []
    for r in range(env.alt):
        row = []
        for c in range(env.larg):
            if (r, c) == (ag.i, ag.j):
                row.append(ag.dir)  # N/L/S/O na posição do agente
            else:
                row.append(env.grid[r][c])
        linhas.append(''.join(row))
    print('\n'.join(linhas))

def main():
    # Arquivo do labirinto (você já usa mapas/maze.txt)
    caminho_mapa = Path("mapas") / "maze.txt"
    if not caminho_mapa.exists():
        print(f"[ERRO] Arquivo do mapa não encontrado em: {caminho_mapa}")
        return

    # Instancia ambiente e agente
    env = Ambiente(str(caminho_mapa))
    ag = Agente(env, direcao_inicial='N')  # pode trocar para 'L','S','O' se quiser testar

    # Info inicial
    print("=== INFO AMBIENTE ===")
    print(f"Dimensões (alt x larg): {env.alt} x {env.larg}")
    print(f"Entrada (E) em: {env.entrada}")
    print(f"Saídas (S): {env.saidas}")
    print(f"Comidas: {env.total_comidas}\n")

    # Render inicial
    print("Início:")
    render(env, ag)
    time.sleep(0.2)

    # Loop de simulação
    max_passos = env.alt * env.larg * 20  # trava de segurança
    for _ in range(max_passos):
        if ag.terminou():
            break
        proximo_passo(ag)

        # “animação” no console
        print("\033[H\033[J", end="")  # limpa console (ANSI)
        render(env, ag)
        time.sleep(0.03)

    # Resultado final
    print("\nFim.")
    print(f"Comidas coletadas: {ag.comidas_coletadas}/{env.total_comidas}")
    print(f"Passos: {ag.passos}")
    print(f"Pontuação: {ag.pontuacao()}")

if __name__ == "__main__":
    main()
