from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Criamos um banco de dados SQLite local chamado 'lanchonete.db'
SQLALCHEMY_DATABASE_URL = "sqlite:///./lanchonete.db"

# O engine é quem cuida da conversa com o arquivo do banco de dados
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# A SessionLocal é o que usaremos para abrir sessões de leitura/escrita de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A classe Base será herdada por todos os nossos modelos (tabelas) do banco
Base = declarative_base()

# Função auxiliar para abrir e fechar a conexão com o banco de forma segura
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()