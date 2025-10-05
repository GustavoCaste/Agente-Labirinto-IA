# main.py
# Simulação: carrega o ambiente, cria o agente e executa passos com memória + BFS.
# Versão com gravação de vídeo simples usando OpenCV (opcional).

import time
from pathlib import Path
from ambiente import Ambiente
from agente import Agente

# ===== CONFIGURAÇÃO DA GRAVAÇÃO =====
GRAVAR_VIDEO = True                 # defina False para desativar gravação
NOME_VIDEO = "simulacao.avi"
FPS = 10.0
CELL_SIZE = 22                      # pixels por célula (define a resolução do vídeo)

def _tentar_importar_cv2():
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
        return cv2, np
    except Exception:
        return None, None

def _abrir_videowriter(cv2, largura_cel, altura_cel):
    """Tenta abrir o VideoWriter com alguns codecs comuns (XVID -> MJPG -> MP4V)."""
    frame_size = (largura_cel * CELL_SIZE, altura_cel * CELL_SIZE)
    for codec in ("XVID", "MJPG", "MP4V"):
        fourcc = cv2.VideoWriter_fourcc(*codec)
        vw = cv2.VideoWriter(NOME_VIDEO, fourcc, FPS, frame_size)
        if vw.isOpened():
            print(f"[VÍDEO] Gravando em {NOME_VIDEO} (codec {codec}, {FPS} fps, {frame_size[0]}x{frame_size[1]})")
            return vw
        try:
            vw.release()
        except Exception:
            pass
    print("[VÍDEO] Aviso: não foi possível abrir VideoWriter. Seguiremos sem gravar.")
    return None

def _frame_do_estado(cv2, np, env: Ambiente, ag: Agente):
    """Gera um frame (imagem BGR) a partir do grid do ambiente e do estado do agente."""
    h_px = env.alt * CELL_SIZE
    w_px = env.larg * CELL_SIZE
    img = np.ones((h_px, w_px, 3), dtype=np.uint8) * 255  # fundo branco

    # Cores BGR
    cores = {
        'X': (0, 0, 0),         # parede preto
        '_': (200, 200, 200),   # corredor cinza claro
        'E': (0, 255, 0),       # entrada verde
        'S': (255, 0, 0),       # saída azul (BGR)
        'o': (0, 200, 200),     # comida ciano
    }

    # desenha células
    for i in range(env.alt):
        for j in range(env.larg):
            ch = env.grid[i][j]
            cor = cores.get(ch, (220, 220, 220))
            y1, y2 = i * CELL_SIZE, (i + 1) * CELL_SIZE
            x1, x2 = j * CELL_SIZE, (j + 1) * CELL_SIZE
            cv2.rectangle(img, (x1, y1), (x2, y2), cor, -1)

    # desenha agente (círculo + seta da direção)
    ai, aj = ag.i, ag.j
    cx = aj * CELL_SIZE + CELL_SIZE // 2
    cy = ai * CELL_SIZE + CELL_SIZE // 2
    cv2.circle(img, (cx, cy), CELL_SIZE // 2 - 2, (0, 0, 255), -1)  # agente vermelho

    dx = dy = 0
    if ag.dir == 'N':
        dy = -CELL_SIZE // 2 + 3
    elif ag.dir == 'S':
        dy = CELL_SIZE // 2 - 3
    elif ag.dir == 'L':
        dx = CELL_SIZE // 2 - 3
    elif ag.dir == 'O':
        dx = -CELL_SIZE // 2 + 3
    cv2.line(img, (cx, cy), (cx + dx, cy + dy), (255, 255, 255), 2)

    return img

def render(env: Ambiente, ag: Agente):
    """Desenha o mapa no console (mostra a letra da direção na posição atual)."""
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
    # Arquivo do labirinto
    caminho_mapa = Path("mapas") / "maze.txt"
    if not caminho_mapa.exists():
        print(f"[ERRO] Arquivo do mapa não encontrado em: {caminho_mapa}")
        return

    # Instancia ambiente e agente
    env = Ambiente(str(caminho_mapa))
    # passa explicitamente a quantidade de comidas (enunciado literal)
    ag = Agente(env, direcao_inicial='N', comidas_alvo=env.total_comidas)

    # Info inicial
    print("=== INFO AMBIENTE ===")
    print(f"Dimensões (alt x larg): {env.alt} x {env.larg}")
    print(f"Entrada (E) em: {env.entrada}")
    print(f"Saídas (S): {env.saidas}")
    print(f"Comidas: {env.total_comidas}\n")

    # Inicializa gravação (opcional)
    cv2 = np = None
    writer = None
    if GRAVAR_VIDEO:
        cv2, np = _tentar_importar_cv2()
        if cv2 is None:
            print("[VÍDEO] OpenCV/Numpy não encontrados. Instale com: pip install opencv-python numpy")
        else:
            writer = _abrir_videowriter(cv2, env.larg, env.alt)

    # Render inicial
    print("Início:")
    render(env, ag)
    if writer is not None:
        frame = _frame_do_estado(cv2, np, env, ag)
        writer.write(frame)
    time.sleep(0.2)

    # Loop de simulação
    max_passos = env.alt * env.larg * 50  # trava de segurança
    for _ in range(max_passos):
        if ag.terminou():
            break
        ag.step()

        # console
        print("\033[H\033[J", end="")  # limpa console (ANSI)
        render(env, ag)

        # vídeo
        if writer is not None:
            frame = _frame_do_estado(cv2, np, env, ag)
            writer.write(frame)

        time.sleep(0.02)

    # Finaliza vídeo
    if writer is not None:
        writer.release()
        print(f"[VÍDEO] Arquivo salvo: {NOME_VIDEO}")

    # Resultado final
    print("\nFim.")
    print(f"Comidas coletadas: {ag.comidas_coletadas}/{env.total_comidas}")
    print(f"Passos: {ag.passos}")
    print(f"Pontuação: {ag.pontuacao()}")

if __name__ == "__main__":
    main()
