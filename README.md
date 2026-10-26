# 💰 Gerenciador de Finanças Pessoais

Aplicação em **Python e SQLite** para registrar receitas e despesas e consultar
resumos financeiros por período e categoria, construída com arquitetura em
camadas e código modular.

> **Status:** em desenvolvimento. A estrutura de domínio, persistência e regras de negócio já estão implementadas. A interface de terminal e os testes automatizados ainda estão pendentes.

---

## 🎯 Objetivo

O projeto está sendo desenvolvido para praticar, de forma organizada e com ajuda de IA:

- modelagem de dados relacionais com SQLite;
- separação de responsabilidades em camadas;
- validação de dados e tratamento de erros de negócio;
- representação precisa de valores monetários;
- testes automatizados.

---

## 🛠️ Tecnologias

| Tecnologia | Papel |
|---|---|
| Python 3.10+ | Linguagem (dataclasses, enum, type hints, Decimal) |
| SQLite 3 | Banco de dados relacional embutido |
| pytest | Testes automatizados (dependência de desenvolvimento) |
| Git / GitHub | Versionamento |

---

## 🏗️ Arquitetura em camadas

O fluxo de uma chamada é sempre o mesmo, de fora para dentro:

```
┌──────────────────────────────────────────────────────────┐
│  interface.py        Terminal: lê teclado, imprime       │  ← Apresentação
├──────────────────────────────────────────────────────────┤
│  servicos/           Regras de negócio e validações      │  ← Domínio
├──────────────────────────────────────────────────────────┤
│  repositorios/       Único lugar com SQL                 │  ← Persistência
├──────────────────────────────────────────────────────────┤
│  banco.py            Conexão e esquema (SQLite)          │  ← Infraestrutura
└──────────────────────────────────────────────────────────┘
```

**Regra de ouro:** uma camada só fala com a camada logo abaixo. A interface
nunca escreve SQL; o repositório nunca imprime no terminal; o modelo nunca
sabe que o banco existe.

Benefício prático: para virar uma API REST, apenas a camada de apresentação é
substituída. Serviço, repositórios e modelos continuam intactos.

---

## 🧩 Padrões de projeto usados

| Padrão | Onde está | Para que serve |
|---|---|---|
| **Layered Architecture** | projeto inteiro | Separa apresentação, negócio e dados |
| **Repository** | `repositorios/` | Isola o SQL; trocar de banco afeta só esta camada |
| **Service Layer** | `servicos/` | Concentra as regras de negócio em um lugar testável |
| **Domain Model** (dataclasses) | `modelos.py` | Representa o negócio sem depender de framework |
| **Dependency Injection** | construtores | Facilita testes (troca repositório por dublê) |
| **Custom Exceptions** | `erros.py` | Erros de negócio explícitos, sem `print` espalhado |
| **Configuration Object** | `configuracao.py` | Configuração central e imutável (`frozen=True`) |
| **Value Object** | `TipoMovimento`, `ResumoFinanceiro` | Objetos que carregam dados entre camadas |
| **Formatter / Presenter** | `formatadores.py` | Formatação de moeda e data separada da regra |
| **12-Factor (config por env)** | `configuracao.py` | Caminho do banco via `FINANCAS_DB` |

---

## 🗄️ Modelo de dados

```
┌──────────────────────┐          ┌──────────────────────────┐
│      categorias      │          │        transacoes        │
├──────────────────────┤          ├──────────────────────────┤
│ id    INTEGER PK     │◄────────┐│ id             INTEGER PK│
│ nome  TEXT UNIQUE    │         └│ categoria_id   INTEGER FK│
│ tipo  TEXT CHECK     │          │ descricao      TEXT      │
└──────────────────────┘          │ valor_centavos INTEGER   │
                                  │ data_hora      TEXT      │
                                  └──────────────────────────┘
```

Regras garantidas **pelo banco**, não só pelo Python:

- `categorias.nome` é `UNIQUE` — não existem duas categorias com o mesmo nome.
- `categorias.tipo` tem `CHECK (tipo IN ('receita','despesa'))`.
- `transacoes.valor_centavos` tem `CHECK (valor_centavos > 0)`.
- `transacoes.categoria_id` é `FOREIGN KEY` com `ON DELETE RESTRICT`: não é
  possível apagar uma categoria que tenha transações.
- `PRAGMA foreign_keys = ON` é executado a cada conexão — no SQLite a
  verificação de chave estrangeira vem **desligada** por padrão.
- Índice em `transacoes.data_hora` para acelerar os filtros por período.

Consultas que o projeto demonstra: `JOIN` entre as duas tabelas, `GROUP BY`
com `SUM` para os totais, filtro por período (`>=` / `<=`), `INSERT OR IGNORE`
para idempotência e consultas sempre parametrizadas (`?`).

---

## 📁 Estrutura atual

```text
src/financas/
├── banco.py                         # conexão e criação do esquema SQLite
├── configuracao.py                  # configurações da aplicação
├── erros.py                         # exceções de negócio
├── formatadores.py                  # formatação de moeda, data e movimento
├── modelos.py                       # entidades e modelos de resumo
├── repositorios/
│   ├── categoria_repositorio.py     # persistência e consulta de categorias
│   └── transacao_repositorio.py     # transações e consultas agregadas
└── servicos/
    └── financas_servico.py          # validações e regras de negócio

tests/                               # testes automatizados (a implementar)
```

