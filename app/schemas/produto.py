from pydantic import BaseModel
from decimal import Decimal

# Molde para quando formos cadastrar um novo produto no cardápio
class ProdutoCreate(BaseModel):
    nome: str
    preco: Decimal

# Molde de como a API vai responder os dados do produto
class ProdutoResponse(BaseModel):
    id: int
    nome: str
    preco: Decimal

    class Config:
        from_attributes = True

# Molde para atualizar ou definir a quantidade de um produto no estoque de uma unidade
class EstoqueUpdate(BaseModel):
    unidade_id: int
    produto_id: int
    quantidade: int