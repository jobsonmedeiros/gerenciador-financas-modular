"""
test_repositorios.py — Testes da camada de banco.

Aqui testamos o que só o banco pode garantir: chave estrangeira,
restrição de valor positivo, unicidade de categoria e o JOIN.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

import pytest

from financas.modelos import Categoria, TipoMovimento, Transacao
from financas.repositorios import CategoriaRepositorio, TransacaoRepositorio


def test_banco_impede_transacao_sem_categoria_valida(conexao):
    # A chave estrangeira está ligada no conectar(): o SQLite deve recusar.
    transacoes = TransacaoRepositorio(conexao)

    with pytest.raises(sqlite3.IntegrityError):
        transacoes.criar(
            Transacao(
                id=None,
                descricao="Sem categoria",
                valor_centavos=1000,
                categoria_id=999,
                data_hora=datetime(2026, 10, 1, 8, 0),
            )
        )


def test_banco_impede_valor_nao_positivo(conexao):
    categorias = CategoriaRepositorio(conexao)
    categoria = categorias.criar("Teste", TipoMovimento.DESPESA)

    with pytest.raises(sqlite3.IntegrityError):
        conexao.execute(
            "INSERT INTO transacoes (descricao, valor_centavos, categoria_id,"
            " data_hora) VALUES (?, ?, ?, ?);",
            ("Zero", 0, categoria.id, "2026-10-01T08:00:00"),
        )


def test_nome_de_categoria_e_unico(conexao):
    categorias = CategoriaRepositorio(conexao)
    categorias.criar("Mercado", TipoMovimento.DESPESA)

    with pytest.raises(sqlite3.IntegrityError):
        categorias.criar("Mercado", TipoMovimento.DESPESA)


def test_lista_categorias_por_tipo(conexao):
    categorias = CategoriaRepositorio(conexao)
    categorias.criar("Salário", TipoMovimento.RECEITA)
    categorias.criar("Mercado", TipoMovimento.DESPESA)

    receitas = categorias.listar(TipoMovimento.RECEITA)

    assert [c.nome for c in receitas] == ["Salário"]


def test_buscar_por_id_devolve_none_quando_nao_existe(conexao):
    categorias = CategoriaRepositorio(conexao)

    assert categorias.buscar_por_id(12345) is None


def test_soma_por_categoria_usa_join_com_tipo(conexao):
    categorias = CategoriaRepositorio(conexao)
    transacoes = TransacaoRepositorio(conexao)

    mercado: Categoria = categorias.criar("Mercado", TipoMovimento.DESPESA)
    for valor in (1000, 2500):
        transacoes.criar(
            Transacao(
                id=None,
                descricao="Compra",
                valor_centavos=valor,
                categoria_id=mercado.id,
                data_hora=datetime(2026, 10, 2, 10, 0),
            )
        )

    totais = transacoes.somar_por_tipo()
    por_categoria = transacoes.somar_por_categoria()

    assert totais[TipoMovimento.DESPESA] == 3500
    assert por_categoria[0].categoria == "Mercado"
    assert por_categoria[0].total_centavos == 3500