---

## ✅ O que já está implementado

- Criação do banco SQLite, com tabelas para categorias e transações,
  restrições de integridade e índice por data.
- Modelos de domínio imutáveis para categorias, transações e resumos.
- Categorias padrão, criadas de forma idempotente.
- Registro e listagem de transações, com filtros opcionais por data.
- Resumo de receitas e despesas e agrupamento de valores por categoria.
- Validação de descrição, categoria e valor informado.
- Valores monetários armazenados em centavos inteiros, sem usar `float`
  para persistência ou cálculos.
- Funções de formatação para moeda brasileira, data, tipo e sinal do movimento.

---

## 🚧 Ainda por fazer

- Interface de terminal para interação com a pessoa usuária.
- Testes automatizados para serviços, repositórios e formatadores.
- Definição e aplicação consistente do fuso horário configurado.

---

## ⚙️ Configuração do ambiente

O programa usa apenas a biblioteca padrão do Python em tempo de execução.
Para instalar as dependências de desenvolvimento:

```bash
python -m pip install -r requirements.txt
```

O caminho do banco pode ser definido pela variável de ambiente `FINANCAS_DB`.
Sem essa variável, o banco é criado como `financas.db` no diretório de execução.
O fuso horário pode ser informado por `FINANCAS_TZ`; sua aplicação efetiva às
datas ainda está pendente.

---

## ▶️ Uso atual

O projeto ainda não tem um ponto de entrada ou menu de terminal. As operações
estão disponíveis pela camada de serviço. O trecho abaixo cria um banco em
memória, inicializa o esquema e as categorias padrão:

```python
import sqlite3

from financas.banco import criar_esquema
from financas.modelos import TipoMovimento
from financas.repositorios import CategoriaRepositorio, TransacaoRepositorio
from financas.servicos.financas_servico import FinancasServico

conexao = sqlite3.connect(":memory:")
conexao.row_factory = sqlite3.Row
conexao.execute("PRAGMA foreign_keys = ON;")
criar_esquema(conexao)

servico = FinancasServico(
    CategoriaRepositorio(conexao),
    TransacaoRepositorio(conexao),
)
servico.inicializar_dados_padrao()

categoria = servico.listar_categorias(TipoMovimento.RECEITA)[0]
servico.registrar_transacao("Salário", "3500,00", categoria.id)
resumo = servico.gerar_resumo()

print(resumo.saldo_centavos)
```

Para executar um script com esses imports a partir da raiz do repositório,
adicione `src` ao caminho de módulos do Python.

**PowerShell:**
```powershell
$env:PYTHONPATH = "src"
python exemplo.py
```

**Bash / Linux / macOS:**
```bash
PYTHONPATH=src python exemplo.py
```

---

## 💡 Decisões técnicas

**1. Dinheiro em centavos inteiros, não em `float`.**
`0.1 + 0.2 != 0.3` em ponto flutuante. Guardar `valor_centavos INTEGER` elimina
erro de arredondamento. A conversão para reais acontece só na exibição.

**2. `Decimal` na conversão de entrada.**
Aceita `"1.234,56"` e `"1234.56"` sem perder precisão, e a validação de valor
positivo fica no serviço, não na tela.

**3. Consultas sempre parametrizadas (`?`).**
Nunca há concatenação de texto no SQL — proteção contra SQL Injection.

**4. `INSERT OR IGNORE` para dados iniciais.**
A inicialização é *idempotente*: rodar dez vezes produz o mesmo estado.

**5. Datas em ISO-8601 (`YYYY-MM-DDTHH:MM:SS`).**
Formato que ordena corretamente como texto, permitindo comparação direta no SQL.

**6. Erros de negócio como exceções.**
O serviço lança `ValorInvalidoError`; a interface decide como mostrar. Isso
mantém a regra de negócio independente de terminal, API ou HTML.

**7. `PRAGMA foreign_keys = ON` em cada conexão.**
No SQLite a verificação de chave estrangeira é desligada por padrão — sem o
`PRAGMA`, o banco aceitaria `categoria_id` inexistente.

---

## 🧪 Testes

A suíte de testes automatizados ainda está sendo criada. Quando houver testes
em `tests/`, execute-os com:

```bash
python -m pytest
```

---

## 🗺️ Roadmap

- [x] Definição do escopo e estrutura inicial do projeto
- [x] Configuração e conexão com SQLite
- [x] Criação do esquema do banco
- [x] Modelos de domínio e exceções de negócio
- [x] Repositório de categorias
- [x] Repositório de transações e consultas agregadas
- [x] Camada de serviço com validações e cálculos
- [x] Funções iniciais de formatação
- [ ] Testes automatizados
- [ ] Interface de terminal e relatórios
- [ ] Documentação final e instruções de uso completas

---

## 👤 Autor

**Jobson Medeiros** — Bacharel em Sistemas de Informação e Licenciado em
Matemática.

- GitHub: [@jobsonmedeiros](https://github.com/jobsonmedeiros)
- LinkedIn: [@jobsonmedeiros](https://www.linkedin.com/in/jobsonmedeiros/)
