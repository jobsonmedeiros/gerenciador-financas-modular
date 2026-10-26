"""
test_servico.py — Testes das regras de negócio.

PADRÃO DE PROJETO: "AAA (Arrange, Act, Assert)".
Cada teste prepara os dados (Arrange), executa uma ação (Act) e
verifica o resultado (Assert). O nome descreve o comportamento.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from financas.erros import CategoriaInvalidaError, ValorInvalidoError
from financas.modelos import TipoMovimento


def _id_categoria(servico, nome: str) -> int:
    """Acha o id de uma categoria pelo nome (facilita os testes)."""
    for categoria in servico.listar_categorias():
        if categoria.nome == nome:
            return categoria.id
    raise AssertionError(f"Categoria {nome} não encontrada")


def test_categorias_padrao_sao_criadas_uma_unica_vez(servico):
    # Arrange / Act
    criadas_primeira_vez = servico.inicializar_dados_padrao()
    criadas_segunda_vez = servico.inicializar_dados_padrao()

    # Assert: a segunda chamada é idempotente
    assert criadas_primeira_vez == 9
    assert criadas_segunda_vez == 0


def test_registra_transacao_convertendo_valor_com_virgula(servico_com_categorias):
    servico = servico_com_categorias
    categoria_id = _id_categoria(servico, "Alimentação")

    transacao = servico.registrar_transacao("Mercado", "150,90", categoria_id)

    assert transacao.id is not None
    assert transacao.valor_centavos == 15090


def test_aceita_valor_com_ponto_de_milhar(servico_com_categorias):
    servico = servico_com_categorias
    categoria_id = _id_categoria(servico, "Moradia")

    transacao = servico.registrar_transacao("Aluguel", "1.234,56", categoria_id)

    assert transacao.valor_centavos == 123456


def test_aceita_valor_com_simbolo_de_moeda(servico_com_categorias):
    servico = servico_com_categorias
    categoria_id = _id_categoria(servico, "Educação")

    transacao = servico.registrar_transacao("Curso", "R$ 89,90", categoria_id)

    assert transacao.valor_centavos == 8990


@pytest.mark.parametrize("valor_invalido", ["0", "-10", "abc", "", "   "])
def test_rejeita_valores_invalidos(servico_com_categorias, valor_invalido):
    servico = servico_com_categorias
    categoria_id = _id_categoria(servico, "Lazer")

    with pytest.raises(ValorInvalidoError):
        servico.registrar_transacao("Cinema", valor_invalido, categoria_id)


def test_rejeita_categoria_inexistente(servico_com_categorias):
    with pytest.raises(CategoriaInvalidaError):
        servico_com_categorias.registrar_transacao("Teste", "10", 9999)


def test_rejeita_descricao_vazia(servico_com_categorias):
    servico = servico_com_categorias
    categoria_id = _id_categoria(servico, "Transporte")

    with pytest.raises(ValorInvalidoError):
        servico.registrar_transacao("   ", "10", categoria_id)


def test_resumo_calcula_saldo_e_agrupa_por_categoria(servico_com_categorias):
    # Arrange
    servico = servico_com_categorias
    quando = datetime(2026, 10, 15, 12, 0)

    servico.registrar_transacao(
        "Salário", "5000", _id_categoria(servico, "Salário"), quando
    )
    servico.registrar_transacao(
        "Mercado", "800,50", _id_categoria(servico, "Alimentação"), quando
    )
    servico.registrar_transacao(
        "Ônibus", "199,50", _id_categoria(servico, "Transporte"), quando
    )

    # Act
    resumo = servico.gerar_resumo()

    # Assert
    assert resumo.total_receitas_centavos == 500000
    assert resumo.total_despesas_centavos == 100000
    assert resumo.saldo_centavos == 400000

    categorias = {linha.categoria: linha for linha in resumo.por_categoria}
    assert categorias["Alimentação"].total_centavos == 80050
    assert categorias["Alimentação"].tipo is TipoMovimento.DESPESA


def test_resumo_filtra_por_periodo(servico_com_categorias):
    servico = servico_com_categorias
    categoria_id = _id_categoria(servico, "Salário")

    servico.registrar_transacao(
        "Salário setembro", "1000", categoria_id, datetime(2026, 9, 5, 9, 0)
    )
    servico.registrar_transacao(
        "Salário outubro", "2000", categoria_id, datetime(2026, 10, 5, 9, 0)
    )

    resumo_outubro = servico.gerar_resumo(
        inicio=datetime(2026, 10, 1), fim=datetime(2026, 10, 31, 23, 59, 59)
    )

    assert resumo_outubro.total_receitas_centavos == 200000


def test_resumo_de_periodo_sem_transacoes_volta_zerado(servico_com_categorias):
    resumo = servico_com_categorias.gerar_resumo(
        inicio=datetime(2020, 1, 1), fim=datetime(2020, 12, 31)
    )

    assert resumo.total_receitas_centavos == 0
    assert resumo.total_despesas_centavos == 0
    assert resumo.saldo_centavos == 0
    assert resumo.por_categoria == ()
