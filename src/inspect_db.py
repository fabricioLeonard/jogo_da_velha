"""
Utilitário de inspeção do banco de dados do Jogo da Velha.

Carrega DATABASE_URL do ficheiro .env, conecta-se via SQLAlchemy e
exibe o histórico completo da tabela `partidas` em formato tabular
no terminal. Útil para validar a persistência durante o desenvolvimento.

Uso:
    python src/inspect_db.py
    python src/inspect_db.py --limite 10
    python src/inspect_db.py --vencedor X
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Resolução de caminhos e carregamento do .env
# ---------------------------------------------------------------------------

_RAIZ = Path(__file__).resolve().parent.parent
_ENV  = _RAIZ / ".env"

# Tenta carregar python-dotenv; prossegue sem ele se não estiver instalado
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=_ENV)
    _DOTENV_OK = True
except ImportError:
    _DOTENV_OK = False
    print("[AVISO] python-dotenv não instalado. Lendo variáveis do ambiente do sistema.")

# Garante que src/ esteja no path para importações internas
if str(_RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(_RAIZ / "src"))

# ---------------------------------------------------------------------------
# Dependências SQLAlchemy
# ---------------------------------------------------------------------------

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
except ImportError as exc:
    print(f"[ERRO CRÍTICO] SQLAlchemy não encontrado: {exc}")
    print("  Execute: pip install sqlalchemy")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuração da conexão
# ---------------------------------------------------------------------------

def _obter_url() -> str:
    """
    Lê DATABASE_URL do ambiente. Usa SQLite local como fallback.

    Returns:
        str: URL de conexão compatível com SQLAlchemy.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        fallback = f"sqlite:///{_RAIZ / 'jogo_da_velha.db'}"
        print(f"[AVISO] DATABASE_URL não definida. Usando fallback: {fallback}")
        return fallback
    return url


def _criar_engine():
    """Cria e retorna o engine SQLAlchemy com base na URL obtida."""
    url = _obter_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, echo=False)


# ---------------------------------------------------------------------------
# Formatação tabular (sem dependências externas)
# ---------------------------------------------------------------------------

_COLUNAS = ["ID", "Data/Hora", "Vencedor", "Jogadas"]
_LARGURAS = [6, 22, 12, 9]         # largura mínima por coluna


def _linha_sep(larguras: list[int], char: str = "─") -> str:
    """Monta uma linha separadora com as larguras fornecidas."""
    segmentos = [char * (l + 2) for l in larguras]
    return "┼".join(segmentos)


def _linha_dados(valores: list[str], larguras: list[int]) -> str:
    """Formata uma linha de dados alinhada às larguras das colunas."""
    celulas = [f" {v:<{l}} " for v, l in zip(valores, larguras)]
    return "│".join(celulas)


def _cabecalho(larguras: list[int]) -> str:
    """Retorna o cabeçalho da tabela formatado."""
    return _linha_dados(_COLUNAS, larguras)


def _ajustar_larguras(linhas: list[list[str]]) -> list[int]:
    """
    Calcula a largura máxima necessária para cada coluna,
    considerando os dados e os cabeçalhos.

    Args:
        linhas: Lista de listas de strings (uma por linha de dados).

    Returns:
        list[int]: Larguras ajustadas por coluna.
    """
    larguras = list(_LARGURAS)
    for lin in linhas:
        for i, cel in enumerate(lin):
            larguras[i] = max(larguras[i], len(cel))
    return larguras


def _formatar_tabela(linhas: list[list[str]]) -> str:
    """
    Constrói a representação textual da tabela.

    Args:
        linhas: Dados da tabela (uma lista de strings por linha).

    Returns:
        str: Tabela formatada pronta para impressão.
    """
    largs = _ajustar_larguras(linhas)
    sep   = _linha_sep(largs)

    partes = [sep, _cabecalho(largs), sep]
    for lin in linhas:
        partes.append(_linha_dados(lin, largs))
    partes.append(sep)

    return "\n".join(partes)


# ---------------------------------------------------------------------------
# Lógica principal de inspeção
# ---------------------------------------------------------------------------

