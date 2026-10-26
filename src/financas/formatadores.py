"""
formatadores.py — Funções que transformam dados em texto para a tela.

PADRÃO DE PROJETO: "Formatter / Presenter".
Formatação de dinheiro e data é detalhe de apresentação. Ficando aqui,
a mesma regra pode ser reutilizada por um CLI, uma API ou um HTML.
"""

from __future__ import annotations

from financas.modelos import TipoMovimento


def formatar_reais(centavos: int, moeda: str = "R$") -> str:
    """123456 -> "R$ 1.234,56" (padrão brasileiro)."""
    sinal = "-" if centavos < 0 else ""
    inteiro, resto = divmod(abs(centavos), 100)
    # "{:,}".format usa vírgula de milhar; depois trocamos por ponto.
    milhar = f"{inteiro:,}".replace(",", ".")
    return f"{sinal}{moeda} {milhar},{resto:02d}"


def formatar_data(data_hora) -> str:
    """datetime -> "23/10/2026 10:42"."""
    return data_hora.strftime("%d/%m/%Y %H:%M")


def rotulo_tipo(tipo: TipoMovimento) -> str:
    """Transforma o enum em texto legível: receita -> Receita."""
    return "Receita" if tipo is TipoMovimento.RECEITA else "Despesa"


def sinal_tipo(tipo: TipoMovimento) -> str:
    """Usa + para receita e - para despesa na listagem."""
    return "+" if tipo is TipoMovimento.RECEITA else "-"