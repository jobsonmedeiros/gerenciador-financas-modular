import sys
from datetime import datetime

sys.path.insert(0, "src")

from financas.banco import conectar, criar_esquema
from financas.configuracao import Configuracao
from financas.modelos import Transacao
from financas.repositorios.categoria_repositorio import CategoriaRepositorio
from financas.repositorios.transacao_repositorio import TransacaoRepositorio

conexao = conectar(Configuracao(":memory:"))
criar_esquema(conexao)

categorias = CategoriaRepositorio(conexao)
transacoes = TransacaoRepositorio(conexao)
categorias.garantir_categorias_padrao()

ids = {c.nome: c.id for c in categorias.listar()}
quando = datetime(2026, 10, 15, 12, 0)

transacoes.criar(Transacao(None, "Salário", 500000, ids["Salário"], quando))
transacoes.criar(Transacao(None, "Mercado", 80050, ids["Alimentação"], quando))
transacoes.criar(Transacao(None, "Ônibus", 19950, ids["Transporte"], quando))

print("Totais por tipo:", transacoes.somar_por_tipo())
print("Por categoria:")
for linha in transacoes.somar_por_categoria():
    print(f"  {linha.categoria:<12} {linha.tipo.value:<8} {linha.total_centavos}")
print("Listagem:", len(transacoes.listar()))