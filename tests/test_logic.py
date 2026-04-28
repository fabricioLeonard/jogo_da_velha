"""
Testes unitários para a classe Board (src/logic.py).

Cenários obrigatórios cobertos:
    - Vitória em linha (horizontal)
    - Vitória em diagonal (principal e secundária)
    - Empate completo (velha — tabuleiro cheio sem vencedor)
    - Tentativa de jogada em célula já ocupada

Todos os asserts validam também o estado interno da matriz (_grade),
não apenas os valores de retorno dos métodos públicos.
"""

from __future__ import annotations

import sys
import os

# Garante que src/ seja encontrado independentemente do diretório de invocação
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from logic import Board


# ===========================================================================
# Helpers de inspeção da matriz interna
# ===========================================================================


def _grade_interna(board: Board) -> list[list]:
    """
    Acessa diretamente o atributo _grade para validar o estado interno.

    Args:
        board (Board): Instância do tabuleiro.

    Returns:
        list[list]: Referência à matriz 3×3 interna.
    """
    return board._grade  # acesso intencional ao atributo privado para QA


def _celula(board: Board, lin: int, col: int):
    """Retorna o valor raw da célula (lin, col) da matriz interna."""
    return _grade_interna(board)[lin][col]


def _todas_celulas(board: Board) -> list:
    """Retorna a lista plana com os 9 valores da matriz interna."""
    grade = _grade_interna(board)
    return [grade[l][c] for l in range(3) for c in range(3)]


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def board() -> Board:
    """
    Fornece um tabuleiro limpo para cada teste.

    Returns:
        Board: Instância nova com todas as células None.
    """
    return Board()


@pytest.fixture
def board_vitoria_linha(board: Board) -> Board:
    """
    Tabuleiro com 'X' vencendo na primeira linha (horizontal).

    Estado interno resultante:
        [['X', 'X', 'X'],
         ['O', 'O', None],
         [None, None, None]]

    Returns:
        Board: Tabuleiro com vitória de 'X' na linha 0.
    """
    board.make_move(0, 0, "X")
    board.make_move(1, 0, "O")
    board.make_move(0, 1, "X")
    board.make_move(1, 1, "O")
    board.make_move(0, 2, "X")  # <- vitória de X
    return board


@pytest.fixture
def board_vitoria_diagonal_principal(board: Board) -> Board:
    """
    Tabuleiro com 'X' vencendo na diagonal principal (↘).

    Estado interno resultante:
        [['X', 'O', 'O'],
         [None, 'X', None],
         [None, None, 'X']]

    Returns:
        Board: Tabuleiro com vitória de 'X' em (0,0)→(1,1)→(2,2).
    """
    board.make_move(0, 0, "X")
    board.make_move(0, 1, "O")
    board.make_move(1, 1, "X")
    board.make_move(0, 2, "O")
    board.make_move(2, 2, "X")  # <- vitória de X
    return board


@pytest.fixture
def board_vitoria_diagonal_secundaria(board: Board) -> Board:
    """
    Tabuleiro com 'O' vencendo na diagonal secundária (↙).

    Estado interno resultante:
        [['X', 'X', 'O'],
         ['X', 'O', None],
         ['O', None, None]]

    Returns:
        Board: Tabuleiro com vitória de 'O' em (0,2)→(1,1)→(2,0).
    """
    board.make_move(0, 0, "X")
    board.make_move(0, 2, "O")
    board.make_move(0, 1, "X")
    board.make_move(1, 1, "O")
    board.make_move(1, 0, "X")
    board.make_move(2, 0, "O")  # <- vitória de O
    return board


@pytest.fixture
def board_velha(board: Board) -> Board:
    """
    Tabuleiro em empate completo (velha): todas as células preenchidas, sem vencedor.

    Estado interno resultante:
        [['X', 'O', 'X'],
         ['X', 'O', 'O'],
         ['O', 'X', 'X']]

    Returns:
        Board: Tabuleiro completamente preenchido sem vencedor.
    """
    jogadas = [
        (0, 0, "X"), (0, 1, "O"), (0, 2, "X"),
        (1, 0, "X"), (1, 1, "O"), (1, 2, "O"),
        (2, 0, "O"), (2, 1, "X"), (2, 2, "X"),
    ]
    for lin, col, jogador in jogadas:
        board.make_move(lin, col, jogador)
    return board


