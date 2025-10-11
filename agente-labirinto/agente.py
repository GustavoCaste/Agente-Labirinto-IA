# agente.py

from collections import deque
from typing import Dict, List, Optional, Set, Tuple
from ambiente import Ambiente

# Movimentos (linha, coluna)
DIRECOES = {
    'N': (-1, 0),
    'S': ( 1, 0),
    'L': ( 0, 1),
    'O': ( 0,-1),
}

DELTA_TO_DIR = {v: k for k, v in DIRECOES.items()}

class Agente:
    def __init__(self, ambiente: Ambiente, direcao_inicial: str = 'N', comidas_alvo: Optional[int] = None):
        self.env = ambiente
        self.i, self.j = self.env.entrada
        self.dir = direcao_inicial

        self.passos = 0
        self.comidas_coletadas = 0
        self.comidas_alvo = comidas_alvo if comidas_alvo is not None else self.env.total_comidas

        self.mem: Dict[Tuple[int,int], str] = {}
        self.visitado: Set[Tuple[int,int]] = set()
        self.visitas: Dict[Tuple[int,int], int] = {}
        self.plano: List[str] = []

        self.ultima_pos: Optional[Tuple[int,int]] = None

        self._atualizar_memoria()

    # ===== SENSORES =====
    def getSensor(self) -> List[List[str]]:
        return self.env.get_sensor(self.i, self.j, self.dir)

    def getSensorComidas(self) -> Dict[str, int]:
        return self.env.contar_comidas_direcoes(self.i, self.j)

    def _atualizar_memoria(self):
        sensor = self.getSensor()
        atual = (self.i, self.j)
        self.mem[atual] = self.env.celula(self.i, self.j)

        for r in range(3):
            for c in range(3):
                ai = self.i + (r - 1)
                aj = self.j + (c - 1)
                if r == 2 and c == 2:
                    continue
                self.mem[(ai, aj)] = sensor[r][c]

        self.visitado.add(atual)
        self.visitas[atual] = self.visitas.get(atual, 0) + 1

    # ===== ATUADORES =====
    def setDirection(self, nova_dir: str):
        if nova_dir in DIRECOES:
            self.dir = nova_dir

    def move(self) -> bool:
        di, dj = DIRECOES[self.dir]
        ni, nj = self.i + di, self.j + dj

        if self.env.celula(ni, nj) != 'X':
            prev = (self.i, self.j)
            self.i, self.j = ni, nj
            self.passos += 1
            if self.env.coletar_se_comida(self.i, self.j):
                self.comidas_coletadas += 1
            self.ultima_pos = prev
            self._atualizar_memoria()
            return True
        return False

    # ===== LÓGICA GUIADA POR COMIDA =====
    def _map_diag_para_cardinal(self, d: str) -> str:
        if d in ('NE', 'NO'):
            return 'N'
        if d in ('SE', 'SO'):
            return 'S'
        return d  # já é cardinal

    def _ranking_direcoes_por_comida(self) -> List[str]:
        """
        Retorna uma lista de direções CARDINAIS em ordem de preferência, baseada na contagem de comidas:
        - Compara N,S,L,O e NE,NO,SE,SO.
        - Se um diagonal vencer, mapeia para: NE/NO -> N, SE/SO -> S.
        - Empate: preferir vizinho menos visitado e que não seja a ultima_pos.
        - Ignora direções bloqueadas por 'X'.
        """
        cont = self.getSensorComidas()
        # Lista de candidatos (pode conter diagonais)
        cand = [
            ('N', cont['N']), ('S', cont['S']), ('L', cont['L']), ('O', cont['O']),
            ('NE', cont['NE']), ('NO', cont['NO']), ('SE', cont['SE']), ('SO', cont['SO']),
        ]
        # Ordena por quantidade desc
        cand.sort(key=lambda x: x[1], reverse=True)

        preferencia: List[Tuple[int, str, Tuple[int,int]]] = []
        vistos = set()
        for d_raw, qtd in cand:
            d = self._map_diag_para_cardinal(d_raw)
            if d in vistos:
                continue  # não repetir a mesma cardinal após mapear diagonais
            di, dj = DIRECOES[d]
            q = (self.i + di, self.j + dj)
            if self.env.celula(*q) == 'X':
                continue  # não considerar direção bloqueada
            # desempate: 1) maior comida (já ordenado), 2) não voltar para ultima_pos, 3) menos visitas
            bounce = 1 if (self.ultima_pos is not None and q == self.ultima_pos) else 0
            preferencia.append((bounce, d, q))
            vistos.add(d)

        # Ordena pelo anti-bounce e menos visitas
        preferencia.sort(key=lambda t: (t[0], self.visitas.get(t[2], 0)))
        return [d for _, d, _ in preferencia]

    # ===== PLANEJAMENTO (mantido p/ exploração) =====
    def _vizinhos_livres_mem(self, p: Tuple[int,int]) -> List[Tuple[int,int]]:
        i, j = p
        res = []
        for di, dj in DIRECOES.values():
            q = (i+di, j+dj)
            ch = self.mem.get(q)
            if ch is None:
                continue
            if ch != 'X':
                res.append(q)
        return res

    def _bfs_ate_predicado(self, start: Tuple[int,int], objetivo: callable) -> Optional[List[Tuple[int,int]]]:
        fila = deque([start])
        veio: Dict[Tuple[int,int], Optional[Tuple[int,int]]] = {start: None}
        while fila:
            u = fila.popleft()
            if objetivo(u):
                caminho: List[Tuple[int,int]] = []
                v = u
                while v is not None:
                    caminho.append(v)
                    v = veio[v]
                caminho.reverse()
                return caminho
            viz = self._vizinhos_livres_mem(u)
            viz.sort(key=lambda x: self.visitas.get(x, 0))
            for v in viz:
                if v not in veio:
                    veio[v] = u
                    fila.append(v)
        return None

    def _traduz_caminho_para_direcoes(self, caminho: List[Tuple[int,int]]) -> List[str]:
        dirs: List[str] = []
        for k in range(1, len(caminho)):
            i0, j0 = caminho[k-1]
            i1, j1 = caminho[k]
            di, dj = i1 - i0, j1 - j0
            d = DELTA_TO_DIR.get((di, dj))
            if d:
                dirs.append(d)
        return dirs

    def _fronteiras_exploracao(self) -> List[Tuple[int,int]]:
        fronteiras = []
        for (i, j), ch in self.mem.items():
            if ch == 'X':
                continue
            if ch not in ('_', 'E', 'S', 'o'):
                continue
            for di, dj in DIRECOES.values():
                q = (i+di, j+dj)
                if q not in self.mem:
                    fronteiras.append((i, j))
                    break
        return fronteiras

    def _planejar(self):
        origem = (self.i, self.j)

        # 1) comida conhecida mais próxima (memória)
        comidas = [p for p, ch in self.mem.items() if ch == 'o']
        if comidas:
            alvo_set = set(comidas)
            caminho = self._bfs_ate_predicado(origem, lambda p: p in alvo_set)
            if caminho and len(caminho) > 1:
                self.plano = self._traduz_caminho_para_direcoes(caminho)
                return

        # 2) fronteira
        fronteiras = self._fronteiras_exploracao()
        if fronteiras:
            alvo_set = set(fronteiras)
            caminho = self._bfs_ate_predicado(origem, lambda p: p in alvo_set)
            if caminho and len(caminho) > 1:
                self.plano = self._traduz_caminho_para_direcoes(caminho)
                return

        # 3) sair se já coletou tudo
        if self.comidas_coletadas >= self.comidas_alvo:
            saidas = [p for p, ch in self.mem.items() if ch == 'S']
            if saidas:
                alvo_set = set(saidas)
                caminho = self._bfs_ate_predicado(origem, lambda p: p in alvo_set)
                if caminho and len(caminho) > 1:
                    self.plano = self._traduz_caminho_para_direcoes(caminho)
                    return

        self.plano = []

    # ===== UM PASSO =====
    def step(self):
        # 0) Prioridade: seguir o sensor de comidas (direção com mais 'o')
        ranking = self._ranking_direcoes_por_comida()
        for d in ranking:
            di, dj = DIRECOES[d]
            q = (self.i + di, self.j + dj)
            if self.env.celula(*q) != 'X':
                self.setDirection(d)
                if self.move():
                    return

        # 1) Se não há preferência por comida (tudo zero/bloqueado), planejar
        if not self.plano:
            self._planejar()

        if self.plano:
            prox = self.plano.pop(0)
            self.setDirection(prox)
            if self.move():
                return

        # 2) Explorar vizinho desconhecido (evitando bounce)
        for d in self._direcoes_ordenadas():
            di, dj = DIRECOES[d]
            q = (self.i + di, self.j + dj)
            if q not in self.mem and self.env.celula(*q) != 'X':
                self.setDirection(d)
                if self.move():
                    return

        # 3) Andar por vizinho livre conhecido
        for d in self._direcoes_ordenadas():
            di, dj = DIRECOES[d]
            q = (self.i + di, self.j + dj)
            if self.mem.get(q, 'X') != 'X':
                self.setDirection(d)
                if self.move():
                    return

    # ===== ESTADO =====
    def terminou(self) -> bool:
        em_saida = (self.i, self.j) in self.env.saidas
        return self.comidas_coletadas >= self.comidas_alvo and em_saida

    def pontuacao(self) -> int:
        return self.comidas_coletadas * 10 - self.passos
