"""
test_formatadores.py — Testes da formatação de valores e datas.

Formatação errada passa despercebida em revisão de código e aparece
na tela do usuário. Por isso vale testar.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from financas.formatadores import (
    formatar_data,
    formatar_reais,
    rotulo_tipo,
    sinal_tipo,
)
from financas.modelos import TipoMovimento


@pytest.mark.parametrize(
    ("centavos", "esperado"),
    [
        (0, "R$ 0,00"),
        (5, "R$ 0,05"),
        (90, "R$ 0,90"),
        (15090, "R$ 150,90"),
        (123456, "R$ 1.234,56"),
        (500000, "R$ 5.000,00"),
        (123456789, "R$ 1.234.567,89"),
        (-15090, "-R$ 150,90"),
    ],
)
def test_formatar_reais(centavos, esperado):
    assert formatar_reais(centavos) == esperado


def test_formatar_reais_aceita_outra_moeda():
    assert formatar_reais(15090, "US$") == "US$ 150,90"


def test_formatar_data_usa_padrao_brasileiro():
    assert formatar_data(datetime(2026, 10, 25, 14, 7)) == "25/10/2026 14:07"


def test_rotulo_e_sinal_do_tipo():
    assert rotulo_tipo(TipoMovimento.RECEITA) == "Receita"
    assert rotulo_tipo(TipoMovimento.DESPESA) == "Despesa"
    assert sinal_tipo(TipoMovimento.RECEITA) == "+"
    assert sinal_tipo(TipoMovimento.DESPESA) == "-"
