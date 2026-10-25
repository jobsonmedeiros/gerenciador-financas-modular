# 💰 Gerenciador de Finanças Pessoais

> Sistema de controle de gastos pessoais em **Python + SQLite**, com arquitetura em camadas, código modular e testes automatizados.

🚧 **Projeto em desenvolvimento** — este README é atualizado a cada etapa.

---

## 🎯 Objetivo

Registrar receitas e despesas pelo terminal e consultar, a qualquer momento, o extrato do mês e o resumo de gastos por categoria — com os dados persistidos em um banco relacional.

O foco do projeto é praticar, de forma organizada:

- modelagem relacional (chaves, restrições, índices);
- separação de responsabilidades em camadas;
- validação de dados e tratamento de erros;
- testes automatizados.

---

## 🛠️ Tecnologias previstas

| Tecnologia | Papel |
|---|---|
| Python 3.10+ | Linguagem (dataclasses, enum, type hints, Decimal) |
| SQLite 3 | Banco de dados relacional embutido |
| pytest | Testes automatizados |
| Git / GitHub | Versionamento |

---

## 📁 Estrutura prevista

```
portifolio-financas/
├── main.py                  # ponto de entrada (monta as camadas)
├── src/
│   └── financas/
│       ├── configuracao.py  # configurações centrais
│       ├── modelos.py       # Categoria, Transacao, ResumoFinanceiro
│       ├── erros.py         # exceções de negócio
│       ├── banco.py         # conexão e esquema SQLite
│       ├── formatadores.py  # moeda e data no padrão brasileiro
│       ├── interface.py     # menu de terminal
│       ├── repositorios/    # acesso a dados (SQL)
│       └── servicos/        # regras de negócio
├── tests/                   # testes automatizados
└── docs/                    # documentação de apoio
```

---

## 🗺️ Roadmap

- [x] Definição do escopo e da estrutura do projeto
- [ ] Estrutura de pastas e arquivos base
- [ ] Configuração e conexão com o banco de dados
- [ ] Criação do esquema (tabelas, chaves e restrições)
- [ ] Modelos de domínio
- [ ] Repositório de categorias
- [ ] Repositório de transações (consultas com JOIN e GROUP BY)
- [ ] Camada de serviço (validações e cálculos)
- [ ] Interface de terminal (menu e relatórios)
- [ ] Testes automatizados
- [ ] Documentação final

---

## ▶️ Como executar

*(será documentado na etapa final)*

---

## 🧪 Testes

*(será documentado na etapa final)*

---

## 💡 Decisões técnicas

*(será documentado na etapa final)*

---

## 👤 Autor

**Jobson Medeiros** — Bacharel em Sistemas de Informação e Licenciado em Matemática.

- GitHub: [@jobsonmedeiros](https://github.com/jobsonmedeiros)
- Linkedin: [@jobsonmedeiros](https://www.linkedin.com/in/jobsonmedeiros/)
