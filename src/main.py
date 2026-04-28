"""
Ponto de entrada do Jogo da Velha MVP.

Integra a lógica do tabuleiro (logic.py) com a persistência de dados
(database.py) e renderiza a interface gráfica via Pygame.

Funcionalidades:
    - Janela 600×600 com grade 3×3 interativa
    - Alternância automática de turnos entre 'X' e 'O'
    - Detecção de vitória e empate com exibição de mensagem
    - Persistência única do resultado via flag `resultado_gravado`
    - Tecla R para reiniciar a partida
    - Tecla Q / fechar janela para encerrar o jogo
"""

from __future__ import annotations

import sys
import os

# Garante que os módulos do pacote src sejam encontrados ao executar
# diretamente (python src/main.py) ou a partir da raiz do projeto.
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import pygame

from logic import Board
from database import salvar_resultado

# ---------------------------------------------------------------------------
# Constantes de layout e paleta de cores
# ---------------------------------------------------------------------------

LARGURA = 600
ALTURA = 600
TAMANHO_CELULA = LARGURA // 3          # 200 px por célula
ESPESSURA_LINHA = 6
MARGEM_SIMBOLO = 30                    # distância mínima do símbolo à borda da célula
RAIO_CIRCULO = (TAMANHO_CELULA // 2) - MARGEM_SIMBOLO
ESPESSURA_SIMBOLO = 10

FPS = 60

# Paleta
COR_FUNDO          = (15,  17,  26)    # quase preto azulado
COR_GRADE          = (50,  55,  80)    # cinza-azulado
COR_X              = (94, 196, 255)    # azul ciano
COR_O              = (255, 110, 120)   # rosa-coral
COR_VITORIA_LINHA  = (255, 215,   0)   # dourado
COR_TEXTO          = (230, 230, 245)
COR_TEXTO_STATUS   = (160, 165, 190)
COR_OVERLAY        = (15,  17,  26, 200)   # fundo semi-transparente do overlay

FONTE_STATUS_TAM   = 30
FONTE_OVERLAY_TAM  = 52
FONTE_HINT_TAM     = 22

TITULO_JANELA = "Jogo da Velha — MVP"


# ---------------------------------------------------------------------------
# Inicialização
# ---------------------------------------------------------------------------

def inicializar_pygame() -> tuple[pygame.Surface, pygame.time.Clock]:
    """
    Inicializa o Pygame, cria a janela e o relógio de FPS.

    Returns:
        tuple: (Surface da janela, Clock do Pygame)
    """
    pygame.init()
    pygame.display.set_caption(TITULO_JANELA)
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    relogio = pygame.time.Clock()
    return tela, relogio


def carregar_fontes() -> dict[str, pygame.font.Font]:
    """
    Carrega as fontes utilizadas na interface.

    Returns:
        dict: Mapeamento nome → objeto Font.
    """
    pygame.font.init()
    return {
        "status":  pygame.font.SysFont("segoeui", FONTE_STATUS_TAM,  bold=True),
        "overlay": pygame.font.SysFont("segoeui", FONTE_OVERLAY_TAM, bold=True),
        "hint":    pygame.font.SysFont("segoeui", FONTE_HINT_TAM),
    }


# ---------------------------------------------------------------------------
# Desenho
# ---------------------------------------------------------------------------

def desenhar_fundo(tela: pygame.Surface) -> None:
    """Preenche o fundo com a cor base."""
    tela.fill(COR_FUNDO)


def desenhar_grade(tela: pygame.Surface) -> None:
    """
    Desenha as linhas horizontais e verticais que formam a grade 3×3.

    Args:
        tela (pygame.Surface): Superfície de renderização.
    """
    for i in range(1, 3):
        # Linhas horizontais
        pygame.draw.line(
            tela, COR_GRADE,
            (0,       i * TAMANHO_CELULA),
            (LARGURA, i * TAMANHO_CELULA),
            ESPESSURA_LINHA,
        )
        # Linhas verticais
        pygame.draw.line(
            tela, COR_GRADE,
            (i * TAMANHO_CELULA, 0),
            (i * TAMANHO_CELULA, ALTURA),
            ESPESSURA_LINHA,
        )


def _centro_celula(lin: int, col: int) -> tuple[int, int]:
    """
    Calcula as coordenadas do centro de uma célula na tela.

    Args:
        lin (int): Índice da linha (0–2).
        col (int): Índice da coluna (0–2).

    Returns:
        tuple[int, int]: (x, y) em pixels.
    """
    cx = col * TAMANHO_CELULA + TAMANHO_CELULA // 2
    cy = lin * TAMANHO_CELULA + TAMANHO_CELULA // 2
    return cx, cy


def desenhar_x(tela: pygame.Surface, lin: int, col: int) -> None:
    """
    Renderiza o símbolo 'X' centralizado na célula indicada.

    Args:
        tela (pygame.Surface): Superfície de renderização.
        lin (int): Linha da célula.
        col (int): Coluna da célula.
    """
    cx, cy = _centro_celula(lin, col)
    offset = RAIO_CIRCULO

    pygame.draw.line(
        tela, COR_X,
        (cx - offset, cy - offset),
        (cx + offset, cy + offset),
        ESPESSURA_SIMBOLO,
    )
    pygame.draw.line(
        tela, COR_X,
        (cx + offset, cy - offset),
        (cx - offset, cy + offset),
        ESPESSURA_SIMBOLO,
    )


def desenhar_o(tela: pygame.Surface, lin: int, col: int) -> None:
    """
    Renderiza o símbolo 'O' centralizado na célula indicada.

    Args:
        tela (pygame.Surface): Superfície de renderização.
        lin (int): Linha da célula.
        col (int): Coluna da célula.
    """
    cx, cy = _centro_celula(lin, col)
    pygame.draw.circle(tela, COR_O, (cx, cy), RAIO_CIRCULO, ESPESSURA_SIMBOLO)


def desenhar_simbolos(tela: pygame.Surface, grade: list[list]) -> None:
    """
    Percorre a grade e desenha o símbolo correspondente em cada célula preenchida.

    Args:
        tela (pygame.Surface): Superfície de renderização.
        grade (list[list]): Matriz 3×3 retornada por Board.get_grade().
    """
    for lin in range(3):
        for col in range(3):
            valor = grade[lin][col]
            if valor == "X":
                desenhar_x(tela, lin, col)
            elif valor == "O":
                desenhar_o(tela, lin, col)


def destacar_combinacao(
    tela: pygame.Surface,
    combinacao: list[tuple[int, int]],
) -> None:
    """
    Desenha uma linha dourada sobre as três células vencedoras.

    Args:
        tela (pygame.Surface): Superfície de renderização.
        combinacao (list[tuple[int, int]]): Lista de (linha, coluna) vencedores.
    """
    inicio = _centro_celula(*combinacao[0])
    fim    = _centro_celula(*combinacao[2])
    pygame.draw.line(tela, COR_VITORIA_LINHA, inicio, fim, ESPESSURA_SIMBOLO + 2)


def desenhar_overlay(
    tela: pygame.Surface,
    fontes: dict[str, pygame.font.Font],
    mensagem: str,
) -> None:
    """
    Exibe um painel semi-transparente com a mensagem de fim de partida.

    Args:
        tela (pygame.Surface): Superfície de renderização.
        fontes (dict): Dicionário de fontes.
        mensagem (str): Texto a exibir (ex.: "X Venceu!" ou "Empate!").
    """
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill(COR_OVERLAY)
    tela.blit(overlay, (0, 0))

    # Mensagem principal
    surf_msg = fontes["overlay"].render(mensagem, True, COR_TEXTO)
    rect_msg = surf_msg.get_rect(center=(LARGURA // 2, ALTURA // 2 - 20))
    tela.blit(surf_msg, rect_msg)

    # Dica de reinício
    surf_hint = fontes["hint"].render("Pressione R para jogar novamente", True, COR_TEXTO_STATUS)
    rect_hint = surf_hint.get_rect(center=(LARGURA // 2, ALTURA // 2 + 45))
    tela.blit(surf_hint, rect_hint)


def desenhar_status(
    tela: pygame.Surface,
    fontes: dict[str, pygame.font.Font],
    jogador_atual: str,
    jogo_encerrado: bool,
) -> None:
    """
    Exibe o turno atual no topo da tela quando o jogo ainda está em curso.

    Args:
        tela (pygame.Surface): Superfície de renderização.
        fontes (dict): Dicionário de fontes.
        jogador_atual (str): Símbolo do jogador ('X' ou 'O').
        jogo_encerrado (bool): Se True, não exibe a barra de status.
    """
    if jogo_encerrado:
        return

    cor = COR_X if jogador_atual == "X" else COR_O
    texto = f"Vez de: {jogador_atual}"
    surf = fontes["status"].render(texto, True, cor)
    # Posicionado no centro superior, com pequeno padding
    rect = surf.get_rect(midtop=(LARGURA // 2, 8))
    tela.blit(surf, rect)


# ---------------------------------------------------------------------------
# Lógica de jogo — utilidades
# ---------------------------------------------------------------------------

def posicao_para_celula(x: int, y: int) -> tuple[int, int]:
    """
    Converte coordenadas de pixel para índices de célula (linha, coluna).

    Args:
        x (int): Coordenada horizontal do clique.
        y (int): Coordenada vertical do clique.

    Returns:
        tuple[int, int]: (linha, coluna) correspondentes.
    """
    col = x // TAMANHO_CELULA
    lin = y // TAMANHO_CELULA
    return lin, col


def encontrar_combinacao_vitoria(
    grade: list[list],
    vencedor: str,
) -> list[tuple[int, int]] | None:
    """
    Encontra a combinação de células responsável pela vitória.

    Args:
        grade (list[list]): Matriz 3×3 com o estado atual.
        vencedor (str): Símbolo do vencedor ('X' ou 'O').

    Returns:
        list[tuple[int, int]] | None: Lista de (linha, coluna) ou None.
    """
    combinacoes = [
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)],
    ]
    for combo in combinacoes:
        if all(grade[l][c] == vencedor for l, c in combo):
            return combo
    return None


def reiniciar_partida(tabuleiro: Board) -> tuple[str, bool, bool, int]:
    """
    Reinicia o estado da partida sem recriar o tabuleiro.

    Args:
        tabuleiro (Board): Instância do tabuleiro a reiniciar.

    Returns:
        tuple: (jogador_atual, jogo_encerrado, resultado_gravado, total_jogadas)
    """
    tabuleiro.reset()
    return "X", False, False, 0


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Ponto de entrada do jogo.

    Inicializa o Pygame, cria o tabuleiro e executa o loop principal de eventos.
    """
    tela, relogio = inicializar_pygame()
    fontes = carregar_fontes()
    tabuleiro = Board()

    jogador_atual: str              = "X"
    jogo_encerrado: bool            = False
    resultado_gravado: bool         = False   # garante persistência única por partida
    total_jogadas: int              = 0
    mensagem_fim: str               = ""
    combinacao_vitoria: list | None = None

    executando = True
    while executando:
        # ── Eventos ─────────────────────────────────────────────────────────
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_q, pygame.K_ESCAPE):
                    executando = False
                elif evento.key == pygame.K_r:
                    jogador_atual, jogo_encerrado, resultado_gravado, total_jogadas = (
                        reiniciar_partida(tabuleiro)
                    )
                    mensagem_fim      = ""
                    combinacao_vitoria = None

            elif evento.type == pygame.MOUSEBUTTONDOWN and not jogo_encerrado:
                if evento.button == 1:  # botão esquerdo
                    mx, my = evento.pos
                    lin, col = posicao_para_celula(mx, my)

                    if tabuleiro.make_move(lin, col, jogador_atual):
                        total_jogadas += 1
                        grade = tabuleiro.get_grade()

                        # Verifica vitória
                        vencedor = tabuleiro.check_winner()
                        if vencedor:
                            jogo_encerrado    = True
                            mensagem_fim      = f"{vencedor} Venceu!"
                            combinacao_vitoria = encontrar_combinacao_vitoria(grade, vencedor)

                        # Verifica empate
                        elif tabuleiro.is_full():
                            jogo_encerrado = True
                            mensagem_fim   = "Empate!"
                            vencedor       = "Empate"

                        # Persiste resultado uma única vez
                        if jogo_encerrado and not resultado_gravado:
                            try:
                                salvar_resultado(
                                    vencedor=vencedor if vencedor != "Empate" else "Empate",
                                    jogadas=total_jogadas,
                                )
                                resultado_gravado = True
                            except Exception as erro:
                                print(f"[AVISO] Não foi possível salvar o resultado: {erro}")

                        # Alterna jogador
                        if not jogo_encerrado:
                            jogador_atual = "O" if jogador_atual == "X" else "X"

        # ── Renderização ─────────────────────────────────────────────────────
        desenhar_fundo(tela)
        desenhar_grade(tela)
        desenhar_simbolos(tela, tabuleiro.get_grade())

        if combinacao_vitoria:
            destacar_combinacao(tela, combinacao_vitoria)

        desenhar_status(tela, fontes, jogador_atual, jogo_encerrado)

        if jogo_encerrado:
            desenhar_overlay(tela, fontes, mensagem_fim)

        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
