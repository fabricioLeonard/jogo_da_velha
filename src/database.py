"""
Módulo de persistência do Jogo da Velha.

Carrega a URL do banco de dados a partir da variável DATABASE_URL
definida no ficheiro .env (via python-dotenv). Configura o engine
SQLAlchemy, define o modelo ORM da tabela `partidas` e expõe as
funções públicas `salvar_resultado` e `listar_partidas`.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ---------------------------------------------------------------------------
# Carregamento do .env
# ---------------------------------------------------------------------------

# Localiza o ficheiro .env na raiz do projecto (um nível acima de src/)
_RAIZ_PROJETO = Path(__file__).resolve().parent.parent
_FICHEIRO_ENV = _RAIZ_PROJETO / ".env"

# load_dotenv não lança excepção se o ficheiro não existir — apenas ignora
load_dotenv(dotenv_path=_FICHEIRO_ENV)


# ---------------------------------------------------------------------------
# Configuração do engine
# ---------------------------------------------------------------------------

def _obter_url_banco() -> str:
    """
    Lê DATABASE_URL do ambiente (previamente carregado pelo dotenv).

    Usa SQLite local como fallback seguro caso a variável não esteja definida.

    Returns:
        str: URL de conexão compatível com SQLAlchemy.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        # Fallback: SQLite na raiz do projecto
        caminho_sqlite = _RAIZ_PROJETO / "jogo_da_velha.db"
        url = f"sqlite:///{caminho_sqlite}"
        print(
            f"[AVISO] DATABASE_URL não encontrada no .env. "
            f"Usando SQLite em: {caminho_sqlite}"
        )
    return url


_URL_BANCO: str = _obter_url_banco()

# Para SQLite, a URL relativa sqlite:///jogo_da_velha.db é resolvida
# relativamente ao diretório de trabalho actual. Usamos o caminho absoluto
# gerado pelo fallback acima para garantir consistência em qualquer CWD.
_connect_args: dict = (
    {"check_same_thread": False}
    if _URL_BANCO.startswith("sqlite")
    else {}
)

_engine = create_engine(
    _URL_BANCO,
    connect_args=_connect_args,
    echo=False,  # defina True para imprimir o SQL gerado (útil em desenvolvimento)
)

_SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


# ---------------------------------------------------------------------------
# Modelo ORM
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Classe base declarativa para todos os modelos ORM."""


class Partida(Base):
    """
    Modelo ORM que representa uma partida registada no banco de dados.

    Atributos:
        id (int): Identificador único gerado automaticamente (PK).
        data_hora (datetime): Data e hora do registo em UTC (auto-preenchido).
        vencedor (str | None): Símbolo do vencedor ('X', 'O' ou 'Empate').
        total_jogadas (int): Total de jogadas realizadas na partida.
    """

    __tablename__ = "partidas"

    id: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Chave primária auto-incrementada",
    )
    data_hora: datetime = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Data e hora do registo em UTC",
    )
    vencedor: Optional[str] = Column(
        String(10),
        nullable=True,
        comment="Símbolo do vencedor: 'X', 'O' ou 'Empate'",
    )
    total_jogadas: int = Column(
        Integer,
        nullable=False,
        comment="Número total de jogadas realizadas",
    )

    def __repr__(self) -> str:
        return (
            f"<Partida id={self.id} "
            f"vencedor={self.vencedor!r} "
            f"jogadas={self.total_jogadas} "
            f"data={self.data_hora}>"
        )


# ---------------------------------------------------------------------------
# Inicialização automática das tabelas
# ---------------------------------------------------------------------------


def _inicializar_banco() -> None:
    """
    Cria as tabelas no banco de dados caso ainda não existam.

    Executada automaticamente na importação do módulo, sem necessidade
    de migrações manuais no contexto do MVP.
    """
    Base.metadata.create_all(bind=_engine)


_inicializar_banco()


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def salvar_resultado(vencedor: Optional[str], jogadas: int) -> Partida:
    """
    Persiste o resultado de uma partida no banco de dados.

    Abre uma sessão dedicada, insere o registo, realiza o commit e
    fecha a conexão — garantindo que a transacção seja atómica.
    Em caso de erro executa rollback antes de propagar a excepção.

    Args:
        vencedor (Optional[str]): Símbolo do vencedor ('X', 'O'),
            'Empate' para partidas sem vencedor, ou None se indefinido.
        jogadas (int): Número total de jogadas realizadas.

    Returns:
        Partida: Instância do modelo com o ``id`` populado após o commit.

    Raises:
        ValueError: Se ``jogadas`` for negativo.
        SQLAlchemyError: Em caso de falha ao persistir no banco de dados.

    Exemplo::

        partida = salvar_resultado(vencedor='X', jogadas=5)
        print(partida.id)  # ex.: 1
    """
    if jogadas < 0:
        raise ValueError(
            f"O total de jogadas não pode ser negativo. Recebido: {jogadas}"
        )

    sessao: Session = _SessionLocal()
    try:
        nova_partida = Partida(
            data_hora=datetime.utcnow(),
            vencedor=vencedor,
            total_jogadas=jogadas,
        )
        sessao.add(nova_partida)
        sessao.commit()
        # Atualiza o objecto com os valores gerados pelo banco (ex.: id)
        sessao.refresh(nova_partida)
        return nova_partida
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()


def listar_partidas() -> list[Partida]:
    """
    Retorna todas as partidas registadas, ordenadas da mais recente para a mais antiga.

    Returns:
        list[Partida]: Lista de instâncias de :class:`Partida`.
    """
    sessao: Session = _SessionLocal()
    try:
        return (
            sessao.query(Partida)
            .order_by(Partida.data_hora.desc())
            .all()
        )
    finally:
        sessao.close()


def verificar_conexao() -> bool:
    """
    Testa se a conexão com o banco de dados está operacional.

    Returns:
        bool: True se a conexão for bem-sucedida, False caso contrário.
    """
    try:
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as erro:
        print(f"[ERRO] Falha na conexão com o banco: {erro}")
        return False
