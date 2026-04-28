<div align="center">

# 🎮 Jogo da Velha — MVP

![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-00B140?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-d71f00?style=for-the-badge&logo=sqlite&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Testado-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow?style=for-the-badge)

**Um MVP funcional do clássico Jogo da Velha (Tic-Tac-Toe), construído com Python e Pygame, com arquitetura modular, salvamento automático de histórico no banco de dados e metodologia NLDD.**

</div>

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos e Instalação](#-pré-requisitos-e-instalação)
- [Como Executar](#-como-executar)
- [Persistência e Configuração](#️-persistência-e-configuração)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Controles](#-controles)
- [Contribuição](#-contribuição)

---

## ✨ Funcionalidades

- 🧠 **Lógica de negócio isolada** — a classe `Board` é completamente independente do Pygame, podendo ser reutilizada ou testada sem interface gráfica
- 🎨 **Interface gráfica com tema escuro premium** — janela 600×660 px com paleta de cores harmoniosa, peças com efeito de brilho (*glow*) e animações de hover
- 🗄️ **Armazenamento de Partidas** — os resultados das partidas são salvos automaticamente em um banco de dados via SQLAlchemy
- 🏆 **Detecção automática de vitória** — avalia todas as 8 combinações possíveis (3 linhas, 3 colunas, 2 diagonais)
- 🤝 **Detecção de empate** — identifica tabuleiro cheio sem vencedor
- 🔄 **Reinício rápido de partida** — sem necessidade de fechar e reabrir a aplicação
- 🛡️ **Validação completa de jogadas** — rejeita coordenadas fora dos limites, células já ocupadas e jogadas após fim de jogo
- 🧪 **Suíte de testes unitários** — 30+ casos de teste cobrindo todos os cenários da lógica de negócio

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia | Versão | Finalidade |
|---|---|---|---|
| Linguagem | Python | 3.13+ | Base do projeto |
| Interface Gráfica | Pygame | 2.6.1 | Renderização e eventos |
| Banco de Dados | SQLAlchemy (SQLite/PostgreSQL) | latest | Persistência de resultados |
| Variáveis de Ambiente | python-dotenv | latest | Carregamento de configurações seguras |
| Testes | Pytest | latest | Validação da lógica |

---

## ⚙️ Pré-requisitos e Instalação

**Requisitos mínimos:**
- Python 3.13 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Passo a passo de Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/jogo_da_velha_mvp.git
cd jogo_da_velha_mvp
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

## 🗄️ Persistência e Configuração

O MVP conta com uma camada de banco de dados robusta gerida pelo **SQLAlchemy**. A conexão é parametrizada de forma segura através do pacote **python-dotenv**, que lê as variáveis contidas no arquivo `.env`.

### O arquivo `.env` e suas configurações

Antes de rodar o projeto pela primeira vez, você precisa criar um arquivo `.env` na raiz do projeto (geralmente copiando do `.env.example`). O arquivo `.env` contém configurações sensíveis e parâmetros de ambiente da sua máquina.

**Exemplo do conteúdo esperado no `.env`**:
```env
DATABASE_URL=sqlite:///./jogo.db
DEBUG=True
```

**Explicação das variáveis:**
- `DATABASE_URL`: Define a string de conexão com o banco de dados. No exemplo acima, configuramos para criar um banco de dados local chamado `jogo.db` na raiz do projeto (SQLite). Se você desejar usar um banco como PostgreSQL no futuro, basta alterar essa string (ex: `postgresql://usuario:senha@localhost/meubanco`).
- `DEBUG`: Define se a aplicação deve exibir logs mais detalhados (como o SQL gerado pelo SQLAlchemy no console). 

Sempre que uma partida é concluída (vitória ou empate), a aplicação aciona o módulo `src/database.py`, que se conecta à `DATABASE_URL` informada, cria as tabelas caso não existam, e salva o vencedor, a quantidade de jogadas e a data/hora.

---

## ▶️ Como Executar

### 1. Iniciar o jogo

Certifique-se de que o `.env` foi criado. Em seguida, rode:

```bash
python src/main.py
```

### 2. Verificar o Banco de Dados

Para verificar os registros salvos localmente sem precisar abrir um cliente SQL, execute o script auxiliar:

```bash
python verificar_banco.py
```

### 3. Executar os testes unitários

```bash
# Execução simples com saída detalhada
pytest tests/ -v
```

---

## 🏗️ Arquitetura do Projeto

O projeto adota a metodologia **NLDD (Natural Language Driven Development)**, garantindo a máxima separação de responsabilidades.

```text
jogo_da_velha_mvp/
│
├── src/
│   ├── __init__.py       # Marca src/ como pacote Python
│   ├── logic.py          # 🧠 LÓGICA DE NEGÓCIO — classe Board (zero dependência visual)
│   ├── database.py       # 🗄️ BANCO DE DADOS — SQLAlchemy e modelos de persistência
│   └── main.py           # 🎨 INTERFACE GRÁFICA — renderização Pygame e loop de eventos
│
├── tests/
│   ├── __init__.py       # Marca tests/ como pacote Python
│   └── test_logic.py     # 🧪 TESTES UNITÁRIOS — 30+ casos via Pytest
│
├── .env                  # Variáveis de ambiente locais (não versionado)
├── .env.example          # Exemplo de configuração de variáveis
├── requirements.txt      # Dependências do projeto
├── verificar_banco.py    # Script utilitário para listar partidas
└── README.md             # Esta documentação
```

---

## 🕹️ Controles

| Ação | Controle |
|---|---|
| Realizar jogada | Clique esquerdo do rato na célula |
| Reiniciar partida | Tecla `R` ou clique após fim de jogo |
| Sair da aplicação | Tecla `ESC` ou fechar a janela |

---

<div align="center">

Desenvolvido com 🐍 Python · ⚡ Pygame · 🤖 Antigravity (Google DeepMind)

</div>