# ===========================================================================
# TestEstadoInicial — valida a matriz logo após __init__
# ===========================================================================


class TestEstadoInicial:
    """Verifica que a matriz interna é inicializada corretamente."""

    def test_matriz_3x3(self, board: Board) -> None:
        """A grade interna deve ser uma lista de 3 sublistas com 3 elementos cada."""
        grade = _grade_interna(board)
        assert len(grade) == 3, "A grade deve ter 3 linhas"
        for lin in grade:
            assert len(lin) == 3, f"Cada linha deve ter 3 colunas, encontrado: {len(lin)}"

    def test_todas_celulas_none(self, board: Board) -> None:
        """Todos os 9 valores da matriz devem ser None após a criação."""
        assert _todas_celulas(board) == [None] * 9

    def test_check_winner_none_inicial(self, board: Board) -> None:
        """Sem jogadas, check_winner deve retornar None."""
        assert board.check_winner() is None

    def test_is_full_false_inicial(self, board: Board) -> None:
        """Sem jogadas, is_full deve retornar False."""
        assert board.is_full() is False


# ===========================================================================
# TestMakeMove — valida o estado da matriz após jogadas
# ===========================================================================


class TestMakeMove:
    """Testa o registro de jogadas e a integridade da matriz interna."""

    def test_jogada_valida_retorna_true(self, board: Board) -> None:
        """make_move em célula vazia dentro dos limites deve retornar True."""
        assert board.make_move(1, 1, "X") is True

    def test_jogada_atualiza_celula_interna(self, board: Board) -> None:
        """Após make_move válido, a célula correspondente na _grade deve conter o símbolo."""
        board.make_move(0, 0, "X")
        assert _celula(board, 0, 0) == "X", (
            "A célula (0,0) na matriz interna deve ser 'X' após a jogada"
        )

    def test_apenas_celula_alvo_e_alterada(self, board: Board) -> None:
        """Somente a célula jogada deve mudar; as demais devem permanecer None."""
        board.make_move(2, 1, "O")
        for lin in range(3):
            for col in range(3):
                if (lin, col) == (2, 1):
                    assert _celula(board, lin, col) == "O"
                else:
                    assert _celula(board, lin, col) is None, (
                        f"Célula ({lin},{col}) deveria ser None"
                    )

    # ------------------------------------------------------------------
    # Cenário obrigatório: Tentativa de jogada em célula ocupada
    # ------------------------------------------------------------------

    def test_celula_ocupada_retorna_false(self, board: Board) -> None:
        """Tentativa de jogada em célula já ocupada deve retornar False."""
        board.make_move(0, 0, "X")
        resultado = board.make_move(0, 0, "O")
        assert resultado is False

    def test_celula_ocupada_nao_sobrescreve_matriz(self, board: Board) -> None:
        """
        O valor interno da célula ocupada NÃO deve ser alterado após
        uma tentativa inválida de sobrescrita.
        """
        board.make_move(0, 0, "X")
        board.make_move(0, 0, "O")  # deve ser ignorado
        assert _celula(board, 0, 0) == "X", (
            "A célula (0,0) na _grade ainda deve conter 'X' — não 'O'"
        )

    def test_celula_ocupada_nao_altera_restante_da_matriz(self, board: Board) -> None:
        """Uma tentativa inválida não deve causar efeitos colaterais na matriz."""
        board.make_move(1, 1, "X")
        grade_antes = [row[:] for row in _grade_interna(board)]
        board.make_move(1, 1, "O")  # tentativa inválida
        grade_depois = _grade_interna(board)
        assert grade_antes == grade_depois, (
            "A matriz interna não deve mudar após uma jogada inválida"
        )

    @pytest.mark.parametrize("lin,col", [
        (-1, 0), (3, 0), (0, -1), (0, 3), (-1, -1), (3, 3),
    ])
    def test_fora_dos_limites_retorna_false(
        self, board: Board, lin: int, col: int
    ) -> None:
        """Índices fora do intervalo [0, 2] devem retornar False sem alterar a matriz."""
        resultado = board.make_move(lin, col, "X")
        assert resultado is False
        assert _todas_celulas(board) == [None] * 9, (
            "A matriz interna não deve ser alterada por jogadas fora dos limites"
        )


