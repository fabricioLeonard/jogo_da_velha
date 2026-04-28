"""
Módulo de lógica do Jogo da Velha.

Contém a classe Board, responsável por gerenciar o estado do tabuleiro,
validar jogadas e verificar condições de vitória ou empate.
"""

from typing import Optional


# Tipo para representar um jogador ('X', 'O') ou célula vazia (None)
Jogador = Optional[str]

# Tipo para representar o tabuleiro: lista 3x3 de Jogador
Tabuleiro = list[list[Jogador]]


class Board:
    """
    Representa o tabuleiro do Jogo da Velha (3x3).

    Gerencia o estado interno do jogo, valida jogadas e verifica
    condições de vitória ou empate. Completamente isolada de
    qualquer biblioteca gráfica.

    Atributos:
        _grade (Tabuleiro): Matriz 3x3 que armazena o estado de cada célula.
            Cada célula pode conter 'X', 'O' ou None (vazia).
    """

    # Linhas, colunas e diagonais que constituem vitória
    _COMBINACOES_VITORIA: list[list[tuple[int, int]]] = [
        # Linhas
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        # Colunas
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        # Diagonais
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]

    def __init__(self) -> None:
        """
        Inicializa o tabuleiro com todas as células vazias (None).

        A grade interna é uma matriz 3x3 onde cada posição começa
        sem nenhum jogador marcado.
        """
        self._grade: Tabuleiro = self._criar_grade_vazia()

    # ------------------------------------------------------------------
    # Métodos públicos
    # ------------------------------------------------------------------

    def make_move(self, linha: int, coluna: int, jogador: str) -> bool:
        """
        Registra a jogada de um jogador em uma posição do tabuleiro.

        Valida se a posição está dentro dos limites (0–2) e se a
        célula ainda não foi ocupada. Caso as validações passem,
        marca a célula com o símbolo do jogador e retorna True.

        Args:
            linha (int): Índice da linha (deve ser 0, 1 ou 2).
            coluna (int): Índice da coluna (deve ser 0, 1 ou 2).
            jogador (str): Símbolo do jogador ('X' ou 'O').

        Returns:
            bool: True se a jogada foi realizada com sucesso,
                  False se a posição for inválida ou já estiver ocupada.
        """
        if not self._posicao_valida(linha, coluna):
            return False

        if self._grade[linha][coluna] is not None:
            return False

        self._grade[linha][coluna] = jogador
        return True

    def check_winner(self) -> Optional[str]:
        """
        Verifica se existe um vencedor no estado atual do tabuleiro.

        Percorre todas as combinações de vitória possíveis (linhas,
        colunas e diagonais). Retorna o símbolo do vencedor assim
        que uma combinação completa for encontrada.

        Returns:
            Optional[str]: O símbolo do vencedor ('X' ou 'O') se houver
                           um, ou None caso o jogo ainda não tenha terminado.
        """
        for combinacao in self._COMBINACOES_VITORIA:
            valores = [self._grade[lin][col] for lin, col in combinacao]
            primeiro = valores[0]
            if primeiro is not None and all(v == primeiro for v in valores):
                return primeiro

        return None

    def is_full(self) -> bool:
        """
        Verifica se o tabuleiro está completamente preenchido.

        Um tabuleiro cheio (sem vencedor) representa um empate.

        Returns:
            bool: True se não houver nenhuma célula vazia, False caso contrário.
        """
        return all(
            self._grade[lin][col] is not None
            for lin in range(3)
            for col in range(3)
        )

    def reset(self) -> None:
        """
        Reinicia o tabuleiro para o estado inicial.

        Todas as células voltam a ser None, permitindo o início de
        uma nova partida sem necessidade de criar uma nova instância.
        """
        self._grade = self._criar_grade_vazia()

    def get_grade(self) -> Tabuleiro:
        """
        Retorna uma cópia do estado atual do tabuleiro.

        Fornece acesso somente-leitura à grade interna para exibição
        ou lógica externa, sem expor a referência direta ao atributo privado.

        Returns:
            Tabuleiro: Cópia da matriz 3x3 com o estado atual de cada célula.
        """
        return [linha[:] for linha in self._grade]

    # ------------------------------------------------------------------
    # Métodos privados auxiliares
    # ------------------------------------------------------------------

    @staticmethod
    def _criar_grade_vazia() -> Tabuleiro:
        """
        Cria e retorna uma grade 3x3 com todas as células vazias (None).

        Returns:
            Tabuleiro: Nova matriz 3x3 preenchida com None.
        """
        return [[None, None, None] for _ in range(3)]

    @staticmethod
    def _posicao_valida(linha: int, coluna: int) -> bool:
        """
        Verifica se os índices de linha e coluna estão dentro dos limites.

        Args:
            linha (int): Índice da linha a verificar.
            coluna (int): Índice da coluna a verificar.

        Returns:
            bool: True se ambos os índices estiverem no intervalo [0, 2].
        """
        return 0 <= linha <= 2 and 0 <= coluna <= 2

    def __repr__(self) -> str:
        """
        Retorna uma representação textual do tabuleiro para depuração.

        Returns:
            str: Grade formatada com os valores de cada célula.
        """
        linhas = []
        for linha in self._grade:
            celulas = [v if v is not None else "." for v in linha]
            linhas.append(" | ".join(celulas))
        separador = "\n---------\n"
        return separador.join(linhas)
