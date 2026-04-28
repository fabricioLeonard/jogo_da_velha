<div align="center">

# 🎮 Jogo da Velha — MVP

![Versão](https://img.shields.io/badge/Versão-v1.0.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-00B140?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-d71f00?style=for-the-badge&logo=sqlite&logoColor=white)
![python-dotenv](https://img.shields.io/badge/python--dotenv-env-ECD53F?style=for-the-badge&logo=dotenv&logoColor=black)
![Pytest](https://img.shields.io/badge/Pytest-Testado-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Licença](https://img.shields.io/badge/Licença-MIT-yellow?style=for-the-badge)

**Um MVP funcional do clássico Jogo da Velha (Tic-Tac-Toe), construído com Python e Pygame, com arquitetura modular, salvamento automático de histórico via SQLAlchemy e metodologia NLDD.**

</div>

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos e Instalação](#-pré-requisitos-e-instalação)
- [Configuração do Ambiente](#️-configuração-do-ambiente)
- [Como Executar](#️-como-executar)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Controles](#-controles)
- [Contribuição](#-contribuição)

---

## ✨ Funcionalidades

- 🧠 **Lógica de negócio isolada** — a classe `Board` é completamente independente do Pygame, podendo ser reutilizada ou testada sem interface gráfica
- 🎨 **Interface gráfica com tema escuro** — janela 600×600 px com paleta de cores harmoniosa, símbolos X e O em ciano e rosa-coral, linha dourada sobre as células vencedoras
- 🗄️ **Persistência automática** — ao fim de cada partida (vitória ou empate), o resultado é gravado exatamente **uma vez** na tabela `partidas` via flag `resultado_gravado`
- 🏆 **Detecção automática de vitória** — avalia todas as 8 combinações possíveis (3 linhas, 3 colunas, 2 diagonais)
- 🤝 **Detecção de empate** — identifica tabuleiro cheio sem vencedor (velha)
- 🔄 **Reinício rápido** — tecla `R` reinicia a partida sem fechar a aplicação
- 🛡️ **Validação completa de jogadas** — rejeita coordenadas fora dos limites e células já ocupadas
- 📋 **Histórico no terminal** — ao encerrar, exibe tabela formatada com todas as partidas e resumo estatístico
- 🔍 **Inspeção do banco via CLI** — `src/inspect_db.py` com filtros `--limite` e `--vencedor`
- 🧪 **Suíte de testes unitários** — 30+ casos cobrindo todos os cenários, com validação do estado interno da matriz

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia | Finalidade |
|---|---|---|
| Linguagem | Python 3.13+ | Base do projeto |
| Interface Gráfica | Pygame 2.6.1 | Renderização e loop de eventos |
| Banco de Dados | SQLAlchemy + SQLite | Persistência de resultados (ORM) |
| Variáveis de Ambiente | python-dotenv | Carregamento seguro de configurações |
| Testes | Pytest | Validação da lógica de negócio |

---

## ⚙️ Pré-requisitos e Instalação

**Requisitos mínimos:**
- Python 3.13 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Passo a passo

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/jogo_da_velha.git
cd jogo_da_velha
```

**2. Crie e ative o ambiente virtual**
```bash
# Criar
python -m venv venv

# Ativar — Windows (PowerShell)
venv\Scripts\Activate.ps1

# Ativar — Linux / macOS
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

---

## 🔐 Configuração do Ambiente

O projeto usa **python-dotenv** para carregar configurações a partir do arquivo `.env` na raiz do projeto.

**1. Copie o arquivo de exemplo:**
```bash
cp .env.example .env
```

**2. Conteúdo do `.env`:**
```env
# String de conexão com o banco de dados
DATABASE_URL=sqlite:///jogo_da_velha.db
```

**Variáveis disponíveis:**

| Variável | Obrigatória | Padrão (fallback) | Descrição |
|---|---|---|---|
| `DATABASE_URL` | Não | `sqlite:///jogo_da_velha.db` | URL de conexão SQLAlchemy. Compatível com SQLite, PostgreSQL e MySQL |

> **Nota:** Se `DATABASE_URL` não for definida, o `database.py` usa automaticamente SQLite local com aviso no terminal. As tabelas são criadas automaticamente na primeira execução.

**Exemplos de `DATABASE_URL`:**
```env
# SQLite (desenvolvimento)
DATABASE_URL=sqlite:///jogo_da_velha.db

# PostgreSQL (produção)
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/jogo_da_velha

# MySQL / MariaDB
DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/jogo_da_velha
```

---

## ▶️ Como Executar

### 1. Iniciar o jogo

```bash
python src/main.py
```

A janela Pygame abrirá. As partidas são salvas automaticamente no banco ao terminar.
Ao fechar, o histórico completo é exibido no terminal.

### 2. Inspecionar o banco de dados

Use `src/inspect_db.py` para consultar o histórico sem abrir um cliente SQL:

```bash
# Todos os registros
python src/inspect_db.py

# Últimas 5 partidas
python src/inspect_db.py --limite 5

# Apenas vitórias de X
python src/inspect_db.py --vencedor X

# Empates com limite
python src/inspect_db.py --vencedor Empate --limite 3
```

**Filtros disponíveis:**

| Flag | Atalho | Valores aceitos | Descrição |
|---|---|---|---|
| `--limite` | `-l` | inteiro | Número máximo de registros |
| `--vencedor` | `-v` | `X`, `O`, `Empate` | Filtra pelo resultado da partida |

### 3. Executar os testes unitários

```bash
pytest tests/ -v
```

---

## 🏗️ Arquitetura do Projeto

O projeto adota a metodologia **NLDD (Natural Language Driven Development)**, com separação clara de responsabilidades.

```text
jogo_da_velha/
│
├── src/
│   ├── logic.py          # 🧠 LÓGICA — classe Board (zero dependência visual)
│   ├── database.py       # 🗄️ DADOS — SQLAlchemy, modelo Partida, salvar_resultado()
│   ├── main.py           # 🎨 INTERFACE — Pygame, loop de eventos, flag resultado_gravado
│   └── inspect_db.py     # 🔍 CLI — inspeção do banco com filtros e resumo estatístico
│
├── tests/
│   └── test_logic.py     # 🧪 TESTES — 30+ casos com validação da matriz interna
│
├── .env                  # Variáveis de ambiente locais (não versionado)
├── .env.example          # Modelo de configuração de variáveis
├── .gitignore            # Arquivos ignorados pelo Git
├── LICENSE               # Licença MIT
└── README.md             # Esta documentação
```

### Fluxo de dados

```
main.py
  └─► Board.make_move()       [logic.py]
        └─► check_winner() / is_full()
              └─► salvar_resultado()  [database.py]  ← chamado 1× via resultado_gravado
                    └─► tabela `partidas` no banco (DATABASE_URL)
```

---

## 🕹️ Controles

| Ação | Controle |
|---|---|
| Realizar jogada | Clique esquerdo na célula desejada |
| Reiniciar partida | Tecla `R` |
| Sair da aplicação | Tecla `Q`, `ESC` ou fechar a janela |

---

<div align="center">

Desenvolvido com 🐍 Python · ⚡ Pygame · 🤖 Antigravity (Google DeepMind)

</div>
