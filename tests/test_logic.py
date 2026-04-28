"""
Testes unitários para a classe Board (src/logic.py).

Cobre os cenários obrigatórios:
    - Vitória em linha (horizontal)
    - Vitória em coluna (vertical)
    - Vitória em diagonal (principal e secundária)
    - Empate completo (tabuleiro cheio sem vencedor)
    - Tentativa de jogada em célula já ocupada
    - Validações adicionais de borda e estado
"""

import sys
import os

# Garante que o pacote src seja encontrado independentemente de como o pytest é invocado
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from logic import Board


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def tabuleiro() -> Board:
    """
    Fornece uma instância limpa de Board para cada teste.

    Yields:
        Board: Tabuleiro novo com todas as células vazias.
    """
    return Board()


@pytest.fixture
def tabuleiro_vitoria_linha(tabuleiro: Board) -> Board:
    """
    Tabuleiro pré-configurado com 'X' vencendo na primeira linha.

    Estado:
        X | X | X
        O | O | .
        . | . | .

    Args:
        tabuleiro (Board): Fixture base com tabuleiro vazio.

    Returns:
        Board: Tabuleiro com vitória de 'X' na linha 0.
    """
    tabuleiro.make_move(0, 0, "X")
    tabuleiro.make_move(1, 0, "O")
    tabuleiro.make_move(0, 1, "X")
    tabuleiro.make_move(1, 1, "O")
    tabuleiro.make_move(0, 2, "X")  # <- vitória de X
    return tabuleiro


@pytest.fixture
def tabuleiro_vitoria_coluna(tabuleiro: Board) -> Board:
    """
    Tabuleiro pré-configurado com 'O' vencendo na segunda coluna.

    Estado:
        X | O | .
        X | O | .
        . | O | .

    Args:
        tabuleiro (Board): Fixture base com tabuleiro vazio.

    Returns:
        Board: Tabuleiro com vitória de 'O' na coluna 1.
    """
    tabuleiro.make_move(0, 0, "X")
    tabuleiro.make_move(0, 1, "O")
    tabuleiro.make_move(1, 0, "X")
    tabuleiro.make_move(1, 1, "O")
    tabuleiro.make_move(2, 2, "X")  # jogada neutra
    tabuleiro.make_move(2, 1, "O")  # <- vitória de O
    return tabuleiro


@pytest.fixture
def tabuleiro_vitoria_diagonal_principal(tabuleiro: Board) -> Board:
    """
    Tabuleiro pré-configurado com 'X' vencendo na diagonal principal (↘).

    Estado:
        X | O | O
        . | X | .
        . | . | X

    Args:
        tabuleiro (Board): Fixture base com tabuleiro vazio.

    Returns:
        Board: Tabuleiro com vitória de 'X' na diagonal (0,0)→(1,1)→(2,2).
    """
    tabuleiro.make_move(0, 0, "X")
    tabuleiro.make_move(0, 1, "O")
    tabuleiro.make_move(1, 1, "X")
    tabuleiro.make_move(0, 2, "O")
    tabuleiro.make_move(2, 2, "X")  # <- vitória de X
    return tabuleiro


@pytest.fixture
def tabuleiro_vitoria_diagonal_secundaria(tabuleiro: Board) -> Board:
    """
    Tabuleiro pré-configurado com 'O' vencendo na diagonal secundária (↙).

    Estado:
        X | X | O
        X | O | .
        O | . | .

    Args:
        tabuleiro (Board): Fixture base com tabuleiro vazio.

    Returns:
        Board: Tabuleiro com vitória de 'O' na diagonal (0,2)→(1,1)→(2,0).
    """
    tabuleiro.make_move(0, 0, "X")
    tabuleiro.make_move(0, 2, "O")
    tabuleiro.make_move(0, 1, "X")
    tabuleiro.make_move(1, 1, "O")
    tabuleiro.make_move(1, 0, "X")
    tabuleiro.make_move(2, 0, "O")  # <- vitória de O
    return tabuleiro


