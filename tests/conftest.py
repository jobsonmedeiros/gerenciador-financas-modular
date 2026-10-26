"""
conftest.py — Configuração compartilhada dos testes (fixtures).

PADRÃO DE PROJETO: "Fixture" do pytest.
Cada teste recebe um banco SQLite em MEMÓRIA (":memory:"), novo a cada
teste. Isso garante isolamento total: um teste nunca vê dados de outro.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Garante que `import financas` funcione rodando o pytest da raiz do projeto.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from financas.banco import conectar, criar_esquema  # noqa: E402
from financas.configuracao import Configuracao  # noqa: E402
from financas.repositorios import (  # noqa: E402
    CategoriaRepositorio,
    TransacaoRepositorio,
)
from financas.servicos import FinancasServico  # noqa: E402


@pytest.fixture
def conexao():
    """Uma conexão em memória com o esquema criado."""
    config = Configuracao(caminho_banco=":memory:")
    conexao = conectar(config)
    criar_esquema(conexao)
    yield conexao
    conexao.close()


@pytest.fixture
def servico(conexao) -> FinancasServico:
    """O serviço completo, ligado ao banco em memória."""
    return FinancasServico(
        CategoriaRepositorio(conexao), TransacaoRepositorio(conexao)
    )


@pytest.fixture
def servico_com_categorias(servico) -> FinancasServico:
    """O serviço já com as categorias padrão criadas."""
    servico.inicializar_dados_padrao()
    return servico
