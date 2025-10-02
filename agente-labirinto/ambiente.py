# ambiente.py

# Essa classe representa o "mundo" onde o agente vai andar.

from typing import List, Tuple  # só para dicas de tipo (não precisa instalar nada)

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
        # abre o arquivo de texto e lê todas as linhas
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
