# ambiente.py
# Essa classe representa o "mundo" onde o agente vai andar.

from typing import List, Tuple  # apenas dicas de tipo

class Ambiente:
    def __init__(self, caminho_txt: str):
        # Carrega o mapa do arquivo txt e salva em uma matriz de caracteres
        self.grid: List[List[str]] = self._carregar(caminho_txt)

        # altura = número de linhas, largura = número de colunas
        self.alt = len(self.grid)
        self.larg = len(self.grid[0]) if self.alt > 0 else 0

        # guarda onde está a entrada e todas as saídas
        self.entrada = self._achar('E')
        self.saidas = self._achar_todos('S')

        # conta quantas comidas existem no mapa
        self.total_comidas = sum(linha.count('o') for linha in self.grid)

    def _carregar(self, caminho: str) -> List[List[str]]:
        # abre o arquivo de texto e lê todas as linhas (ignora linhas vazias finais)
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = [list(l.strip('\n')) for l in f.readlines() if l.strip('\n')]
        # valida se todas as linhas têm o mesmo tamanho
        larg = len(linhas[0])
        assert all(len(l) == larg for l in linhas), "Mapa com larguras diferentes."
        return linhas

    def _achar(self, alvo: str) -> Tuple[int, int]:
        # procura a primeira ocorrência de um símbolo (ex: 'E')
        for i, linha in enumerate(self.grid):
            for j, c in enumerate(linha):
                if c == alvo:
                    return (i, j)
        raise ValueError(f"Símbolo '{alvo}' não encontrado no mapa.")

    def _achar_todos(self, alvo: str) -> List[Tuple[int, int]]:
        # retorna todas as posições de um símbolo (ex: todas as saídas 'S')
        coords = []
        for i, linha in enumerate(self.grid):
            for j, c in enumerate(linha):
                if c == alvo:
                    coords.append((i, j))
        return coords

    def dentro(self, i: int, j: int) -> bool:
        # verifica se uma posição está dentro do mapa
        return 0 <= i < self.alt and 0 <= j < self.larg

    def celula(self, i: int, j: int) -> str:
        # retorna o que existe na posição (i,j)
        # se estiver fora do mapa, conta como parede 'X'
        if not self.dentro(i, j):
            return 'X'
        return self.grid[i][j]

    def coletar_se_comida(self, i: int, j: int) -> bool:
        # se houver comida na posição, substitui por '_' e retorna True
        if self.grid[i][j] == 'o':
            self.grid[i][j] = '_'
            return True
        return False

    # === SENSOR 3x3 ===
    def get_sensor(self, i: int, j: int, direcao: str) -> List[List[str]]:
        """
        Retorna uma matriz 3x3 com o entorno do agente.
        Padrão adotado (linhas x colunas):
            [0,0]=NW  [0,1]=N   [0,2]=NE
            [1,0]=W   [1,1]=C   [1,2]=E
            [2,0]=SW  [2,1]=S   [2,2]=DIRECAO (letra 'N','S','L','O')

        Fora do mapa conta como 'X'. [1,1] reflete o terreno atual.
        """
        sensor = [['X' for _ in range(3)] for _ in range(3)]

        # vizinhança relativa ao (i,j)
        rel = [
            (-1, -1), (-1, 0), (-1, 1),
            (0,  -1), (0,  0), (0,  1),
            (1,  -1), (1,  0), (1,  1),
        ]

        idx = 0
        for r in range(3):
            for c in range(3):
                if r == 2 and c == 2:
                    # posição de direção do agente (exigência do enunciado)
                    sensor[r][c] = direcao
                else:
                    di, dj = rel[idx]
                    sensor[r][c] = self.celula(i + di, j + dj)
                idx += 1

        return sensor
