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

tests/
├── conftest.py                      # fixtures com banco em memória
├── test_servico.py                  # testes das regras de negócio
├── test_repositorios.py             # testes de banco, chave estrangeira e JOIN
└── test_formatadores.py             # testes de formatação de moeda e data
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

- Aplicação efetiva do fuso horário configurado às datas registradas.
- Edição e exclusão de transações.
- Categorias personalizadas criadas pela pessoa usuária.

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

## ▶️ Como executar

### Pré-requisitos

- Python 3.10 ou superior (`python --version` para conferir)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/jobsonmedeiros/gerenciador-financas-modular.git

# 2. Entre na pasta
cd gerenciador-financas-modular

# 3. (opcional, recomendado) crie um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Execute
python main.py
```

Na primeira execução o sistema cria `financas.db` e as 9 categorias padrão.

### Menu

```
=== GERENCIADOR DE FINANÇAS PESSOAIS ===
1. Registrar transação
2. Ver extrato do mês
3. Resumo por categoria
4. Listar categorias
0. Sair
```

### Exemplo de saída

```
--- Extrato de 10/2026 ---
#6   26/10/2026 14:06  -R$ 89,90      (Educação) Curso de Python
#5   26/10/2026 14:06  -R$ 310,20     (Transporte) Combustível
#4   26/10/2026 14:06  -R$ 1.500,00   (Moradia) Aluguel
#3   26/10/2026 14:06  -R$ 842,35     (Alimentação) Supermercado
#2   26/10/2026 14:06  +R$ 1.200,00   (Freelance) Projeto freelance
#1   26/10/2026 14:06  +R$ 5.200,00   (Salário) Salário outubro
--------------------------------------------------------
Receitas: R$ 6.400,00
Despesas: R$ 2.742,45
Saldo:    R$ 3.657,55

--- Resumo por categoria (10/2026) ---
Salário         Receita     R$ 5.200,00
Moradia         Despesa     R$ 1.500,00
Freelance       Receita     R$ 1.200,00
Alimentação     Despesa       R$ 842,35
Transporte      Despesa       R$ 310,20
Educação        Despesa        R$ 89,90
--------------------------------------------------------
Saldo do mês: R$ 3.657,55
```

### Variáveis de ambiente

| Variável | Efeito |
|---|---|
| `FINANCAS_DB` | caminho do arquivo do banco (padrão: `financas.db`) |
| `FINANCAS_TZ` | fuso horário configurado (aplicação às datas ainda pendente) |

---

## 🧪 Testes

```bash
pip install -r requirements.txt
python -m pytest
```

Resultado esperado:

```
...............................                                          [100%]
31 passed in 0.27s
```

Os testes usam SQLite **em memória** (`:memory:`), então não tocam no banco
real e rodam em menos de um segundo. Cobertura por arquivo:

| Arquivo | O que verifica |
|---|---|
| `test_servico.py` | conversão de valores, validações, saldo, filtro por período |
| `test_repositorios.py` | chave estrangeira, `CHECK`, `UNIQUE`, `JOIN` e `GROUP BY` |
| `test_formatadores.py` | formatação de moeda, data, rótulo e sinal |

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
- [x] Funções de formatação
- [x] Interface de terminal e relatórios
- [x] Testes automatizados
- [ ] Aplicação do fuso horário configurado
- [ ] Edição e exclusão de transações
- [ ] Exportação de relatório para CSV
- [ ] Versão web com FastAPI (reaproveitando serviço e repositórios)

---

## 👤 Autor

**Jobson Medeiros** — Bacharel em Sistemas de Informação e Licenciado em
Matemática.

- GitHub: [@jobsonmedeiros](https://github.com/jobsonmedeiros)
- LinkedIn: [@jobsonmedeiros](https://www.linkedin.com/in/jobsonmedeiros/)
