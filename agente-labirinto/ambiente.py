# ambiente.py
# Essa classe representa o "mundo" onde o agente vai andar.

from typing import Dict, List, Tuple

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
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = [list(l.strip('\n')) for l in f.readlines() if l.strip('\n')]
        larg = len(linhas[0])
        assert all(len(l) == larg for l in linhas), "Mapa com larguras diferentes."
        return linhas

    def _achar(self, alvo: str) -> Tuple[int, int]:
        for i, linha in enumerate(self.grid):
            for j, c in enumerate(linha):
                if c == alvo:
                    return (i, j)
        raise ValueError(f"Símbolo '{alvo}' não encontrado no mapa.")

    def _achar_todos(self, alvo: str) -> List[Tuple[int, int]]:
        coords = []
        for i, linha in enumerate(self.grid):
            for j, c in enumerate(linha):
                if c == alvo:
                    coords.append((i, j))
        return coords

    def dentro(self, i: int, j: int) -> bool:
        return 0 <= i < self.alt and 0 <= j < self.larg

    def celula(self, i: int, j: int) -> str:
        if not self.dentro(i, j):
            return 'X'
        return self.grid[i][j]

    def coletar_se_comida(self, i: int, j: int) -> bool:
        if self.grid[i][j] == 'o':
            self.grid[i][j] = '_'
            return True
        return False

    # === SENSOR 3x3 ===
    def get_sensor(self, i: int, j: int, direcao: str) -> List[List[str]]:
        sensor = [['X' for _ in range(3)] for _ in range(3)]

        rel = [
            (-1, -1), (-1, 0), (-1, 1),
            (0,  -1), (0,  0), (0,  1),
            (1,  -1), (1,  0), (1,  1),
        ]

        idx = 0
        for r in range(3):
            for c in range(3):
                if r == 2 and c == 2:
                    sensor[r][c] = direcao
                else:
                    di, dj = rel[idx]
                    sensor[r][c] = self.celula(i + di, j + dj)
                idx += 1

        return sensor

    def _contar_ray(self, i: int, j: int, di: int, dj: int) -> int:
        ci, cj = i + di, j + dj
        total = 0
        while self.dentro(ci, cj):
            if self.grid[ci][cj] == 'o':
                total += 1
            ci += di
            cj += dj
        return total

    def _contar_setor(self, i: int, j: int, sinal_i: int, sinal_j: int) -> int:
        total = 0
        for r in range(self.alt):
            for c in range(self.larg):
                cond_i = (r - i) * sinal_i < 0   # acima (−1) / abaixo (+1)
                cond_j = (c - j) * sinal_j > 0   # direita (+1) / esquerda (−1)
                if cond_i and cond_j and self.grid[r][c] == 'o':
                    total += 1
        return total

    def contar_comidas_direcoes(self, i: int, j: int) -> Dict[str, int]:
        n = self._contar_ray(i, j, -1,  0)
        s = self._contar_ray(i, j,  1,  0)
        l = self._contar_ray(i, j,  0,  1)
        o = self._contar_ray(i, j,  0, -1)

        ne = self._contar_setor(i, j, -1, +1)
        no = self._contar_setor(i, j, -1, -1)
        se = self._contar_setor(i, j, +1, +1)
        so = self._contar_setor(i, j, +1, -1)

        return {'N': n, 'S': s, 'L': l, 'O': o, 'NE': ne, 'NO': no, 'SE': se, 'SO': so}
