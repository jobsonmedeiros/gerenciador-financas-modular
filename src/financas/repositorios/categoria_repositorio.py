"""
categoria_repositorio.py — Acesso à tabela `categorias`.

PADRÃO DE PROJETO: "Repository Pattern".
O repositório é o ÚNICO lugar do sistema que escreve SQL. O resto do
código pede objetos (Categoria) e não sabe que existe SQLite por baixo.
"""

from __future__ import annotations

import sqlite3

from financas.modelos import Categoria, TipoMovimento


class CategoriaRepositorio:
    """Traduz linhas da tabela `categorias` em objetos Categoria."""

    def __init__(self, conexao: sqlite3.Connection) -> None:
        # A conexão é injetada de fora (Dependency Injection).
        # O repositório não abre conexão sozinho: isso facilita os testes.
        self._conexao = conexao

    def criar(self, nome: str, tipo: TipoMovimento) -> Categoria:
        """Insere uma categoria e devolve o objeto já com o id do banco."""
        with self._conexao as conexao:
            cursor = conexao.execute(
                "INSERT INTO categorias (nome, tipo) VALUES (?, ?);",
                (nome.strip(), tipo.value),
            )
        return Categoria(id=cursor.lastrowid, nome=nome.strip(), tipo=tipo)

    def listar(self, tipo: TipoMovimento | None = None) -> list[Categoria]:
        """Lista todas as categorias ou só as de um tipo (receita/despesa)."""
        if tipo is None:
            cursor = self._conexao.execute(
                "SELECT id, nome, tipo FROM categorias ORDER BY tipo, nome;"
            )
        else:
            cursor = self._conexao.execute(
                "SELECT id, nome, tipo FROM categorias"
                " WHERE tipo = ? ORDER BY nome;",
                (tipo.value,),
            )
        return [self._para_modelo(linha) for linha in cursor.fetchall()]

    def buscar_por_id(self, categoria_id: int) -> Categoria | None:
        """Devolve a categoria com esse id, ou None se não existir."""
        cursor = self._conexao.execute(
            "SELECT id, nome, tipo FROM categorias WHERE id = ?;",
            (categoria_id,),
        )
        linha = cursor.fetchone()
        return self._para_modelo(linha) if linha else None

    def garantir_categorias_padrao(self) -> int:
        """Cria as categorias iniciais que ainda não existirem.

        `INSERT OR IGNORE` usa a restrição UNIQUE do nome: se a categoria
        já existe, o banco ignora sem lançar erro. É idempotente.
        Retorna quantas foram realmente criadas.
        """
        padrao = [
            ("Salário", TipoMovimento.RECEITA),
            ("Freelance", TipoMovimento.RECEITA),
            ("Investimentos", TipoMovimento.RECEITA),
            ("Alimentação", TipoMovimento.DESPESA),
            ("Transporte", TipoMovimento.DESPESA),
            ("Moradia", TipoMovimento.DESPESA),
            ("Saúde", TipoMovimento.DESPESA),
            ("Educação", TipoMovimento.DESPESA),
            ("Lazer", TipoMovimento.DESPESA),
        ]
        criadas = 0
        with self._conexao as conexao:
            for nome, tipo in padrao:
                cursor = conexao.execute(
                    "INSERT OR IGNORE INTO categorias (nome, tipo) VALUES (?, ?);",
                    (nome, tipo.value),
                )
                criadas += cursor.rowcount  # 1 se inseriu, 0 se ignorou
        return criadas

    @staticmethod
    def _para_modelo(linha: sqlite3.Row) -> Categoria:
        """Converte uma linha do banco no objeto Categoria (mapper)."""
        return Categoria(
            id=linha["id"],
            nome=linha["nome"],
            tipo=TipoMovimento(linha["tipo"]),
        )