"""
modelos.py — As "entidades" do sistema (o que existe no domínio).

PADRÃO DE PROJETO: "Domain Model" com dataclasses.
Cada classe representa um conceito real do negócio (Categoria, Transacao)
e NÃO sabe nada de banco de dados, de terminal ou de SQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TipoMovimento(str, Enum):
    """Tipo de uma categoria ou transação.

    Herdar de `str` permite comparar direto com texto do banco:
    TipoMovimento.RECEITA == "receita"  -> True
    """

    RECEITA = "receita"
    DESPESA = "despesa"


@dataclass(frozen=True)
class Categoria:
    """Uma categoria de gasto ou de ganho (ex.: Alimentação, Salário)."""

    id: int | None      # None enquanto ainda não foi salva no banco
    nome: str
    tipo: TipoMovimento


@dataclass(frozen=True)
class Transacao:
    """Um lançamento financeiro (uma entrada ou uma saída de dinheiro).

    IMPORTANTE: o valor é guardado em CENTAVOS e como inteiro.
    Guardar dinheiro em float gera erro de arredondamento
    (0.1 + 0.2 != 0.3). Inteiro em centavos é o padrão da indústria.
    """

    id: int | None
    descricao: str
    valor_centavos: int
    categoria_id: int
    data_hora: datetime

    @property
    def valor_reais(self) -> float:
        """Converte centavos para reais apenas na hora de exibir."""
        return self.valor_centavos / 100


@dataclass(frozen=True)
class ResumoCategoria:
    """Resultado de um agrupamento: quanto cada categoria movimentou."""

    categoria: str
    tipo: TipoMovimento
    total_centavos: int


@dataclass(frozen=True)
class ResumoFinanceiro:
    """Resultado consolidado de um período (usado no relatório)."""

    total_receitas_centavos: int
    total_despesas_centavos: int
    por_categoria: tuple[ResumoCategoria, ...]

    @property
    def saldo_centavos(self) -> int:
        """Saldo = tudo que entrou menos tudo que saiu."""
        return self.total_receitas_centavos - self.total_despesas_centavos