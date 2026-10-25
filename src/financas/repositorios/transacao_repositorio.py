"""
transacao_repositorio.py — Acesso à tabela `transacoes`.

Aqui aparecem as consultas mais interessantes do projeto:
JOIN com categorias, GROUP BY por categoria e filtro por período.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

from financas.modelos import ResumoCategoria, TipoMovimento, Transacao

# Datas gravadas como texto ISO-8601 ("2026-10-23T10:00:00").
# Esse formato ordena corretamente como texto, então BETWEEN funciona
# direto no SQL, sem conversão.
_FORMATO_DATA = "%Y-%m-%dT%H:%M:%S"


class TransacaoRepositorio:
    """Traduz linhas da tabela `transacoes` em objetos Transacao."""

    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def criar(self, transacao: Transacao) -> Transacao:
        """Insere uma transação e devolve com o id gerado."""
        with self._conexao as conexao:
            cursor = conexao.execute(
                """
                INSERT INTO transacoes
                    (descricao, valor_centavos, categoria_id, data_hora)
                VALUES (?, ?, ?, ?);
                """,
                (
                    transacao.descricao.strip(),
                    transacao.valor_centavos,
                    transacao.categoria_id,
                    transacao.data_hora.strftime(_FORMATO_DATA),
                ),
            )
        return Transacao(
            id=cursor.lastrowid,
            descricao=transacao.descricao.strip(),
            valor_centavos=transacao.valor_centavos,
            categoria_id=transacao.categoria_id,
            data_hora=transacao.data_hora,
        )

    def listar(
        self, inicio: datetime | None = None, fim: datetime | None = None
    ) -> list[Transacao]:
        """Lista transações, opcionalmente entre duas datas (inclusive)."""
        sql = (
            "SELECT id, descricao, valor_centavos, categoria_id, data_hora"
            " FROM transacoes"
        )
        parametros: list[str] = []
        filtros: list[str] = []

        # Os filtros são montados dinamicamente, mas SEMPRE com parâmetros
        # (?), nunca concatenando texto. Isso evita SQL Injection.
        if inicio is not None:
            filtros.append("data_hora >= ?")
            parametros.append(inicio.strftime(_FORMATO_DATA))
        if fim is not None:
            filtros.append("data_hora <= ?")
            parametros.append(fim.strftime(_FORMATO_DATA))

        if filtros:
            sql += " WHERE " + " AND ".join(filtros)
        sql += " ORDER BY data_hora DESC, id DESC;"

        cursor = self._conexao.execute(sql, parametros)
        return [self._para_modelo(linha) for linha in cursor.fetchall()]

    def somar_por_tipo(
        self, inicio: datetime | None = None, fim: datetime | None = None
    ) -> dict[TipoMovimento, int]:
        """Soma os valores (em centavos) separando receita e despesa.

        Usa JOIN para descobrir o tipo (que mora na tabela categorias)
        e GROUP BY para somar cada tipo de uma vez.
        """
        sql = """
            SELECT c.tipo AS tipo, SUM(t.valor_centavos) AS total
            FROM transacoes t
            JOIN categorias c ON c.id = t.categoria_id
            {where}
            GROUP BY c.tipo;
        """
        where, parametros = self._montar_where(inicio, fim)
        cursor = self._conexao.execute(sql.format(where=where), parametros)

        totais = {TipoMovimento.RECEITA: 0, TipoMovimento.DESPESA: 0}
        for linha in cursor.fetchall():
            totais[TipoMovimento(linha["tipo"])] = linha["total"] or 0
        return totais

    def somar_por_categoria(
        self, inicio: datetime | None = None, fim: datetime | None = None
    ) -> list[ResumoCategoria]:
        """Quanto cada categoria movimentou, do maior para o menor."""
        sql = """
            SELECT c.nome AS nome, c.tipo AS tipo,
                   SUM(t.valor_centavos) AS total
            FROM transacoes t
            JOIN categorias c ON c.id = t.categoria_id
            {where}
            GROUP BY c.id
            ORDER BY total DESC;
        """
        where, parametros = self._montar_where(inicio, fim)
        cursor = self._conexao.execute(sql.format(where=where), parametros)
        return [
            ResumoCategoria(
                categoria=linha["nome"],
                tipo=TipoMovimento(linha["tipo"]),
                total_centavos=linha["total"] or 0,
            )
            for linha in cursor.fetchall()
        ]

    @staticmethod
    def _montar_where(
        inicio: datetime | None, fim: datetime | None
    ) -> tuple[str, list[str]]:
        """Monta o trecho WHERE e seus parâmetros, reaproveitado nas somas."""
        filtros: list[str] = []
        parametros: list[str] = []
        if inicio is not None:
            filtros.append("t.data_hora >= ?")
            parametros.append(inicio.strftime(_FORMATO_DATA))
        if fim is not None:
            filtros.append("t.data_hora <= ?")
            parametros.append(fim.strftime(_FORMATO_DATA))
        where = ("WHERE " + " AND ".join(filtros)) if filtros else ""
        return where, parametros

    @staticmethod
    def _para_modelo(linha: sqlite3.Row) -> Transacao:
        return Transacao(
            id=linha["id"],
            descricao=linha["descricao"],
            valor_centavos=linha["valor_centavos"],
            categoria_id=linha["categoria_id"],
            data_hora=datetime.strptime(linha["data_hora"], _FORMATO_DATA),
        )