"""
interface.py — A camada de apresentação (terminal).

PADRÃO DE PROJETO: "Separated Interface / CLI Adapter".
Este arquivo só sabe ler teclado, imprimir texto e chamar o serviço.
Se amanhã a entrada for uma API REST, o serviço continua igual:
só esta camada é substituída.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from financas.configuracao import Configuracao
from financas.erros import ErroDeNegocio
from financas.formatadores import (
    formatar_data,
    formatar_reais,
    rotulo_tipo,
    sinal_tipo,
)
from financas.modelos import TipoMovimento
from financas.servicos import FinancasServico

LINHA = "-" * 56


class InterfaceTerminal:
    """Menu interativo do gerenciador de finanças."""

    def __init__(self, servico: FinancasServico, configuracao: Configuracao) -> None:
        self._servico = servico
        self._config = configuracao

    # ------------------------------------------------------------------
    # Ciclo principal
    # ------------------------------------------------------------------
    def executar(self) -> None:
        """Mostra o menu em laço até o usuário escolher sair."""
        criadas = self._servico.inicializar_dados_padrao()
        if criadas:
            print(f"[ok] {criadas} categorias padrão criadas.")

        acoes = {
            "1": self._menu_registrar,
            "2": self._menu_extrato,
            "3": self._menu_resumo,
            "4": self._menu_categorias,
        }

        while True:
            self._imprimir_menu()
            opcao = self._ler("Escolha uma opção: ")

            if opcao == "0":
                print("\nEncerrando. Até logo!")
                return

            acao = acoes.get(opcao)
            if acao is None:
                print("[!] Opção inválida. Digite 0 a 4.")
                continue

            try:
                acao()
            except ErroDeNegocio as erro:
                # Erros previstos viram mensagem amigável, sem derrubar o app.
                print(f"[!] {erro}")
            except (KeyboardInterrupt, EOFError):
                print("\nOperação cancelada.")
            except Exception as erro:  # noqa: BLE001 — proteção final da CLI
                print(f"[!] Erro inesperado: {erro}")

    # ------------------------------------------------------------------
    # Telas
    # ------------------------------------------------------------------
    def _imprimir_menu(self) -> None:
        print()
        print("=== GERENCIADOR DE FINANÇAS PESSOAIS ===")
        print("1. Registrar transação")
        print("2. Ver extrato do mês")
        print("3. Resumo por categoria")
        print("4. Listar categorias")
        print("0. Sair")

    def _menu_registrar(self) -> None:
        print("\n--- Nova transação ---")
        print("1. Receita")
        print("2. Despesa")
        escolha = self._ler("Tipo (1 ou 2): ")

        if escolha == "1":
            tipo = TipoMovimento.RECEITA
        elif escolha == "2":
            tipo = TipoMovimento.DESPESA
        else:
            print("[!] Tipo inválido.")
            return

        categorias = self._servico.listar_categorias(tipo)
        if not categorias:
            print(f"[!] Nenhuma categoria de {rotulo_tipo(tipo).lower()}.")
            return

        print(f"\nCategorias de {rotulo_tipo(tipo).lower()}:")
        for categoria in categorias:
            print(f"  [{categoria.id:>2}] {categoria.nome}")

        categoria_id = self._ler_int("Id da categoria: ")
        if categoria_id is None:
            return

        descricao = self._ler("Descrição (ex.: Supermercado): ")
        valor = self._ler("Valor (ex.: 150,90): ")

        transacao = self._servico.registrar_transacao(
            descricao=descricao,
            valor=valor,
            categoria_id=categoria_id,
        )
        print(
            f"\n[ok] Transação #{transacao.id} registrada: "
            f"{transacao.descricao} — "
            f"{formatar_reais(transacao.valor_centavos, self._config.moeda)}"
        )

    def _menu_extrato(self) -> None:
        inicio, fim = self._periodo_mes_atual()
        transacoes = self._servico.listar_transacoes(inicio, fim)

        print(f"\n--- Extrato de {inicio:%m/%Y} ---")
        if not transacoes:
            print("Nenhuma transação no período.")
            return

        # Mapa id -> categoria para exibir o nome sem consultar o banco
        # uma vez por linha (evita o problema conhecido como N+1 consultas).
        nomes = {c.id: c for c in self._servico.listar_categorias()}

        for transacao in transacoes:
            categoria = nomes.get(transacao.categoria_id)
            nome_categoria = categoria.nome if categoria else "?"
            tipo = categoria.tipo if categoria else TipoMovimento.DESPESA
            valor = formatar_reais(transacao.valor_centavos, self._config.moeda)
            print(
                f"#{transacao.id:<3} {formatar_data(transacao.data_hora)}  "
                f"{sinal_tipo(tipo)}{valor:<12} "
                f"({nome_categoria}) {transacao.descricao}"
            )

        resumo = self._servico.gerar_resumo(inicio, fim)
        print(LINHA)
        self._imprimir_totais(resumo)

    def _menu_resumo(self) -> None:
        inicio, fim = self._periodo_mes_atual()
        resumo = self._servico.gerar_resumo(inicio, fim)

        print(f"\n--- Resumo por categoria ({inicio:%m/%Y}) ---")
        if not resumo.por_categoria:
            print("Nenhuma transação no período.")
            return

        for linha in resumo.por_categoria:
            print(
                f"{linha.categoria:<15} {rotulo_tipo(linha.tipo):<8} "
                f"{formatar_reais(linha.total_centavos, self._config.moeda):>14}"
            )

        print(LINHA)
        print(
            "Saldo do mês: "
            f"{formatar_reais(resumo.saldo_centavos, self._config.moeda)}"
        )

    def _menu_categorias(self) -> None:
        print("\n--- Categorias ---")
        for categoria in self._servico.listar_categorias():
            print(
                f"  [{categoria.id:>2}] {categoria.nome:<15} "
                f"({rotulo_tipo(categoria.tipo)})"
            )

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------
    def _imprimir_totais(self, resumo) -> None:
        """Imprime receitas, despesas e saldo de forma alinhada."""
        moeda = self._config.moeda
        print(
            f"Receitas: {formatar_reais(resumo.total_receitas_centavos, moeda)}"
        )
        print(
            f"Despesas: {formatar_reais(resumo.total_despesas_centavos, moeda)}"
        )
        print(f"Saldo:    {formatar_reais(resumo.saldo_centavos, moeda)}")

    @staticmethod
    def _periodo_mes_atual() -> tuple[datetime, datetime]:
        """Devolve o primeiro e o último instante do mês corrente."""
        agora = datetime.now()
        inicio = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if inicio.month == 12:
            proximo = inicio.replace(year=inicio.year + 1, month=1)
        else:
            proximo = inicio.replace(month=inicio.month + 1)
        fim = proximo - timedelta(seconds=1)
        return inicio, fim

    @staticmethod
    def _ler(mensagem: str) -> str:
        return input(mensagem).strip()

    def _ler_int(self, mensagem: str) -> int | None:
        """Lê um inteiro; devolve None se o usuário digitar algo inválido."""
        texto = self._ler(mensagem)
        try:
            return int(texto)
        except ValueError:
            print("[!] Digite um número inteiro.")
            return None
