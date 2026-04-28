"""
Ponto de entrada do Jogo da Velha MVP.

Integra a lógica do tabuleiro (logic.py) com a persistência de dados
(database.py) e renderiza a interface gráfica via Pygame.

Funcionalidades:
    - Janela 600×600 com grade 3×3 interativa
    - Alternância automática de turnos entre 'X' e 'O'
    - Detecção de vitória e empate com overlay de fim de partida
    - Persistência única do resultado via flag `resultado_gravado`
    - Histórico completo de partidas exibido no terminal ao encerrar
    - Tecla R para reiniciar · Q / ESC / fechar janela para sair
"""

from __future__ import annotations

import sys
import os

# Garante que os módulos src/ sejam encontrados ao executar
# diretamente (python src/main.py) ou a partir da raiz do projeto.
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import pygame

from logic import Board
from database import salvar_resultado, listar_partidas

# ---------------------------------------------------------------------------
# Constantes de layout e paleta de cores
# ---------------------------------------------------------------------------

LARGURA        = 600
ALTURA         = 600
TAMANHO_CELULA = LARGURA // 3          # 200 px por célula
ESPESSURA_GRADE    = 6
ESPESSURA_SIMBOLO  = 10
MARGEM_SIMBOLO     = 30               # distância do símbolo à borda da célula
RAIO_CIRCULO       = (TAMANHO_CELULA // 2) - MARGEM_SIMBOLO

FPS = 60

# Paleta de cores
COR_FUNDO         = ( 15,  17,  26)   # azul-escuro quase preto
COR_GRADE         = ( 50,  55,  80)   # cinza-azulado
COR_X             = ( 94, 196, 255)   # ciano
COR_O             = (255, 110, 120)   # rosa-coral
COR_VITORIA       = (255, 215,   0)   # dourado
COR_TEXTO         = (230, 230, 245)   # branco-azulado
COR_SUBTEXTO      = (160, 165, 190)   # cinza claro
COR_OVERLAY       = ( 15,  17,  26, 210)

FONTE_STATUS_TAM  = 30
FONTE_OVERLAY_TAM = 52
FONTE_HINT_TAM    = 22

TITULO_JANELA = "Jogo da Velha — MVP"

# Separador visual para o terminal
_SEP = "─" * 52


# ---------------------------------------------------------------------------
# Inicialização do Pygame
# ---------------------------------------------------------------------------

def inicializar_pygame() -> tuple[pygame.Surface, pygame.time.Clock]:
    """
    Inicializa o Pygame e cria a janela principal.

    Returns:
        tuple: (Surface da janela, Clock de FPS)
    """
    pygame.init()
    pygame.display.set_caption(TITULO_JANELA)
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    relogio = pygame.time.Clock()
    return tela, relogio


def carregar_fontes() -> dict[str, pygame.font.Font]:
    """
    Carrega as fontes da interface.

    Returns:
        dict: Mapeamento nome → Font.
    """
    pygame.font.init()
    return {
        "status":  pygame.font.SysFont("segoeui", FONTE_STATUS_TAM,  bold=True),
        "overlay": pygame.font.SysFont("segoeui", FONTE_OVERLAY_TAM, bold=True),
        "hint":    pygame.font.SysFont("segoeui", FONTE_HINT_TAM),
    }


# ---------------------------------------------------------------------------
# Funções de desenho
# ---------------------------------------------------------------------------

def desenhar_fundo(tela: pygame.Surface) -> None:
    """Preenche o fundo com a cor base."""
    tela.fill(COR_FUNDO)


def desenhar_grade(tela: pygame.Surface) -> None:
    """
    Renderiza as 4 linhas da grade 3×3.

    Args:
        tela: Superfície de renderização.
    """
    for i in range(1, 3):
        pygame.draw.line(tela, COR_GRADE,
                         (0, i * TAMANHO_CELULA), (LARGURA, i * TAMANHO_CELULA),
                         ESPESSURA_GRADE)
        pygame.draw.line(tela, COR_GRADE,
                         (i * TAMANHO_CELULA, 0), (i * TAMANHO_CELULA, ALTURA),
                         ESPESSURA_GRADE)


def _centro(lin: int, col: int) -> tuple[int, int]:
    """Retorna as coordenadas (px) do centro da célula (lin, col)."""
    cx = col * TAMANHO_CELULA + TAMANHO_CELULA // 2
    cy = lin * TAMANHO_CELULA + TAMANHO_CELULA // 2
    return cx, cy


def desenhar_x(tela: pygame.Surface, lin: int, col: int) -> None:
    """Renderiza o símbolo X na célula indicada."""
    cx, cy = _centro(lin, col)
    off = RAIO_CIRCULO
    pygame.draw.line(tela, COR_X, (cx - off, cy - off), (cx + off, cy + off), ESPESSURA_SIMBOLO)
    pygame.draw.line(tela, COR_X, (cx + off, cy - off), (cx - off, cy + off), ESPESSURA_SIMBOLO)


def desenhar_o(tela: pygame.Surface, lin: int, col: int) -> None:
    """Renderiza o símbolo O na célula indicada."""
    cx, cy = _centro(lin, col)
    pygame.draw.circle(tela, COR_O, (cx, cy), RAIO_CIRCULO, ESPESSURA_SIMBOLO)


def desenhar_simbolos(tela: pygame.Surface, grade: list[list]) -> None:
    """
    Percorre a grade e renderiza X ou O em cada célula preenchida.

    Args:
        tela: Superfície de renderização.
        grade: Matriz 3×3 retornada por Board.get_grade().
    """
    for lin in range(3):
        for col in range(3):
            valor = grade[lin][col]
            if valor == "X":
                desenhar_x(tela, lin, col)
            elif valor == "O":
                desenhar_o(tela, lin, col)


def destacar_vitoria(
    tela: pygame.Surface,
    combinacao: list[tuple[int, int]],
) -> None:
    """
    Traça uma linha dourada sobre as células vencedoras.

    Args:
        tela: Superfície de renderização.
        combinacao: Lista de (lin, col) das 3 células vencedoras.
    """
    inicio = _centro(*combinacao[0])
    fim    = _centro(*combinacao[2])
    pygame.draw.line(tela, COR_VITORIA, inicio, fim, ESPESSURA_SIMBOLO + 2)


def desenhar_overlay(
    tela: pygame.Surface,
    fontes: dict[str, pygame.font.Font],
    mensagem: str,
) -> None:
    """
    Exibe painel semi-transparente com mensagem de fim de partida.

    Args:
        tela: Superfície de renderização.
        fontes: Dicionário de fontes.
        mensagem: Texto principal (ex.: "X Venceu!" ou "Empate!").
    """
    surf_ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    surf_ov.fill(COR_OVERLAY)
    tela.blit(surf_ov, (0, 0))

    surf_msg = fontes["overlay"].render(mensagem, True, COR_TEXTO)
    tela.blit(surf_msg, surf_msg.get_rect(center=(LARGURA // 2, ALTURA // 2 - 20)))

    surf_hint = fontes["hint"].render(
        "R = nova partida   |   Q = sair", True, COR_SUBTEXTO
    )
    tela.blit(surf_hint, surf_hint.get_rect(center=(LARGURA // 2, ALTURA // 2 + 45)))


def desenhar_status(
    tela: pygame.Surface,
    fontes: dict[str, pygame.font.Font],
    jogador_atual: str,
    jogo_encerrado: bool,
) -> None:
    """
    Exibe o turno atual no topo da tela (omitido quando o jogo termina).

    Args:
        tela: Superfície de renderização.
        fontes: Dicionário de fontes.
        jogador_atual: 'X' ou 'O'.
        jogo_encerrado: Suprime o status quando True.
    """
    if jogo_encerrado:
        return
    cor  = COR_X if jogador_atual == "X" else COR_O
    surf = fontes["status"].render(f"Vez de: {jogador_atual}", True, cor)
    tela.blit(surf, surf.get_rect(midtop=(LARGURA // 2, 8)))


# ---------------------------------------------------------------------------
# Utilitários de lógica de jogo
# ---------------------------------------------------------------------------

def pixel_para_celula(x: int, y: int) -> tuple[int, int]:
    """
    Converte coordenadas de pixel em (linha, coluna) da grade.

    Args:
        x: Posição horizontal do clique.
        y: Posição vertical do clique.

    Returns:
        tuple[int, int]: (linha, coluna).
    """
    return y // TAMANHO_CELULA, x // TAMANHO_CELULA


def achar_combinacao_vitoria(
    grade: list[list],
    vencedor: str,
) -> list[tuple[int, int]] | None:
    """
    Localiza as 3 células que formam a vitória de `vencedor`.

    Args:
        grade: Matriz 3×3 atual.
        vencedor: Símbolo do vencedor ('X' ou 'O').

    Returns:
        Lista de (lin, col) ou None.
    """
    combinacoes: list[list[tuple[int, int]]] = [
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)],
    ]
    for combo in combinacoes:
        if all(grade[l][c] == vencedor for l, c in combo):
            return combo
    return None


def reiniciar(tabuleiro: Board) -> tuple[str, bool, bool, int]:
    """
    Reseta o tabuleiro e devolve o estado inicial da partida.

    Returns:
        (jogador_atual, jogo_encerrado, resultado_gravado, total_jogadas)
    """
    tabuleiro.reset()
    return "X", False, False, 0


# ---------------------------------------------------------------------------
# Exibição do histórico no terminal
# ---------------------------------------------------------------------------

def exibir_historico_terminal() -> None:
    """
    Consulta o banco via listar_partidas() e imprime o histórico
    formatado no terminal no momento em que o jogo é encerrado.
    """
    print(f"\n{_SEP}")
    print("  📋  HISTÓRICO DE PARTIDAS")
    print(_SEP)

    try:
        partidas = listar_partidas()
    except Exception as erro:
        print(f"  [ERRO] Não foi possível carregar o histórico: {erro}")
        print(_SEP)
        return

    if not partidas:
        print("  Nenhuma partida registada ainda.")
        print(_SEP)
        return

    # Cabeçalho da tabela
    print(f"  {'#':<5} {'Data/Hora':<22} {'Vencedor':<12} {'Jogadas':>7}")
    print(f"  {'-'*4}  {'-'*20}  {'-'*10}  {'-'*6}")

    # Contadores para o resumo
    contagem: dict[str, int] = {}

    for idx, p in enumerate(partidas, start=1):
        data_str   = p.data_hora.strftime("%d/%m/%Y %H:%M:%S") if p.data_hora else "—"
        vencedor   = p.vencedor if p.vencedor else "—"
        contagem[vencedor] = contagem.get(vencedor, 0) + 1
        print(f"  {idx:<5} {data_str:<22} {vencedor:<12} {p.total_jogadas:>7}")

    # Resumo estatístico
    print(_SEP)
    print("  📊  RESUMO")
    print(_SEP)
    total = len(partidas)
    print(f"  Total de partidas : {total}")
    for jogador, qtd in sorted(contagem.items()):
        pct = (qtd / total) * 100
        label = "Vitórias de X" if jogador == "X" \
               else "Vitórias de O" if jogador == "O" \
               else "Empates        " if jogador == "Empate" \
               else f"Outras ({jogador})"
        print(f"  {label:<18}: {qtd}  ({pct:.1f}%)")
    print(f"{_SEP}\n")


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Ponto de entrada do jogo.

    Inicializa Pygame, cria o tabuleiro e executa o loop de eventos.
    Ao sair, imprime o histórico completo de partidas no terminal.
    """
    tela, relogio = inicializar_pygame()
    fontes        = carregar_fontes()
    tabuleiro     = Board()

    jogador_atual: str              = "X"
    jogo_encerrado: bool            = False
    resultado_gravado: bool         = False   # flag: salvar_resultado chamado 1× por partida
    total_jogadas: int              = 0
    mensagem_fim: str               = ""
    combinacao_vitoria: list | None = None

    executando = True
    while executando:

        # ── Eventos ──────────────────────────────────────────────────────────
        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                executando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_q, pygame.K_ESCAPE):
                    executando = False
                elif evento.key == pygame.K_r:
                    jogador_atual, jogo_encerrado, resultado_gravado, total_jogadas = (
                        reiniciar(tabuleiro)
                    )
                    mensagem_fim       = ""
                    combinacao_vitoria = None

            elif evento.type == pygame.MOUSEBUTTONDOWN and not jogo_encerrado:
                if evento.button == 1:
                    lin, col = pixel_para_celula(*evento.pos)

                    if tabuleiro.make_move(lin, col, jogador_atual):
                        total_jogadas += 1
                        grade = tabuleiro.get_grade()

                        # Verifica vitória
                        vencedor = tabuleiro.check_winner()
                        if vencedor:
                            jogo_encerrado     = True
                            mensagem_fim       = f"{vencedor} Venceu!"
                            combinacao_vitoria = achar_combinacao_vitoria(grade, vencedor)

                        # Verifica empate
                        elif tabuleiro.is_full():
                            jogo_encerrado = True
                            mensagem_fim   = "Empate!"
                            vencedor       = "Empate"

                        # ── Persistência única via flag ──────────────────────
                        if jogo_encerrado and not resultado_gravado:
                            try:
                                salvar_resultado(
                                    vencedor=vencedor,
                                    jogadas=total_jogadas,
                                )
                                resultado_gravado = True
                            except Exception as erro:
                                print(f"[AVISO] Falha ao gravar resultado: {erro}")

                        # Alterna jogador apenas se o jogo continua
                        if not jogo_encerrado:
                            jogador_atual = "O" if jogador_atual == "X" else "X"

        # ── Renderização ─────────────────────────────────────────────────────
        desenhar_fundo(tela)
        desenhar_grade(tela)
        desenhar_simbolos(tela, tabuleiro.get_grade())

        if combinacao_vitoria:
            destacar_vitoria(tela, combinacao_vitoria)

        desenhar_status(tela, fontes, jogador_atual, jogo_encerrado)

        if jogo_encerrado:
            desenhar_overlay(tela, fontes, mensagem_fim)

        pygame.display.flip()
        relogio.tick(FPS)

    # ── Encerramento: exibe histórico no terminal ─────────────────────────────
    exibir_historico_terminal()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
