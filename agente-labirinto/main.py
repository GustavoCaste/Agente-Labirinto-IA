# main.py
# Simulação: carrega o ambiente, cria o agente e executa passos com memória + BFS.

import time
from pathlib import Path
from ambiente import Ambiente
from agente import Agente

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
    # Arquivo do labirinto (mapas/maze.txt)
    caminho_mapa = Path("mapas") / "maze_grande.txt"
    if not caminho_mapa.exists():
        print(f"[ERRO] Arquivo do mapa não encontrado em: {caminho_mapa}")
        return

    # Instancia ambiente e agente
    env = Ambiente(str(caminho_mapa))
    ag = Agente(env, direcao_inicial='N')

    # Info inicial
    print("=== INFO AMBIENTE ===")
    print(f"Dimensões (alt x larg): {env.alt} x {env.larg}")
    print(f"Entrada (E) em: {env.entrada}")
    print(f"Saídas (S): {env.saidas}")
    print(f"Comidas: {env.total_comidas}\n")

    # Render inicial
    print("Início:")
    render(env, ag)
    time.sleep(0.02)

    # Loop de simulação
    max_passos = env.alt * env.larg * 50  # trava de segurança (aumentado)
    for _ in range(max_passos):
        if ag.terminou():
            break
        ag.step()

        # “animação” no console
        print("\033[H\033[J", end="")  # limpa console (ANSI)
        render(env, ag)
        time.sleep(0.02)

    # Resultado final
    print("\nFim.")
    print(f"Comidas coletadas: {ag.comidas_coletadas}/{env.total_comidas}")
    print(f"Passos: {ag.passos}")
    print(f"Pontuação: {ag.pontuacao()}")

if __name__ == "__main__":
    main()
