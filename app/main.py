from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import engine, Base, get_db

# Modelos e Schemas
from app.models.usuario_model import Usuario, Produto, Unidade, Estoque, Pedido, ItemPedido
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.schemas.produto import ProdutoCreate, ProdutoResponse, EstoqueUpdate
from app.schemas.pedido import PedidoCreate

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lanchonete Raízes do Nordeste",
    description="API para gerenciamento de pedidos, estoque por unidade e fidelidade LGPD",
    version="1.0.0"
)

@app.get("/")
def pagina_inicial():
    return {"mensagem": "Bem-vindo à API da Lanchonete Raízes do Nordeste!", "status": "Servidor rodando perfeitamente"}

# ==================== USUÁRIOS ====================
@app.post("/usuarios/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado.")
    novo_usuario = Usuario(nome=usuario.nome, email=usuario.email, senha=usuario.senha, role=usuario.role, consentimento_lgpd=usuario.consentimento_lgpd)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

# ==================== CARDÁPIO E ESTOQUE ====================
@app.post("/produtos/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    novo_produto = Produto(nome=produto.nome, preco=produto.preco)
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto

@app.post("/unidades/", status_code=status.HTTP_201_CREATED)
def cadastrar_unidade(nome: str, cidade: str, db: Session = Depends(get_db)):
    nova_unidade = Unidade(nome=nome, cidade=cidade)
    db.add(nova_unidade)
    db.commit()
    db.refresh(nova_unidade)
    return nova_unidade

@app.post("/estoque/", status_code=status.HTTP_200_OK)
def atualizar_estoque(estoque_dados: EstoqueUpdate, db: Session = Depends(get_db)):
    prod = db.query(Produto).filter(Produto.id == estoque_dados.produto_id).first()
    unid = db.query(Unidade).filter(Unidade.id == estoque_dados.unidade_id).first()
    if not prod or not unid:
        raise HTTPException(status_code=404, detail="Produto ou Unidade não encontrados.")
    item_estoque = db.query(Estoque).filter(Estoque.unidade_id == estoque_dados.unidade_id, Estoque.produto_id == estoque_dados.produto_id).first()
    if item_estoque:
        item_estoque.quantidade = estoque_dados.quantidade
    else:
        item_estoque = Estoque(unidade_id=estoque_dados.unidade_id, produto_id=estoque_dados.produto_id, quantidade=estoque_dados.quantidade)
        db.add(item_estoque)
    db.commit()
    return {"mensagem": f"Estoque do produto '{prod.nome}' atualizado para {estoque_dados.quantidade}."}

@app.get("/unidades/{unidade_id}/estoque/")
def consultar_estoque_unidade(unidade_id: int, db: Session = Depends(get_db)):
    unidade = db.query(Unidade).filter(Unidade.id == unidade_id).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")
    resultados = db.query(Estoque).filter(Estoque.unidade_id == unidade_id).all()
    cardapio_disponivel = [{"produto_id": item.produto.id, "nome_produto": item.produto.nome, "preco": item.produto.preco, "quantidade_disponivel": item.quantidade} for item in resultados]
    return {"unidade": unidade.nome, "cidade": unidade.cidade, "cardapio": cardapio_disponivel}

# ==================== SIMULAÇÃO DE VENDAS (NOVO!) ====================
@app.post("/pedidos/", status_code=status.HTTP_201_CREATED)
def realizar_pedido(pedido_dados: PedidoCreate, db: Session = Depends(get_db)):
    # 1. Verifica se usuário e unidade existem
    user = db.query(Usuario).filter(Usuario.id == pedido_dados.usuario_id).first()
    unid = db.query(Unidade).filter(Unidade.id == pedido_dados.unidade_id).first()
    if not user or not unid:
        raise HTTPException(status_code=404, detail="Usuário ou Unidade não encontrados.")
    
    # 2. Cria a estrutura do Pedido principal
    novo_pedido = Pedido(usuario_id=pedido_dados.usuario_id, unidade_id=pedido_dados.unidade_id, canal_pedido=pedido_dados.canal_pedido.upper(), total=0.0)
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)
    
    valor_total = 0.0
    
    # 3. Processa cada item comprado
    for item in pedido_dados.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto ID {item.produto_id} não existe.")
        
        # Verifica se tem estoque na unidade
        estoque_item = db.query(Estoque).filter(Estoque.unidade_id == pedido_dados.unidade_id, Estoque.produto_id == item.produto_id).first()
        if not estoque_item or estoque_item.quantidade < item.quantidade:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para o produto '{produto.nome}'.")
        
        # Deduz a quantidade do estoque da unidade física!
        estoque_item.quantidade -= item.quantidade
        
        # Calcula subtotal do item
        subtotal_item = produto.preco * item.quantidade
        valor_total += float(subtotal_item)
        
        # Salva o item na tabela vinculada ao pedido
        novo_item = ItemPedido(pedido_id=novo_pedido.id, produto_id=produto.id, quantidade=item.quantidade, preco_unitario=produto.preco)
        db.add(novo_item)

    # 4. Atualiza o valor total final do pedido
    novo_pedido.total = valor_total
    db.commit()
    
    return {
        "mensagem": "Pedido realizado com sucesso!",
        "pedido_id": novo_pedido.id,
        "canal": novo_pedido.canal_pedido,
        "total_pago": valor_total,
        "status": novo_pedido.status
    }