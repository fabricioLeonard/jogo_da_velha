"""
Módulo de persistência do Jogo da Velha.

Configura a conexão com o banco de dados SQLite via SQLAlchemy,
define o modelo da tabela `partidas` e expõe a função
`salvar_resultado` para registrar o desfecho de cada partida.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ---------------------------------------------------------------------------
# Configuração do banco de dados
# ---------------------------------------------------------------------------

# Caminho do arquivo SQLite — fica na raiz do projeto (um nível acima de src/)
_DIRETORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CAMINHO_DB = os.path.join(_DIRETORIO_BASE, "jogo_da_velha.db")

_URL_BANCO = f"sqlite:///{_CAMINHO_DB}"

# Engine compartilhada pelo módulo
_engine = create_engine(
    _URL_BANCO,
    connect_args={"check_same_thread": False},  # necessário para SQLite em apps multithread
    echo=False,  # defina True para exibir o SQL gerado no console (útil em desenvolvimento)
)

# Fábrica de sessões ligada ao engine
_SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


# ---------------------------------------------------------------------------
# Modelo ORM
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Classe base declarativa para todos os modelos ORM."""


class Partida(Base):
    """
    Modelo ORM que representa uma partida registrada no banco de dados.

    Atributos:
        id (int): Identificador único gerado automaticamente.
        data_hora (datetime): Data e hora em que a partida foi salva (UTC).
        vencedor (str | None): Símbolo do vencedor ('X' ou 'O'),
            ou 'Empate' quando nenhum jogador vencer.
        total_jogadas (int): Número total de jogadas realizadas na partida.
    """

    __tablename__ = "partidas"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    data_hora: datetime = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Data e hora do registro em UTC",
    )
    vencedor: Optional[str] = Column(
        String(10),
        nullable=True,
        comment="Símbolo do vencedor ('X', 'O') ou 'Empate'",
    )
    total_jogadas: int = Column(
        Integer,
        nullable=False,
        comment="Total de jogadas realizadas na partida",
    )

    def __repr__(self) -> str:
        return (
            f"<Partida id={self.id} "
            f"vencedor={self.vencedor!r} "
            f"jogadas={self.total_jogadas} "
            f"data={self.data_hora}>"
        )


# ---------------------------------------------------------------------------
# Inicialização das tabelas
# ---------------------------------------------------------------------------

def _inicializar_banco() -> None:
    """
    Cria as tabelas no banco de dados caso ainda não existam.

    Chamada automaticamente na importação do módulo, garantindo que
    o schema esteja sempre atualizado sem a necessidade de migrações
    manuais no MVP.
    """
    Base.metadata.create_all(bind=_engine)


# Executa na importação do módulo
_inicializar_banco()


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def salvar_resultado(vencedor: Optional[str], jogadas: int) -> Partida:
    """
    Persiste o resultado de uma partida no banco de dados.

    Abre uma sessão dedicada, insere o registro, realiza o commit e
    fecha a sessão — garantindo que a transação seja atômica. Em caso
    de erro, executa rollback antes de propagar a exceção.

    Args:
        vencedor (Optional[str]): Símbolo do vencedor ('X' ou 'O'),
            'Empate' para partidas sem vencedor, ou None se indefinido.
        jogadas (int): Número total de jogadas realizadas na partida.

    Returns:
        Partida: Instância do modelo recém-criado com o ``id`` populado
            após o commit.

    Raises:
        ValueError: Se `jogadas` for negativo.
        SQLAlchemyError: Em caso de falha ao persistir no banco de dados.

    Exemplo::

        partida = salvar_resultado(vencedor='X', jogadas=5)
        print(partida.id)  # ex.: 1
    """
    if jogadas < 0:
        raise ValueError(f"O total de jogadas não pode ser negativo. Recebido: {jogadas}")

    sessao: Session = _SessionLocal()
    try:
        nova_partida = Partida(
            data_hora=datetime.utcnow(),
            vencedor=vencedor,
            total_jogadas=jogadas,
        )
        sessao.add(nova_partida)
        sessao.commit()
        sessao.refresh(nova_partida)  # atualiza o objeto com os dados gerados pelo DB (ex.: id)
        return nova_partida
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()


def listar_partidas() -> list[Partida]:
    """
    Retorna todas as partidas registradas, ordenadas da mais recente para a mais antiga.

    Returns:
        list[Partida]: Lista de instâncias de :class:`Partida`.
    """
    sessao: Session = _SessionLocal()
    try:
        return sessao.query(Partida).order_by(Partida.data_hora.desc()).all()
    finally:
        sessao.close()
