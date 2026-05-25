from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

# 1. Tabela de Usuários (Clientes, Atendentes, Admin)
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha = Column(String(255), nullable=False)
    role = Column(String(50), default="CLIENTE")  # CLIENTE, ATENDENTE, ADMIN
    consentimento_lgpd = Column(Boolean, default=False)

    # Relacionamento: Um usuário pode ter vários pedidos
    pedidos = relationship("Pedido", back_populates="usuario")


# 2. Tabela de Unidades (Lojas)
class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    cidade = Column(String(100), nullable=False)

    # Relacionamentos
    estoques = relationship("Estoque", back_populates="unidade")
    pedidos = relationship("Pedido", back_populates="unidade")


# 3. Tabela de Produtos (Cardápio Geral)
class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    preco = Column(Numeric(10, 2), nullable=False)  # Corrigido para Numeric!

    # Relacionamentos
    estoques = relationship("Estoque", back_populates="produto")
    itens_pedido = relationship("ItemPedido", back_populates="produto")


# 4. Tabela de Estoques (Cardápio por Unidade)
class Estoque(Base):
    __tablename__ = "estoques"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, default=0)

    # Ligações reversas
    unidade = relationship("Unidade", back_populates="estoques")
    produto = relationship("Produto", back_populates="estoques")


# 5. Tabela de Pedidos (Vendas)
class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    canal_pedido = Column(String(50), nullable=False)  # APP, TOTEM, BALCAO, WEB
    status = Column(String(50), default="PENDENTE")    # PENDENTE, PAGO, FINALIZADO
    total = Column(Numeric(10, 2), default=0.0)        # Corrigido para Numeric!
    data_pedido = Column(DateTime, default=datetime.utcnow)

    # Ligações reversas e sub-itens
    usuario = relationship("Usuario", back_populates="pedidos")
    unidade = relationship("Unidade", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")


# 6. Tabela de Itens do Pedido (Produtos Comprados)
class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)  # Corrigido para Numeric!

    # Ligações reversas
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_pedido")