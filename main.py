"""
main.py — Ponto de entrada da aplicação (Composition Root).

PADRÃO DE PROJETO: "Composition Root".
É o único lugar que monta as peças: configuração -> conexão -> repositórios
-> serviço -> interface. Nenhuma regra de negócio neste arquivo.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permite rodar com `python main.py` sem instalar o pacote:
# adiciona a pasta `src/` ao caminho de importação.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from financas.banco import conectar, criar_esquema  # noqa: E402
from financas.configuracao import CONFIGURACAO_PADRAO, Configuracao  # noqa: E402
from financas.interface import InterfaceTerminal  # noqa: E402
from financas.repositorios import (  # noqa: E402
    CategoriaRepositorio,
    TransacaoRepositorio,
)
from financas.servicos import FinancasServico  # noqa: E402


def criar_aplicacao(
    configuracao: Configuracao = CONFIGURACAO_PADRAO,
) -> InterfaceTerminal:
    """Monta todas as camadas e devolve a interface pronta para uso.

    Esta função também é usada pelos testes: chamando com uma configuração
    apontando para um banco em memória, o sistema inteiro roda isolado.
    """
    conexao = conectar(configuracao)          # 1. banco
    criar_esquema(conexao)                    # 2. tabelas

    categorias = CategoriaRepositorio(conexao)      # 3. repositórios
    transacoes = TransacaoRepositorio(conexao)

    servico = FinancasServico(categorias, transacoes)  # 4. regras de negócio

    return InterfaceTerminal(servico, configuracao)    # 5. apresentação


if __name__ == "__main__":
    criar_aplicacao().executar()
