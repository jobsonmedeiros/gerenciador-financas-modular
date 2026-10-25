"""
configuracao.py — Configurações centrais do sistema.

PADRÃO DE PROJETO: "Configuration Object".
Em vez de espalhar caminhos e constantes pelo código, tudo que muda
entre ambientes (banco de dados, moeda, fuso) fica aqui.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Configuracao:
    """Guarda as configurações da aplicação.

    `frozen=True` deixa o objeto imutável: ninguém altera a configuração
    no meio da execução por acidente.
    """

    # Caminho do arquivo SQLite. Pode ser trocado pela variável FINANCAS_DB.
    caminho_banco: str = os.getenv("FINANCAS_DB", "financas.db")

    # Moeda exibida nos relatórios.
    moeda: str = "R$"

    # Fuso horário usado para registrar a data das transações.
    fuso_horario: str = os.getenv("FINANCAS_TZ", "America/Sao_Paulo")


# Instância única usada pelo resto do sistema.
CONFIGURACAO_PADRAO = Configuracao()