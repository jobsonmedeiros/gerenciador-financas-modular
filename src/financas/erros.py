"""
erros.py — Erros de negócio do sistema.

PADRÃO DE PROJETO: "Custom Exceptions".
Em vez de o serviço imprimir mensagens de erro no terminal, ele lança
exceções próprias. Quem chama (a interface) decide como mostrar.
Isso mantém a regra de negócio independente da tela.
"""


class ErroDeNegocio(Exception):
    """Base para todos os erros previstos do domínio."""


class ValorInvalidoError(ErroDeNegocio):
    """Valor menor ou igual a zero, ou em formato errado."""


class CategoriaInvalidaError(ErroDeNegocio):
    """Categoria inexistente ou de tipo incompatível com a transação."""