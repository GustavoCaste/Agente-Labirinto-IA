# agente.py
# Essa classe representa o "robô" que vai andar no labirinto.

from ambiente import Ambiente

# Dicionário com os movimentos possíveis (linha, coluna)
DIRECOES = {
    'N': (-1, 0),   # norte: sobe uma linha
    'S': (1, 0),    # sul: desce uma linha
    'L': (0, 1),    # leste: anda uma coluna para a direita
    'O': (0, -1)    # oeste: anda uma coluna para a esquerda
}

class Agente:
    def __init__(self, ambiente: Ambiente, direcao_inicial: str = 'N'):
        # referência ao ambiente
        self.env = ambiente

        # posição inicial = entrada do mapa
        self.i, self.j = self.env.entrada

        # direção inicial (por padrão "Norte")
        self.dir = direcao_inicial

        # contadores
        self.passos = 0
        self.comidas_coletadas = 0
        self.comidas_alvo = self.env.total_comidas

    # === SENSORES ===
    def getSensor(self):
        """
        Retorna a matriz 3x3 ao redor do agente.
        O centro da matriz (posição [2][2]) mostra a direção do agente.
        """
        return self.env.get_sensor(self.i, self.j, self.dir)

    # === ATUADORES ===
    def setDirection(self, nova_dir: str):
        """Muda a direção do agente."""
        if nova_dir in DIRECOES:
            self.dir = nova_dir

    def move(self):
        """
        Move o agente na direção atual, se não houver parede.
        Conta passos (-1 ponto) e comida coletada (+10 pontos).
        """
        di, dj = DIRECOES[self.dir]
        ni, nj = self.i + di, self.j + dj

        # só anda se não for parede
        if self.env.celula(ni, nj) != 'X':
            self.i, self.j = ni, nj
            self.passos += 1

            # tenta coletar comida
            if self.env.coletar_se_comida(self.i, self.j):
                self.comidas_coletadas += 1
            return True
        return False

    # === ESTADO DO AGENTE ===
    def terminou(self) -> bool:
        """
        O agente terminou quando:
        - Pegou todas as comidas
        - E está em uma saída
        """
        em_saida = (self.i, self.j) in self.env.saidas
        return self.comidas_coletadas >= self.comidas_alvo and em_saida

    def pontuacao(self) -> int:
        """Calcula pontuação final (10 por comida, -1 por passo)."""
        return self.comidas_coletadas * 10 - self.passos