# ===========================================================================
# TestVitoriaLinha — cenário obrigatório
# ===========================================================================


class TestVitoriaLinha:
    """Valida vitória horizontal e o estado da matriz correspondente."""

    def test_check_winner_retorna_x(self, board_vitoria_linha: Board) -> None:
        """check_winner deve retornar 'X' com a linha 0 completa."""
        assert board_vitoria_linha.check_winner() == "X"

    def test_estado_interno_linha_vencedora(self, board_vitoria_linha: Board) -> None:
        """As três células da linha 0 na _grade devem conter 'X'."""
        grade = _grade_interna(board_vitoria_linha)
        assert grade[0] == ["X", "X", "X"], (
            f"Linha 0 deveria ser ['X','X','X'], encontrado: {grade[0]}"
        )

    def test_celulas_oponente_intactas(self, board_vitoria_linha: Board) -> None:
        """As células de 'O' na linha 1 devem permanecer intactas."""
        grade = _grade_interna(board_vitoria_linha)
        assert grade[1][0] == "O"
        assert grade[1][1] == "O"

    @pytest.mark.parametrize("linha", [0, 1, 2])
    def test_vitoria_em_qualquer_linha(self, board: Board, linha: int) -> None:
        """Qualquer linha completamente preenchida com 'X' deve produzir vitória."""
        for col in range(3):
            board.make_move(linha, col, "X")
        # Valida retorno
        assert board.check_winner() == "X"
        # Valida estado interno
        grade = _grade_interna(board)
        assert grade[linha] == ["X", "X", "X"]

    def test_linha_incompleta_nao_e_vitoria(self, board: Board) -> None:
        """Duas marcas em linha não devem constituir vitória nem alterar outras células."""
        board.make_move(0, 0, "X")
        board.make_move(0, 1, "X")
        assert board.check_winner() is None
        assert _celula(board, 0, 2) is None


# ===========================================================================
# TestVitoriaDiagonal — cenário obrigatório
# ===========================================================================


class TestVitoriaDiagonal:
    """Valida vitória diagonal e o estado interno da matriz."""

    # ── Diagonal principal ──────────────────────────────────────────────────

    def test_diagonal_principal_check_winner(
        self, board_vitoria_diagonal_principal: Board
    ) -> None:
        """check_winner deve retornar 'X' para a diagonal (0,0)→(1,1)→(2,2)."""
        assert board_vitoria_diagonal_principal.check_winner() == "X"

    def test_diagonal_principal_estado_interno(
        self, board_vitoria_diagonal_principal: Board
    ) -> None:
        """As três células da diagonal principal na _grade devem conter 'X'."""
        grade = _grade_interna(board_vitoria_diagonal_principal)
        celulas_diagonal = [grade[i][i] for i in range(3)]
        assert celulas_diagonal == ["X", "X", "X"], (
            f"Diagonal principal deveria ser ['X','X','X'], encontrado: {celulas_diagonal}"
        )

    # ── Diagonal secundária ─────────────────────────────────────────────────

    def test_diagonal_secundaria_check_winner(
        self, board_vitoria_diagonal_secundaria: Board
    ) -> None:
        """check_winner deve retornar 'O' para a diagonal (0,2)→(1,1)→(2,0)."""
        assert board_vitoria_diagonal_secundaria.check_winner() == "O"

    def test_diagonal_secundaria_estado_interno(
        self, board_vitoria_diagonal_secundaria: Board
    ) -> None:
        """As três células da diagonal secundária na _grade devem conter 'O'."""
        grade = _grade_interna(board_vitoria_diagonal_secundaria)
        celulas_diagonal = [grade[i][2 - i] for i in range(3)]
        assert celulas_diagonal == ["O", "O", "O"], (
            f"Diagonal secundária deveria ser ['O','O','O'], encontrado: {celulas_diagonal}"
        )

    def test_diagonal_parcial_nao_e_vitoria(self, board: Board) -> None:
        """Duas marcas na diagonal não devem ser detectadas como vitória."""
        board.make_move(0, 0, "X")
        board.make_move(1, 1, "X")
        assert board.check_winner() is None
        assert _celula(board, 2, 2) is None