@pytest.fixture
def tabuleiro_empate(tabuleiro: Board) -> Board:
    """
    Tabuleiro pré-configurado em empate (todas as células preenchidas, sem vencedor).

    Estado final:
        X | O | X
        X | O | O
        O | X | X

    Args:
        tabuleiro (Board): Fixture base com tabuleiro vazio.

    Returns:
        Board: Tabuleiro completamente preenchido sem vencedor.
    """
    # Sequência que preenche o tabuleiro sem produzir vencedor
    jogadas = [
        (0, 0, "X"), (0, 1, "O"), (0, 2, "X"),
        (1, 0, "X"), (1, 1, "O"), (1, 2, "O"),
        (2, 0, "O"), (2, 1, "X"), (2, 2, "X"),
    ]
    for linha, coluna, jogador in jogadas:
        tabuleiro.make_move(linha, coluna, jogador)
    return tabuleiro


# ===========================================================================
# Testes — Estado inicial
# ===========================================================================


class TestEstadoInicial:
    """Verifica as condições do tabuleiro recém-criado."""

    def test_grade_inicia_vazia(self, tabuleiro: Board) -> None:
        """Todas as 9 células devem ser None após a inicialização."""
        grade = tabuleiro.get_grade()
        for lin in range(3):
            for col in range(3):
                assert grade[lin][col] is None, (
                    f"Célula ({lin},{col}) deveria ser None, mas é {grade[lin][col]!r}"
                )

    def test_sem_vencedor_inicial(self, tabuleiro: Board) -> None:
        """check_winner deve retornar None em um tabuleiro vazio."""
        assert tabuleiro.check_winner() is None

    def test_nao_esta_cheio_inicialmente(self, tabuleiro: Board) -> None:
        """is_full deve retornar False em um tabuleiro vazio."""
        assert tabuleiro.is_full() is False


# ===========================================================================
# Testes — make_move
# ===========================================================================


class TestMakeMove:
    """Testa o registro e a validação de jogadas."""

    def test_jogada_valida_retorna_true(self, tabuleiro: Board) -> None:
        """Uma jogada em célula vazia dentro dos limites deve retornar True."""
        assert tabuleiro.make_move(1, 1, "X") is True

    def test_jogada_valida_atualiza_grade(self, tabuleiro: Board) -> None:
        """Após uma jogada válida, a célula correspondente deve conter o símbolo."""
        tabuleiro.make_move(0, 0, "X")
        assert tabuleiro.get_grade()[0][0] == "X"

    def test_jogada_em_celula_ocupada_retorna_false(self, tabuleiro: Board) -> None:
        """Tentar jogar em uma célula já ocupada deve retornar False."""
        tabuleiro.make_move(0, 0, "X")
        resultado = tabuleiro.make_move(0, 0, "O")
        assert resultado is False

    def test_celula_ocupada_nao_e_sobrescrita(self, tabuleiro: Board) -> None:
        """A célula ocupada não deve ser alterada após tentativa inválida."""
        tabuleiro.make_move(2, 2, "X")
        tabuleiro.make_move(2, 2, "O")  # deve falhar silenciosamente
        assert tabuleiro.get_grade()[2][2] == "X"

    @pytest.mark.parametrize("linha,coluna", [
        (-1, 0), (3, 0), (0, -1), (0, 3), (-1, -1), (3, 3),
    ])
    def test_jogada_fora_dos_limites_retorna_false(
        self, tabuleiro: Board, linha: int, coluna: int
    ) -> None:
        """Jogadas com índices fora do intervalo [0, 2] devem retornar False."""
        assert tabuleiro.make_move(linha, coluna, "X") is False


# ===========================================================================
# Testes — Vitória em linha (horizontal)
# ===========================================================================


class TestVitoriaLinha:
    """Cenários de vitória por preenchimento completo de uma linha."""

    def test_vitoria_linha_detecta_vencedor(
        self, tabuleiro_vitoria_linha: Board
    ) -> None:
        """check_winner deve retornar 'X' quando a linha 0 estiver completa."""
        assert tabuleiro_vitoria_linha.check_winner() == "X"

    @pytest.mark.parametrize("linha", [0, 1, 2])
    def test_vitoria_em_todas_as_linhas(self, tabuleiro: Board, linha: int) -> None:
        """'X' deve ser detectado como vencedor para qualquer linha completa."""
        for col in range(3):
            tabuleiro.make_move(linha, col, "X")
        assert tabuleiro.check_winner() == "X"

    def test_linha_parcial_nao_e_vitoria(self, tabuleiro: Board) -> None:
        """Duas marcas em linha não constituem vitória."""
        tabuleiro.make_move(0, 0, "X")
        tabuleiro.make_move(0, 1, "X")
        assert tabuleiro.check_winner() is None


