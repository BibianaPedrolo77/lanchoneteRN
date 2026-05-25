from pydantic import BaseModel
from typing import List

# Molde para os itens que vão dentro do pedido
class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int

# Molde para quando o cliente for fechar a venda
class PedidoCreate(BaseModel):
    usuario_id: int
    unidade_id: int
    canal_pedido: str  # APP, TOTEM, BALCAO, WEB
    itens: List[ItemPedidoCreate]