# ===========================================================================
# TestEmpate (velha) — cenário obrigatório
# ===========================================================================


class TestEmpate:
    """Valida o estado de empate completo (velha) na matriz interna."""

    # Estado esperado da matriz após empate:
    _GRADE_ESPERADA = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"],
    ]

    def test_is_full_true(self, board_velha: Board) -> None:
        """is_full deve retornar True quando todas as 9 células estão preenchidas."""
        assert board_velha.is_full() is True

    def test_nenhuma_celula_none(self, board_velha: Board) -> None:
        """Nenhuma célula da _grade deve ser None no empate."""
        assert None not in _todas_celulas(board_velha), (
            "Não deve haver células None em um tabuleiro completamente preenchido"
        )

    def test_estado_interno_completo(self, board_velha: Board) -> None:
        """A _grade completa deve corresponder exatamente ao estado esperado."""
        assert _grade_interna(board_velha) == self._GRADE_ESPERADA

    def test_check_winner_none_no_empate(self, board_velha: Board) -> None:
        """check_winner deve retornar None em um empate (nenhum vencedor)."""
        assert board_velha.check_winner() is None

    def test_tabuleiro_parcial_nao_e_cheio(self, board: Board) -> None:
        """is_full deve retornar False enquanto houver células None na _grade."""
        board.make_move(0, 0, "X")
        assert board.is_full() is False
        assert None in _todas_celulas(board)


# ===========================================================================
# TestReset — valida o estado da matriz após reset
# ===========================================================================


class TestReset:
    """Verifica que reset limpa completamente a matriz interna."""

    def test_reset_zera_todas_celulas(self, board: Board) -> None:
        """Após reset, todos os 9 valores da _grade devem ser None."""
        board.make_move(0, 0, "X")
        board.make_move(2, 2, "O")
        board.reset()
        assert _todas_celulas(board) == [None] * 9

    def test_reset_apos_vitoria_limpa_matriz(
        self, board_vitoria_linha: Board
    ) -> None:
        """Após reset de um tabuleiro vencedor, a _grade deve estar limpa."""
        board_vitoria_linha.reset()
        assert _todas_celulas(board_vitoria_linha) == [None] * 9
        assert board_vitoria_linha.check_winner() is None

    def test_reset_apos_empate_limpa_matriz(self, board_velha: Board) -> None:
        """Após reset de um empate, a _grade deve estar completamente limpa."""
        board_velha.reset()
        assert _todas_celulas(board_velha) == [None] * 9
        assert board_velha.is_full() is False

    def test_jogada_valida_apos_reset(self, board: Board) -> None:
        """Após reset, a mesma célula antes ocupada deve aceitar nova jogada."""
        board.make_move(1, 1, "X")
        board.reset()
        resultado = board.make_move(1, 1, "O")
        assert resultado is True
        assert _celula(board, 1, 1) == "O"


# ===========================================================================
# TestGetGrade — valida que a cópia não expõe a matriz interna
# ===========================================================================


class TestGetGrade:
    """Verifica que get_grade retorna uma cópia e não a referência da _grade."""

    def test_retorna_copia_independente(self, board: Board) -> None:
        """Modificar o retorno de get_grade não deve alterar a _grade interna."""
        copia = board.get_grade()
        copia[0][0] = "X"
        # A célula interna deve permanecer None
        assert _celula(board, 0, 0) is None, (
            "get_grade deve retornar cópia — modificá-la não pode afetar _grade"
        )

    def test_copia_reflete_estado_atual(self, board: Board) -> None:
        """O retorno de get_grade deve espelhar o estado atual da _grade."""
        board.make_move(2, 0, "O")
        copia = board.get_grade()
        assert copia[2][0] == "O"
        assert copia[2][0] == _celula(board, 2, 0)
