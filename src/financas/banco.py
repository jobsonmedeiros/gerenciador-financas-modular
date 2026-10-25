"""
banco.py — Criação da conexão e do esquema do banco de dados.

PADRÃO DE PROJETO: "Connection Factory" + criação de esquema.
Uma função entrega conexões prontas e outra garante que as tabelas
existam. Nenhuma regra de negócio aqui.
"""

from __future__ import annotations

import sqlite3

from financas.configuracao import Configuracao

# Script que cria o esquema.
# - FOREIGN KEY liga transacoes.categoria_id a categorias.id.
# - CHECK (valor_centavos > 0) impede valor zero ou negativo direto no banco.
# - ON DELETE RESTRICT impede apagar uma categoria que tenha transações.
_SCRIPT_ESQUEMA = """
CREATE TABLE IF NOT EXISTS categorias (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome  TEXT NOT NULL UNIQUE,
    tipo  TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa'))
);

CREATE TABLE IF NOT EXISTS transacoes (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao      TEXT NOT NULL,
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos > 0),
    categoria_id   INTEGER NOT NULL,
    data_hora      TEXT NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_transacoes_data
    ON transacoes (data_hora);
"""


def conectar(configuracao: Configuracao) -> sqlite3.Connection:
    """Abre (ou cria) o banco e devolve uma conexão configurada.

    - row_factory = sqlite3.Row faz cada linha se comportar como dicionário:
      linha["descricao"] em vez de linha[1].
    - PRAGMA foreign_keys = ON LIGA a verificação de chave estrangeira.
      No SQLite ela vem desligada por padrão — esquecer isso é erro clássico.
    """
    conexao = sqlite3.connect(configuracao.caminho_banco)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON;")
    return conexao


def criar_esquema(conexao: sqlite3.Connection) -> None:
    """Executa o script de criação das tabelas e confirma a transação."""
    with conexao:  # `with` em conexão = commit automático se der tudo certo
        conexao.executescript(_SCRIPT_ESQUEMA)