def listar_historico(
    limite: Optional[int] = None,
    vencedor: Optional[str] = None,
) -> None:
    """
    Realiza SELECT na tabela `partidas` e exibe os resultados no terminal.

    A query é construída dinamicamente para suportar filtragem por vencedor
    e limitação de resultados, ordenando sempre do mais recente para o mais antigo.

    Args:
        limite (Optional[int]): Número máximo de registros a exibir.
            None = sem limite.
        vencedor (Optional[str]): Filtra pelo vencedor ('X', 'O', 'Empate').
            None = sem filtro.
    """
    engine = _criar_engine()

    # ── Validação da conexão ────────────────────────────────────────────────
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as erro:
        print(f"\n[ERRO] Não foi possível conectar ao banco de dados:\n  {erro}\n")
        return

    # ── Construção da query ─────────────────────────────────────────────────
    Session = sessionmaker(bind=engine)
    sessao  = Session()

    try:
        # Importa o modelo a partir do módulo já existente no projeto
        from database import Partida

        query = sessao.query(Partida).order_by(Partida.data_hora.desc())

        if vencedor is not None:
            query = query.filter(Partida.vencedor == vencedor)

        if limite is not None:
            query = query.limit(limite)

        partidas = query.all()

    except Exception as erro:
        print(f"\n[ERRO] Falha ao consultar a tabela partidas:\n  {erro}\n")
        return
    finally:
        sessao.close()

    # ── Exibição ────────────────────────────────────────────────────────────
    print()
    _exibir_cabecalho_relatorio(limite, vencedor)

    if not partidas:
        print("  (nenhuma partida encontrada com os filtros aplicados)\n")
        return

    # Converte os registros para linhas de strings
    linhas_tabela: list[list[str]] = []
    contagem: dict[str, int] = {}

    for p in partidas:
        data_str = (
            p.data_hora.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(p.data_hora, datetime)
            else str(p.data_hora or "—")
        )
        venc_str = str(p.vencedor or "—")
        contagem[venc_str] = contagem.get(venc_str, 0) + 1

        linhas_tabela.append([
            str(p.id),
            data_str,
            venc_str,
            str(p.total_jogadas),
        ])

    print(_formatar_tabela(linhas_tabela))
    _exibir_resumo(len(partidas), contagem)


def _exibir_cabecalho_relatorio(
    limite: Optional[int],
    vencedor: Optional[str],
) -> None:
    """Imprime o título e os filtros ativos do relatório."""
    print("  📋  HISTÓRICO DE PARTIDAS — Jogo da Velha")

    filtros = []
    if vencedor:
        filtros.append(f"vencedor={vencedor!r}")
    if limite:
        filtros.append(f"limite={limite}")

    if filtros:
        print(f"  Filtros ativos: {', '.join(filtros)}")
    print()


def _exibir_resumo(total: int, contagem: dict[str, int]) -> None:
    """Imprime o bloco de resumo estatístico abaixo da tabela."""
    print(f"\n  📊  RESUMO  ({total} partida{'s' if total != 1 else ''})")
    print(f"  {'─' * 35}")

    _LABELS = {"X": "Vitórias de X", "O": "Vitórias de O", "Empate": "Empates"}

    for chave in sorted(contagem.keys()):
        qtd = contagem[chave]
        pct = (qtd / total) * 100
        label = _LABELS.get(chave, f"Outros ({chave})")
        barra = "█" * int(pct / 5)      # barra de progresso simples (cada █ = 5%)
        print(f"  {label:<16}: {qtd:>3}  {pct:5.1f}%  {barra}")

    print()


# ---------------------------------------------------------------------------
# Interface de linha de comando
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    """Define e processa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Inspeciona o banco de dados do Jogo da Velha.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python src/inspect_db.py\n"
            "  python src/inspect_db.py --limite 5\n"
            "  python src/inspect_db.py --vencedor X\n"
            "  python src/inspect_db.py --vencedor Empate --limite 3\n"
        ),
    )
    parser.add_argument(
        "--limite", "-l",
        type=int,
        default=None,
        metavar="N",
        help="Número máximo de registros a exibir (padrão: todos)",
    )
    parser.add_argument(
        "--vencedor", "-v",
        type=str,
        default=None,
        choices=["X", "O", "Empate"],
        help="Filtra pelo vencedor da partida",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = _parse_args()
    listar_historico(limite=args.limite, vencedor=args.vencedor)
