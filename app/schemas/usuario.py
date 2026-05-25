from pydantic import BaseModel, EmailStr
from typing import Optional

# Esse modelo define quais dados o cliente PRECISA enviar para se cadastrar
class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    role: Optional[str] = "CLIENTE"  # CLIENTE, ATENDENTE, ADMIN
    consentimento_lgpd: bool  # Obrigatório pro trabalho da UNINTER!

# Esse modelo define quais dados a API vai DEVOLVER para a tela (escondendo a senha por segurança!)
class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    consentimento_lgpd: bool

    # Isso aqui avisa o Pydantic para ler os dados mesmo que eles venham do banco de dados (SQLAlchemy)
    class Config:
        from_attributes = True  