# ===========================================================================
# Testes — Vitória em coluna (vertical)
# ===========================================================================


class TestVitoriaColuna:
    """Cenários de vitória por preenchimento completo de uma coluna."""

    def test_vitoria_coluna_detecta_vencedor(
        self, tabuleiro_vitoria_coluna: Board
    ) -> None:
        """check_winner deve retornar 'O' quando a coluna 1 estiver completa."""
        assert tabuleiro_vitoria_coluna.check_winner() == "O"

    @pytest.mark.parametrize("coluna", [0, 1, 2])
    def test_vitoria_em_todas_as_colunas(self, tabuleiro: Board, coluna: int) -> None:
        """'O' deve ser detectado como vencedor para qualquer coluna completa."""
        for lin in range(3):
            tabuleiro.make_move(lin, coluna, "O")
        assert tabuleiro.check_winner() == "O"


# ===========================================================================
# Testes — Vitória em diagonal
# ===========================================================================


class TestVitoriaDiagonal:
    """Cenários de vitória pelas diagonais principal e secundária."""

    def test_vitoria_diagonal_principal(
        self, tabuleiro_vitoria_diagonal_principal: Board
    ) -> None:
        """check_winner deve retornar 'X' na diagonal (0,0)→(1,1)→(2,2)."""
        assert tabuleiro_vitoria_diagonal_principal.check_winner() == "X"

    def test_vitoria_diagonal_secundaria(
        self, tabuleiro_vitoria_diagonal_secundaria: Board
    ) -> None:
        """check_winner deve retornar 'O' na diagonal (0,2)→(1,1)→(2,0)."""
        assert tabuleiro_vitoria_diagonal_secundaria.check_winner() == "O"


# ===========================================================================
# Testes — Empate
# ===========================================================================


class TestEmpate:
    """Cenários de empate (tabuleiro cheio sem vencedor)."""

    def test_tabuleiro_cheio_is_full(self, tabuleiro_empate: Board) -> None:
        """is_full deve retornar True quando todas as células estão preenchidas."""
        assert tabuleiro_empate.is_full() is True

    def test_empate_sem_vencedor(self, tabuleiro_empate: Board) -> None:
        """check_winner deve retornar None em um empate."""
        assert tabuleiro_empate.check_winner() is None

    def test_tabuleiro_parcial_nao_e_cheio(self, tabuleiro: Board) -> None:
        """is_full deve retornar False enquanto houver células vazias."""
        tabuleiro.make_move(0, 0, "X")
        assert tabuleiro.is_full() is False


# ===========================================================================
# Testes — reset
# ===========================================================================


class TestReset:
    """Verifica o comportamento do método reset."""

    def test_reset_limpa_tabuleiro(self, tabuleiro: Board) -> None:
        """Após reset, todas as células devem ser None novamente."""
        tabuleiro.make_move(0, 0, "X")
        tabuleiro.make_move(1, 1, "O")
        tabuleiro.reset()

        grade = tabuleiro.get_grade()
        for lin in range(3):
            for col in range(3):
                assert grade[lin][col] is None

    def test_reset_remove_vencedor(
        self, tabuleiro_vitoria_linha: Board
    ) -> None:
        """Após reset, check_winner deve retornar None."""
        assert tabuleiro_vitoria_linha.check_winner() == "X"
        tabuleiro_vitoria_linha.reset()
        assert tabuleiro_vitoria_linha.check_winner() is None

    def test_reset_permite_novas_jogadas(self, tabuleiro: Board) -> None:
        """Após reset, novas jogadas nas mesmas posições devem ser aceitas."""
        tabuleiro.make_move(0, 0, "X")
        tabuleiro.reset()
        assert tabuleiro.make_move(0, 0, "O") is True


# ===========================================================================
# Testes — get_grade (imutabilidade)
# ===========================================================================


class TestGetGrade:
    """Verifica que get_grade retorna uma cópia independente da grade interna."""

    def test_get_grade_retorna_copia(self, tabuleiro: Board) -> None:
        """Modificar a grade retornada não deve alterar o estado interno."""
        grade_externa = tabuleiro.get_grade()
        grade_externa[0][0] = "X"
        assert tabuleiro.get_grade()[0][0] is None
