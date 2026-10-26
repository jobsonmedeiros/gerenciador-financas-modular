"""
financas_servico.py — Onde ficam as REGRAS DE NEGÓCIO.

PADRÃO DE PROJETO: "Service Layer".
É a camada do "como funciona": valida valores, confere se a categoria
existe, converte reais em centavos, calcula o resumo do período.
Não conhece terminal, não conhece SQL — só chama os repositórios.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation

from financas.erros import CategoriaInvalidaError, ValorInvalidoError
from financas.modelos import ResumoFinanceiro, TipoMovimento, Transacao
from financas.repositorios import CategoriaRepositorio, TransacaoRepositorio


class FinancasServico:
    """Orquestra as operações do sistema de finanças pessoais."""

    def __init__(
        self,
        categoria_repositorio: CategoriaRepositorio,
        transacao_repositorio: TransacaoRepositorio,
    ) -> None:
        # As dependências entram pelo construtor (Dependency Injection).
        self._categorias = categoria_repositorio
        self._transacoes = transacao_repositorio

    # ------------------------------------------------------------------
    # Categorias
    # ------------------------------------------------------------------
    def inicializar_dados_padrao(self) -> int:
        """Garante as categorias iniciais. Retorna quantas foram criadas."""
        return self._categorias.garantir_categorias_padrao()

    def listar_categorias(self, tipo: TipoMovimento | None = None):
        """Repassa a listagem de categorias, opcionalmente por tipo."""
        return self._categorias.listar(tipo)

    # ------------------------------------------------------------------
    # Transações
    # ------------------------------------------------------------------
    def registrar_transacao(
        self,
        descricao: str,
        valor: str,
        categoria_id: int,
        quando: datetime | None = None,
    ) -> Transacao:
        """Valida os dados e grava uma nova transação.

        `valor` chega como TEXTO (é o que o usuário digitou), porque
        converter para número é responsabilidade do serviço, não da tela.
        """
        descricao = descricao.strip()
        if not descricao:
            raise ValorInvalidoError("A descrição não pode ficar vazia.")

        valor_centavos = self._converter_para_centavos(valor)

        categoria = self._categorias.buscar_por_id(categoria_id)
        if categoria is None:
            raise CategoriaInvalidaError(
                f"Não existe categoria com o id {categoria_id}."
            )

        transacao = Transacao(
            id=None,
            descricao=descricao,
            valor_centavos=valor_centavos,
            categoria_id=categoria.id,
            data_hora=quando or datetime.now(),
        )
        return self._transacoes.criar(transacao)

    def listar_transacoes(
        self, inicio: datetime | None = None, fim: datetime | None = None
    ) -> list[Transacao]:
        """Lista transações do período informado."""
        return self._transacoes.listar(inicio, fim)

    def gerar_resumo(
        self, inicio: datetime | None = None, fim: datetime | None = None
    ) -> ResumoFinanceiro:
        """Monta o relatório consolidado: totais por tipo e por categoria."""
        totais = self._transacoes.somar_por_tipo(inicio, fim)
        por_categoria = self._transacoes.somar_por_categoria(inicio, fim)

        return ResumoFinanceiro(
            total_receitas_centavos=totais[TipoMovimento.RECEITA],
            total_despesas_centavos=totais[TipoMovimento.DESPESA],
            por_categoria=tuple(por_categoria),
        )

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------
    @staticmethod
    def _converter_para_centavos(valor: str) -> int:
        """Converte "1.234,56" ou "1234.56" em 123456 centavos.

        - usa Decimal (e não float) para não perder precisão;
        - aceita vírgula como separador decimal (padrão brasileiro);
        - rejeita zero e valores negativos.
        """
        texto = valor.strip().replace("R$", "").replace(" ", "")
        if not texto:
            raise ValorInvalidoError("Informe um valor.")

        # Se tem vírgula, ela é o separador decimal: remove pontos de milhar.
        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")

        try:
            decimal = Decimal(texto)
        except InvalidOperation as erro:
            raise ValorInvalidoError(
                f"Valor inválido: {valor!r}. Use algo como 150,90."
            ) from erro

        if decimal <= 0:
            raise ValorInvalidoError("O valor precisa ser maior que zero.")

        return int((decimal * 100).to_integral_value())